"""Configuration and lifecycle for propagator-side optimization."""

import sys
from collections.abc import Callable

import clingo

import constraint_handler.schemas.propagator_atom as prop_atom
from constraint_handler import myClorm
from constraint_handler.PropagatorConstants import (
    OPTIMIZATION_HELPER_PROGRAM,
    OPTIMIZATION_STAGE_ATOM,
    OptimizationStrength,
    propagator_warning_t,
)
from constraint_handler.PropagatorVariables import OptimizationHandler, VariableValue
from constraint_handler.schemas import expression, warning


class OptimizationModeHandler:
    """
    Own optimization state, objective sums, and pruning decisions.

    Attributes:
        sums: OptimizationHandler holding the optimization sums and related state
        best_value: Holds the best objective value found so far
        strength: OptimizationStrength indicating the current pruning strength
        stage_literals: dict[int, int] mapping optimization stages to their corresponding literals
        optimal_models_wanted: int specifying the number of optimal models requested
        optimal_models_found: int counting the number of optimal models found so far

    """

    optimality_atom = clingo.Function(OPTIMIZATION_STAGE_ATOM, [clingo.Number(2)])

    def __init__(self) -> None:
        self.sums = OptimizationHandler()
        self.best_value: list[int | float] = [-sys.maxsize]
        self.strength = OptimizationStrength.STRICT
        self.stage_literals: dict[int, int] = {1: -1, 2: -1}
        self.optimal_models_wanted = 0
        self.optimal_models_found = 0

    @property
    def enabled(self) -> bool:
        """
        Check if optimization is enabled based on the presence of optimization sums.

        Returns:
            bool: True if there are optimization sums, False otherwise.
        """
        return self.sums.get_sum_count() > 0

    def configure(self, ctl: clingo.Control) -> warning.Warning | None:
        """
        Add optimization support and configure the requested optimal-model count.

        Args:
            ctl: Clingo control object.

        Returns:
            warning.Warning | None: A warning if the configuration is not compatible, None otherwise.
        """
        ctl.add("base", [], OPTIMIZATION_HELPER_PROGRAM)
        self.optimal_models_wanted = 1

        if ctl.configuration.solve.opt_mode == "optN":  # ty:ignore[unresolved-attribute]
            self.optimal_models_wanted = int(
                ctl.configuration.solve.models
            )  # ty:ignore[invalid-argument-type,unresolved-attribute]
            ctl.configuration.solve.models = 0  # ty:ignore[invalid-assignment]
            if ctl.configuration.solver.heuristic != "Domain":  # ty:ignore[unresolved-attribute]
                return warning.Warning(
                    warning.Propagator(),
                    (),
                    f"Optimization requires --heuristic=Domain, but {ctl.configuration.solver.heuristic} was set. This may lead to incorrect results.",  # ty:ignore[unresolved-attribute]
                )
        return None

    def reset(self) -> None:
        """
        Reset per-solve optimization state, preserving configuration.

        This includes resetting the optimization sums, best value, pruning strength,
        stage literals, and the count of optimal models found.
        """
        self.sums = OptimizationHandler()
        self.best_value = []
        self.strength = OptimizationStrength.STRICT
        self.stage_literals = {1: -1, 2: -1}
        self.optimal_models_found = 0

    def add_value(self, variable: clingo.Symbol, value: VariableValue, priority: int) -> None:
        """
        Add a value to the optimization sums with the specified priority.

        Args:
            variable: The Clingo symbol representing the variable.
            value: The value associated with the variable.
            priority: The priority of the value in the optimization sums.
        """
        self.sums.add_value(variable, value, priority)

    def get_errors(self) -> propagator_warning_t:
        """
        Get the current optimization errors.

        Returns:
            propagator_warning_t: The current optimization errors.
        """
        return self.sums.get_errors()

    def initialize_best_value(self) -> None:
        """
        Initialize the best value for the optimization sums.

        This sets the best value to the lowest possible values based on the number of optimization sums.
        """
        self.best_value = [-sys.maxsize] * self.sums.get_sum_count()

    def get_optimization_sums(
        self,
        ctl: clingo.PropagateInit,
        get_variable_value: Callable[[expression.Expr, int], VariableValue],
        add_watch: Callable[[int], None],
    ) -> None:
        """
        Load optimization sum declarations from ASP facts.

        Args:
            ctl: Clingo propagation initializer.
            get_variable_value: Callback to intern an expression value.
            add_watch: Callback to register literals for watching.
        """
        max_sums = myClorm.findInPropagateInit(ctl, prop_atom.Propagator_optimize_maximizeSum)

        for (expr, symbol, priority, _), literal in max_sums.items():
            value = get_variable_value(expr, literal)
            add_watch(literal)
            add_watch(-literal)
            self.add_value(symbol, value, priority)

        self.initialize_best_value()

    def reset_sums(self, decision_level: int) -> None:
        """
        Reset the optimization sums for the given decision level.

        Args:
            decision_level: The current decision level in the solver.
        """
        self.sums.reset(decision_level)

    def activate_equal_stage(self, assignment: clingo.Assignment, changed_literal: int | None = None) -> bool:
        """
        Switch to lenient pruning when optimization stage two becomes active.
        "equal" stage refers to the fact that we do not prune new solution that have the best known value.

        Args:
            assignment: The current Clingo assignment.
            changed_literal: The literal that changed in the current propagation step, if any.

        Returns:
            bool: True if the pruning strength was switched to lenient, False otherwise.
        """
        if (
            not self.enabled
            or changed_literal is not None
            and changed_literal != self.stage_literals[2]
            or not assignment.is_true(self.stage_literals[2])
        ):
            return False

        self.strength = OptimizationStrength.LENIENT
        # if we are now in the second stage of optimization,
        # we can now look for equal valued solutions
        print("Now in optimization stage 2, looking for equal or better solutions")
        # continue  # this lit should not be present in any variable or expr
        return True

    def add_helper_atoms(
        self,
        init: clingo.PropagateInit,
        add_watch: Callable[[int], None],
    ) -> None:
        """
        Register stage literals used by optimization pruning.

        Args:
            init: The Clingo propagate initialization object.
            add_watch: A callable to register literals for watching.
        """
        if not self.enabled:
            return

        for atom in init.symbolic_atoms.by_signature(OPTIMIZATION_STAGE_ATOM, 1):
            literal = init.solver_literal(atom.literal)
            stage = atom.symbol.arguments[0].number

            assert stage in (1, 2), f"Unknown optimization stage atom: {atom.symbol}"
            self.stage_literals[stage] = literal
            if stage == 2:
                add_watch(literal)

    def evaluate_optimization_sums(self, ctl: clingo.PropagateControl) -> list[int] | None:
        """
        Evaluate objective bounds and return extra literals for a pruning nogood.

        Args:
            ctl: The Clingo propagate control object.

        Returns:
            list[int] | None: A list of literals for the pruning nogood, or None if no pruning is needed.
        """
        if not self.enabled:
            return None

        self.sums.evaluate(ctl)
        for index, objective in enumerate(self.sums.get_value()):
            if objective > self.best_value[index] or self.sums.has_unassigned(index):
                # if the value is better already,
                # rest of the priorities do not matter

                # if the value is not yet better but has unassigned variables, we cannot be sure yet
                # so we also break (since the behaviour for the rest of the priorities depends if this one is better, the same, or worse)
                break
            if objective == self.best_value[index]:
                # value is the same and has been fully assigned, check next priority
                # if this is the last value, all priorities were the same.
                if index == len(self.best_value) - 1 and self.strength == OptimizationStrength.STRICT:
                    # last priority and strict mode, add nogood to exclude this solution
                    # here, we dont know if this solution is also optimal or not, so we include the optimization stage literal
                    return [self.stage_literals[1]]
                continue
            if objective < self.best_value[index]:
                # if the value is worse and fully assigned, we can already add a nogood to exclude this solution
                # we dont add the stage literal since it is worse than the current best,
                # so it does not matter if we are looking for better or equal solutions to the optimal
                return []
        return None

    def update_best_value(self) -> tuple[list[int | float], list[int | float]] | None:
        """
        Update the incumbent if the current objective vector is better.

        Returns:
            tuple[list[int | float], list[int | float]] | None: A tuple containing the previous and new best values if updated, or None if no update occurred.
        """
        value = self.sums.get_value()
        if self.enabled and value > self.best_value:
            previous = self.best_value
            self.best_value = value
            return previous, value
        return None

    def record_model(self, model: clingo.Model) -> bool:
        """
        Count optimal models and report when the requested count is reached.

        Args:
            model: The Clingo model to be recorded.

        Returns:
            bool: True if the requested number of optimal models has been reached, False otherwise.
        """
        if not self.enabled:
            return False

        if OptimizationModeHandler.optimality_atom in model.symbols(atoms=True):
            self.optimal_models_found += 1
        return self.optimal_models_wanted > 0 and self.optimal_models_found >= self.optimal_models_wanted
