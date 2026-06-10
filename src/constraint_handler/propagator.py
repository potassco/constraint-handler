from __future__ import annotations

import operator
import sys
from typing import Any, Iterable, Literal, Sequence, cast

import clingo
from clingo import Symbol

import constraint_handler.evaluator as evaluator
import constraint_handler.multimap as multimap
import constraint_handler.myClorm as myClorm
import constraint_handler.post_processor as post_processor
import constraint_handler.schemas.expression as expression
import constraint_handler.schemas.propagator_atom as atom
import constraint_handler.schemas.type_ as type_
import constraint_handler.schemas.warning as warning
from constraint_handler.PropagatorConstants import (
    EXECUTION_OUTPUT,
    OPTIMIZATION_HELPER_PROGRAM,
    OPTIMIZATION_STAGE_ATOM,
    OTHER_ENGINE_VAR_NAME,
    REASONING_MODE_PROGRAM,
    REASONING_STAGE_ATOM,
    EvaluationResult,
    OptimizationStrength,
    ReasoningMode,
    ValueStatus,
    propagator_warning_t,
)
from constraint_handler.PropagatorVariables import (
    BoolEvaluateVariable,
    DictVariable,
    EnsureVariable,
    EvaluateVariable,
    Evaluations,
    Execution,
    OptimizationHandler,
    SetVariable,
    Variable,
    VariableManager,
    VariableType,
)


class ConstraintHandlerPropagator(clingo.Propagator):
    """
    Propagator that evaluates constraint_handler variables during solving.

    The propagator maintains a mapping from clingo symbols and solver literals to
    variable objects (see `constraint_handler.PropagatorVariables`). During
    propagation/check it evaluates affected variables, checks ensure constraints,
    and can add nogoods for conflicts or for pruning based on optimization or reasoning mode(brave/cautious).

    Attributes:
        symbol2var: Maps variable symbols to variable objects.
        literal2var: Maps solver literals to variable objects.
        evaluatevars: List of `EvaluateVariable` instances to evaluate.
        optimization_sum: Optimization handler tracking objective sums.
        best_value: Current best objective optimization vector.
        using_optimization: Whether optimization is active.
        optimization_strength: Whether equal quality solutions are allowed when optimizing.
        environment: Evaluation environment built from solver identifier.
        check_only: If True, `propagate` becomes a no-op. Will only evaluate variables in `check`.
        errors: Warnings collected while evaluating variables or reading the input program.
        reasoning_mode: STANDARD/BRAVE/CAUTIOUS mode.
        python_model: Stores the python-level model for output.
    """

    def __init__(self, check_only: bool = False):
        """
        Initialize the propagator.

        Args:
            check_only: If True, do not perform propagation (only allow checks).
        """
        self.symbol2var: VariableManager = VariableManager()
        self.literal2var: dict[int, list[VariableType]] = {}
        self.evaluations: Evaluations = Evaluations()

        self.evaluatevars: list[EvaluateVariable] = []

        self.optimization_sum: OptimizationHandler = OptimizationHandler()
        self.best_value: list[int | float] = [-sys.maxsize]
        self.using_optimization: bool = False
        self.optimization_strength: OptimizationStrength = OptimizationStrength.STRICT
        self.prop_sum_atoms: list[Symbol] = []  # used in the postprocessings

        self.environment: dict[Any, Any] = {}

        self.check_only = check_only

        self.errors: propagator_warning_t = []

        self.reasoning_mode: ReasoningMode = ReasoningMode.STANDARD
        self.reasoning_mode_stage_lits: dict[Literal[1, 2, 3], int] = {1: -1, 2: -1, 3: -1}
        self.reasoning_stage: Literal[0, 1, 2] = 0
        # this is used for cautious reasoning
        # for the first model, the set is assigned the first model
        # This is will hold the model which is then used to update the result
        self.python_model: set[atom.ResultAtom] | None = None
        # variable lits is used for brave/cautious reasoning to create nogoods that force changes in the model between stages
        # There is one literal per variable. When it is true, it means that the variable has a different value than previous solutions
        # TODO: Check that the above explanation is true!
        self.variable_lits: dict[VariableType, int] = {}
        self.previously_stage_2: bool = False

        self.optimization_stage_lits: dict[Literal[1, 2], int] = {1: -1, 2: -1}
        self.optimal_models_wanted: int = 0
        self.optimal_models_found: int = 0
        self.nogood_queue: list[Iterable[int]] = []

        self.forbidden_warnings: dict[warning.Kind, int] = {}
        self.ignored_warnings: dict[warning.Kind, [int, bool]] = {}

    def get_configuration(self, ctl: clingo.Control):
        """
        Read clingo configuration and initialize reasoning-mode settings.

        For brave/cautious modes, this configures the solver heuristic and adds a
        helper program to facilitate the reasoning stages.

        Args:
            ctl: Clingo control instance.
        """
        match ctl.configuration.solve.enum_mode:  # ty:ignore[unresolved-attribute]
            case "brave":
                self.reasoning_mode = ReasoningMode.BRAVE
            case "cautious":
                self.reasoning_mode = ReasoningMode.CAUTIOUS
            case _:
                self.reasoning_mode = ReasoningMode.STANDARD

        if self.reasoning_mode != ReasoningMode.STANDARD:
            ctl.configuration.solver.heuristic = "Domain"  # ty:ignore[invalid-assignment]
            ctl.add("base", [], REASONING_MODE_PROGRAM)

        # TODO: we shoudln't be changing the ctl.configuration
        if ctl.configuration.solve.opt_mode == "optN":
            self.optimal_models_wanted: int = int(ctl.configuration.solve.models)  # ty:ignore[unresolved-attribute]
            ctl.configuration.solve.models = 0  # ty:ignore[invalid-assignment]
            ctl.configuration.solver.heuristic = "Domain"  # ty:ignore[invalid-assignment]
            ctl.add("base", [], OPTIMIZATION_HELPER_PROGRAM)

    def init(self, init: clingo.PropagateInit) -> None:
        """
        Function implementing the init method of a Propagator.
        See clingo Propagator documentation for more details.

        Args:
            init: Clingo PropagateInit object
        """
        self.symbol2var = VariableManager()
        self.literal2var.clear()
        self.evaluatevars.clear()
        self.optimization_sum = OptimizationHandler()
        self.environment = {}
        self.errors.clear()

        if self.check_only:
            init.check_mode = clingo.PropagatorCheckMode.Total

        self.get_solver_identifier(init)

        self.get_variables(init)
        self.get_ensure(init)
        self.get_set_declarations(init)
        self.get_multimap_declarations(init)
        self.get_optimization_sums(init)
        self.get_execution_declarations(init)
        self.get_engine_variables(init)
        self.get_evaluate(init)

        self.set_parents()

        self.add_reasoning_mode_helper_atoms(init)
        self.add_optimization_helper_atoms(init)

        self.get_forbidden_warnings(init)

        self.evaluations.init(list(self.symbol2var.get_variables()))

    def add_reasoning_mode_helper_atoms(self, ctl: clingo.PropagateInit) -> None:
        """
        Register helper literals for brave/cautious reasoning.

        In brave/cautious mode, the encoding provides stage atoms that separate
        (1) clingo reasoning for solver-handled variables and (2) propagator-side
        evaluation.

        Args:
            ctl: Clingo PropagateInit object.
        """
        if self.reasoning_mode in (ReasoningMode.BRAVE, ReasoningMode.CAUTIOUS):
            # Adding reasoning mode helper atoms
            for a in ctl.symbolic_atoms.by_signature(REASONING_STAGE_ATOM, 1):
                assert a.symbol.arguments[0].number in (1, 2, 3), f"Unknown reasoning stage atom: {a.symbol}"
                self.reasoning_mode_stage_lits[a.symbol.arguments[0].number] = ctl.solver_literal(
                    a.literal
                )  # ty:ignore[invalid-assignment]

            # TODO: check if it works with the new variable manager stuff
            for var in self.symbol2var.get_variables():
                if isinstance(var, EnsureVariable):
                    continue
                lit = ctl.add_literal(freeze=True)
                self.variable_lits[var] = lit

    def add_optimization_helper_atoms(self, ctl: clingo.PropagateInit) -> None:
        """
        Register helper literals for optimization pruning.

        If optimization is used, the encoding provides an atom that is true when
        we are still finding the optimal value and adds nogoods to prune worse solution than the current one.
        Then, we disable this atom and look for solutions with the SAME value so we find all optimal solutions
        Args:
            ctl: Clingo PropagateInit object.
        """

        if self.using_optimization:
            # Adding optimization helper atoms
            for a in ctl.symbolic_atoms.by_signature(OPTIMIZATION_STAGE_ATOM, 1):
                lit = ctl.solver_literal(a.literal)
                stage = a.symbol.arguments[0].number

                assert stage in (1, 2), f"Unknown optimization stage atom: {a.symbol}"
                self.optimization_stage_lits[stage] = lit  # ty:ignore[invalid-assignment]

                if stage == 2:
                    ctl.add_watch(lit)

    def set_optimization_check_strength(self, strength: Literal["lt", "le"]) -> None:
        """
        Configure whether optimization pruning requires strict improvement.

        Args:
            strength: Comparison mode.
                - `"lt"`: only strictly better solutions are accepted.
                - `"le"`: better or equal solutions are accepted.

        Raises:
            ValueError: If `strength` is not one of `"lt"` or `"le"`.
        """

        assert strength in ("lt", "le"), f"Unknown optimization check strength: {strength}"

        if strength == "lt":
            self.optimization_check_func = operator.lt
            self.optimization_strength = OptimizationStrength.STRICT
        elif strength == "le":
            self.optimization_check_func = operator.le
            self.optimization_strength = OptimizationStrength.LENIENT
        else:
            raise ValueError(f"Unknown optimization check strength: {strength}")

    def set_optimization_best_value(self, value: list[int | float]) -> None:
        """
        Set the best (incumbent) optimization value used for pruning.

        Args:
            value: Objective vector ordered by priority.
        """
        self.best_value = value

    def check(self, control: clingo.PropagateControl) -> None:
        """
        Perform a full consistency check using the current solver assignment.

        This evaluates all variables, checks ensure constraints and forbidden
        warnings, and applies optimization pruning by adding nogoods when
        necessary.

        Args:
            control: Clingo PropagateControl object.
        """
        if self.add_nogoods_from_queue(control):
            # backtracking due to nogoods in queue
            return

        backtrack = self.evaluated_solver_assignment(control, set(self.symbol2var.get_variables()))

        if backtrack:
            # backtracking due to conflicts in evaluation of variables
            return

        # If not backtracking, check optimization sums
        backtrack = self.evaluate_optimization_sum(control)
        if backtrack:
            # backtracking due to optimization sum being worse than best value
            return

        if control.assignment.is_total:
            self.check_total(control)

    def check_total(self, control: clingo.PropagateControl) -> None:
        """
        Handle a total assignment.

        This evaluates `evaluate` atoms, updates the python-side model for
        brave/cautious reasoning, and updates the incumbent objective value.

        Args:
            control: Clingo PropagateControl object.
        """
        self.check_evaluate(control)
        backtrack = self.evaluate_model(control)
        if backtrack:
            # backtracking due to brave/cautious model being updated
            return

        # if everything is good, we update the best value
        # TODO: Maybe we have to move this next stuff to the on_model function
        # in case there are multiple propagators?
        if self.using_optimization and self.optimization_sum.get_value() > self.best_value:
            print(f"New best optimization value found: {self.optimization_sum.get_value()} (old: {self.best_value})")
            self.best_value = self.optimization_sum.get_value()

        self.handle_warning_ignore(control)

    def handle_warning_ignore(self, ctl: clingo.PropagateControl) -> None:
        for __warning, (literal, observed) in self.ignored_warnings.items():
            if ctl.assignment.is_true(literal):
                self.ignored_warnings[__warning] = (literal, True)
            else:
                self.ignored_warnings[__warning] = (literal, False)

    def evaluate_model(self, ctl: clingo.PropagateControl) -> bool:
        """
        Update and (if needed) refine the accumulated python model.

        In STANDARD mode this only rebuilds the python model and never
        backtracks. In BRAVE/CAUTIOUS mode, the model is accumulated across
        models and nogoods may be enqueued to force progress between stages.

        Args:
            ctl: Clingo propagation control.

        Returns:
            bool: True if nogoods were added and propagation should stop.
        """
        old_model = self.python_model
        self.update_python_model()

        if self.reasoning_mode == ReasoningMode.STANDARD:
            return False

        # This part onwards is only for brave/cautious reasoning
        assert type(self.python_model) is set
        if old_model is not None:
            if self.reasoning_mode == ReasoningMode.CAUTIOUS:
                self.python_model = old_model.intersection(self.python_model)
            if self.reasoning_mode == ReasoningMode.BRAVE:
                self.python_model = old_model.union(self.python_model)

        if not ctl.assignment.is_true(self.reasoning_mode_stage_lits[2]):
            return False

        assert ctl.assignment.is_true(self.reasoning_mode_stage_lits[2]), "stage 2 should be true!"

        if not self.previously_stage_2:
            # First time in stage 2
            self.previously_stage_2 = True

            # add nogoods for the stuff in the current model
            self.nogood_queue.extend(self.get_reasoning_mode_nogoods(self.python_model, first_call=True))

            # add nogoods to ensure at least 1 var changes
            self.nogood_queue.append(
                [-lit for lit in self.variable_lits.values()] + [self.reasoning_mode_stage_lits[2]]
            )

            return self.add_nogoods_from_queue(ctl)

        elif self.previously_stage_2:
            # Subsequent times in stage 2
            assert old_model is not None

            # add nogoods for the new stuff
            if self.reasoning_mode == ReasoningMode.BRAVE:
                variables_considered = self.python_model.difference(old_model)
            elif self.reasoning_mode == ReasoningMode.CAUTIOUS:
                variables_considered = old_model.difference(self.python_model)

            self.nogood_queue.extend(self.get_reasoning_mode_nogoods(variables_considered, first_call=False))

            return self.add_nogoods_from_queue(ctl)

        assert ctl.assignment.is_true(self.reasoning_mode_stage_lits[3]), "stage 3 should be true!"

        return False

    def get_reasoning_mode_nogoods(self, variables: set[atom.ResultAtom], first_call: bool) -> list[Iterable[int]]:
        """
        Create nogoods used to drive brave/cautious reasoning.

        - BRAVE: force the next model to differ in at least one variable so the
            accumulated model can grow.
        - CAUTIOUS: on first call behaves like brave; on subsequent calls, block
            exactly the changes observed to converge to the intersection.

        Args:
                variables: Result atoms relevant for the current step.
                first_call: Whether this is the first stage-2 call for the run.

        Returns:
                list[Iterable[int]]: Nogoods to add (each is a collection of solver literals).
        """
        assert self.reasoning_mode in (ReasoningMode.BRAVE, ReasoningMode.CAUTIOUS)

        nogoods: list[Iterable[int]] = []
        for result_var in variables:
            # TODO: add support for evaluate and warnings
            if isinstance(result_var, (atom.Evaluated, warning.Warning)):
                continue
            assert type(result_var) in (
                atom.Value,
                atom.Set_value,
                atom.Multimap_value,
            ), f"Unexpected variable type: {type(result_var)} with value {result_var}"
            assert isinstance(result_var.name, clingo.Symbol)

            if self.reasoning_mode == ReasoningMode.BRAVE or first_call:
                # The first time we add nogoods, it is the same for brave and cautious
                for var in self.symbol2var[result_var.name].values():
                    ng = self.get_reasons(var).union({self.variable_lits[var]})
                    ng.add(self.reasoning_mode_stage_lits[2])
                    nogoods.append(ng)

            elif self.reasoning_mode == ReasoningMode.CAUTIOUS and not first_call:
                # Second time for cautious we only add nogoods that disable the changes for the variable
                for var in self.symbol2var[result_var.name].values():
                    ng = {self.variable_lits[var]}
                    ng.add(self.reasoning_mode_stage_lits[2])
                    nogoods.append(ng)
            else:
                assert False, "Should not reach here"

        return nogoods

    def add_nogoods_from_queue(self, ctl: clingo.PropagateControl) -> bool:
        """
        Add queued nogoods until the queue is empty or clingo refuses one.

        Args:
            ctl: Clingo PropagateControl object.

        Returns:
            bool: True if adding a nogood failed (propagation must stop).
        """
        while len(self.nogood_queue) > 0:
            ng = self.nogood_queue.pop(0)
            if not ctl.add_nogood(ng):
                return True

        return False

    def check_evaluate(self, ctl: clingo.PropagateControl):
        """
        Evaluate `evaluate` atoms against the current assignments.

        Args:
            ctl: Clingo PropagateControl object.
        """
        self.evaluations.update_evaluations(self.symbol2var.get_variables())
        for var in self.evaluatevars:
            var.evaluate(self.evaluations, ctl, self.environment)

    def propagate(self, control: clingo.PropagateControl, changes: Sequence[int]) -> None:
        """
        Propagate after a solver assignment change.
        Checks which variables are affected by the change, evaluates them,
        and applies optimization pruning if enabled.

        Args:
            control: Clingo propagation control.
            changes: Sequence of (signed) solver literals that changed.
        """
        if self.check_only:
            return

        if self.add_nogoods_from_queue(control):
            # backtracking due to nogoods in queue
            return

        to_evaluate: set[VariableType] = set()
        for rlit in changes:
            lit = abs(rlit)
            if lit in self.literal2var:
                to_evaluate.update(self.literal2var[lit])
            elif lit == self.optimization_stage_lits[2]:
                # if we are now in the second stage of optimization,
                # we can now look for equal valued solutions
                self.set_optimization_check_strength("le")
                print("Now in optimization stage 2, looking for equal or better solutions")

        backtrack = self.evaluated_solver_assignment(control, to_evaluate)
        if backtrack:
            # backtracking due to conflicts in evaluation of variables
            return

        # If not backtracking, check optimization sums
        self.evaluate_optimization_sum(control)

    def evaluate_optimization_sum(self, ctl: clingo.PropagateControl) -> bool:
        """
        Evaluate the current objective value and optionally prune.

        If the objective is already worse than the incumbent and the relevant
        parts are fully assigned, a nogood is added to exclude the current
        partial/total assignment.

        Args:
            ctl: Clingo propagation control.

        Returns:
            bool: True if a nogood was added requiring a backtrack.
        """
        if not self.using_optimization:
            return False
        self.evaluations.update_evaluations(self.symbol2var.get_variables())
        changed = self.optimization_sum.evaluate(self.evaluations, ctl, self.environment)
        if not changed:
            return False

        for i, _sum in enumerate(self.optimization_sum.get_value()):
            if _sum > self.best_value[i] or self.optimization_sum.has_unassigned(i):
                # if the value is better already,
                # rest of the priorities do not matter

                # if the value is not yet better but has unassigned variables, we cannot be sure yet
                # so we also break (since the behaviour for the rest of the priorities depends if this one is better, the same, or worse)
                break
            elif _sum == self.best_value[i]:
                # value is the same and has been fully assigned, check next priority
                # if this is the last value, all priorities were the same.
                if i == len(self.best_value) - 1 and self.optimization_strength == OptimizationStrength.STRICT:
                    # last priority and strict mode, add nogood to exclude this solution
                    # here, we dont know if this solution is also optimal or not, so we include the optimization stage literal
                    self.add_nogood_for_variable(
                        ctl, self.optimization_sum, extra_literals=[self.optimization_stage_lits[1]]
                    )
                    return True
                else:
                    # not last priority or lenient mode, keep looking at next priority
                    continue
            elif _sum < self.best_value[i] and not self.optimization_sum.has_unassigned(i):
                # if the value is worse and fully assigned, we can already add a nogood to exclude this solution
                # we dont add the stage literal since it is worse than the current best,
                # so it does not matter if we are looking for better or equal solutions to the optimal
                self.add_nogood_for_variable(ctl, self.optimization_sum)
                return True

        return False

    def add_nogood_for_variable(
        self,
        ctl: clingo.PropagateControl,
        var: VariableType | OptimizationHandler,
        extra_literals: Iterable[int] | None = None,
        conflict: bool = True,
    ) -> bool:
        """
        Add a nogood blocking the current assignment for a variable.

        The nogood is constructed from the literals that explain the variable's
        current value.

        It is also possible to include extra literals that should be added to the nogood (e.g. to block only for the current optimization stage).

        Args:
            ctl: Clingo PropagateControl object.
            var: Variable (or optimization handler) to block.
            extra_literals: Additional literals to include in the nogood.
            conflict: Whether to treat the nogood as a conflict.
        Returns:
            bool: True if propagation must stop False otherwise
        Raises:
            AssertionError: If we expected the nogood to be a conflict but the solver did not detect it
        """
        ng: set[int] = self.get_reasons(var)
        if extra_literals:
            ng = ng.union(extra_literals)
        prop_stop = ctl.add_nogood(ng)
        if conflict and prop_stop:
            assert (
                False
            ), f"Added violated constraint but solver did not detect it for variable {var} with reasons {ng} and truth values {[ctl.assignment.value(lit) for lit in ng]}"

        return not prop_stop

    def evaluated_solver_assignment(self, ctl: clingo.PropagateControl, to_evaluate: set[VariableType]) -> bool:
        """
        Evaluate a set of variables under the current solver assignment.

        If a variable changes, its parents are scheduled for evaluation.

        Args:
            ctl: Clingo PropagateControl object.
            to_evaluate: Variables that may have been affected by recent changes.

        Returns:
            bool: True if propagation should stop (conflict/forbidden warning),
            False otherwise.
        """
        while len(to_evaluate) > 0:
            var = to_evaluate.pop()

            result = self.evaluate_variable(ctl, var)
            if result is None:
                # variable had issue, stop propagation!
                return True
            elif result:
                # variable changed, evaluate parents
                for parent in var.parents:
                    to_evaluate.add(parent)
        return False

    def evaluate_variable(self, ctl: clingo.PropagateControl, var: VariableType) -> bool | None:
        """
        Evaluate one variable against the current assignment.

        Args:
            ctl: Clingo PropagateControl object.
            var: Variable to evaluate.

        Returns:
            bool | None:
                - True if the variable's value changed.
                - False if it did not change.
                - None if evaluation detected a conflict (nogood added).
        """
        self.evaluations.update_evaluations(self.symbol2var.get_variables())
        eval_result: EvaluationResult = var.evaluate(self.evaluations, ctl, self.environment)

        if eval_result == EvaluationResult.CONFLICT:
            self.add_nogood_for_variable(ctl, var)
            return None
        elif eval_result == EvaluationResult.INFER:
            if self.add_nogood_for_variable(ctl, var, extra_literals=var.infer(), conflict=False):
                return None

        # check if any errors are forbidden
        for _warning in var.get_errors():
            if _warning.id in self.forbidden_warnings:
                if _warning.id == warning.VariableWarning.badValue and not self.symbol2var.is_user_variable(var):
                    # forbid badValue warnings only for user variables
                    continue
                literal = self.forbidden_warnings[_warning.id]
                if ctl.assignment.is_true(literal):
                    # Forbidden warning exists, making program unsat
                    self.add_nogood_for_variable(ctl, var)
                    return None

        return eval_result == EvaluationResult.CHANGED

    def get_reasons(self, var: VariableType | OptimizationHandler, seen: set[VariableType] | None = None) -> set[int]:
        """Compute the set of literals explaining a variable's current value.

        This is used when constructing nogoods for conflicts, forbidden warnings,
        and optimization pruning.

        Args:
            var: Variable whose reasons should be collected.

        Returns:
            set[int]: Set of signed solver literals.
        """
        if seen is None:
            seen = set()
        reasons = var.literals
        for dvar in var.vars():
            if dvar.name == EXECUTION_OUTPUT:
                dvar = dvar.arguments[0]
            if dvar not in self.symbol2var:
                continue
            for vartype in self.symbol2var[dvar].values():
                if vartype not in seen:
                    seen.add(vartype)
                    reasons = reasons.union(self.get_reasons(vartype, seen))

        return reasons

    def undo(self, thread_id: int, assignment: clingo.Assignment, changes: Sequence[int]) -> None:
        """
        Undo propagator state on backtracking.

        This resets variable evaluations whose decision level is higher or equal to the current backtracking level
        and clears derived optimization state.

        Args:
            thread_id: Clingo thread id (unused).
            assignment: Current assignment after backtracking.
            changes: Literals undone by clingo.
        """
        self.symbol2var.reset(assignment.decision_level)

        self.optimization_sum.reset(assignment.decision_level)

    def get_engine_variables(self, ctl: clingo.PropagateInit):
        """
        Load atoms that represent the values of variables from the input program.

        This reads `_se_value`, `_set_contains`, and `Multimap_value` atoms and updates the
        corresponding variables with the assigned values.
        This is used for variables whose values are defined by other engines

        Args:
            ctl: Clingo PropagateInit object.
        """
        if len(self.symbol2var) == 0:
            # if there are no variables, we can skip this part since propagator is not used
            return
        value_atoms = myClorm.findInPropagateInit(ctl, post_processor._se_value)
        set_value_atoms = myClorm.findInPropagateInit(ctl, post_processor._set_contains)
        multimap_value_atoms = myClorm.findInPropagateInit(ctl, atom.Multimap_value)

        for (name, val), _literal in value_atoms.items():
            if not isinstance(name, expression.Variable):
                # ignore other stuff
                continue

            # if it is a variable, get the symbol for it
            _name = myClorm.pytocl(name).arguments[0]
            if _name not in self.symbol2var:
                if (
                    isinstance(val, post_processor.Ref)
                    and isinstance(val.expr, expression.Variable)
                    and val.expr == name
                ):
                    # If the set references itself, it should get its values later from _set_contains,
                    # Here, we make the set variable
                    # TODO: make a difference for sets and multimaps,
                    # currently, Ref is only implemented for sets so we do nothing for multimaps here
                    self.symbol2var.add_variable(_name, SetVariable(OTHER_ENGINE_VAR_NAME, _name, _literal))
                    ctl.add_watch(_literal)
                    ctl.add_watch(-_literal)
                    continue
                # If the value references something else, or it is not a reference,
                # we make a normal variable and add the value to it,
                self.symbol2var.add_variable(_name, Variable(OTHER_ENGINE_VAR_NAME, _name))

            variable: Variable = cast(Variable, self.symbol2var.get_variable(_name, getattr(Variable, "__name__")))
            expr: expression.Expr = val.expr if isinstance(val, post_processor.Ref) else val

            variable.add_value(expr, _literal, _literal)

            ctl.add_watch(_literal)
            ctl.add_watch(-_literal)

        for (name, val_set), _literal in set_value_atoms.items():
            if not isinstance(name, expression.Variable):
                continue
            _name = myClorm.pytocl(name).arguments[0]

            if _name not in self.symbol2var:
                self.errors.append(
                    warning.Warning(
                        warning.Variable(warning.VariableWarning.undeclared),  # ty:ignore[unresolved-attribute]
                        (_name,),
                        f"Warning: Got set value of another engine for variable that does not exist! Ignoring value {_name}, {val_set}.",
                    )
                )
                continue

            set_variable = cast(SetVariable, self.symbol2var.get_variable(_name, getattr(SetVariable, "__name__")))

            expr: expression.Expr = val_set.expr if isinstance(val_set, post_processor.Ref) else val_set

            set_variable.add_value(expr, _literal)
            ctl.add_watch(_literal)
            ctl.add_watch(-_literal)

        for (name, key, val), _literal in multimap_value_atoms.items():
            if name not in self.symbol2var:
                multimap_variable = DictVariable(OTHER_ENGINE_VAR_NAME, name, _literal)
                self.symbol2var.add_variable(name, multimap_variable)
            else:
                if self.symbol2var.has_var_type(name, getattr(DictVariable, "__name__")):
                    # TODO: fix issue where value(myvar, ref(dict...)) makes a variable when it should not
                    multimap_variable = DictVariable(OTHER_ENGINE_VAR_NAME, name, _literal)
                    self.symbol2var.add_variable(name, multimap_variable)
                multimap_variable = cast(
                    DictVariable, self.symbol2var.get_variable(name, getattr(DictVariable, "__name__"))
                )

            multimap_variable.add_value(key, val, _literal)

            ctl.add_watch(_literal)
            ctl.add_watch(-_literal)

    def get_variables(self, ctl: clingo.PropagateInit):
        """
        Load base variable declarations/definitions/domains from ASP facts.

        Reads variable-related atoms and creates/extends `Variable` instances.
        Note that nogoods are added to prevent True assignments to values that are parts of domains that are assigned False.

        Args:
            ctl: Clingo PropagateInit object.
        """
        var_declares = myClorm.findInPropagateInit(ctl, atom.Propagator_variable_declare)
        var_defines = myClorm.findInPropagateInit(ctl, atom.Propagator_variable_define)
        var_domains = myClorm.findInPropagateInit(ctl, atom.Propagator_variable_domain)
        var_optionals = myClorm.findInPropagateInit(ctl, atom.Propagator_variable_declareOptional)

        user_var_names = myClorm.findInPropagateInit(ctl, atom.Propagator_variable_interface)

        for (_, id), _ in user_var_names.items():
            self.symbol2var.add_user_variable_name(id)

        from_facts_literals: dict[clingo.Symbol, int] = {}
        for (name, symbol_var, domain), _literal in var_declares.items():
            if not self.symbol2var.has_var_type(symbol_var, getattr(Variable, "__name__")):
                self.symbol2var.add_variable(symbol_var, Variable(name, symbol_var))

            variable: Variable = cast(Variable, self.symbol2var.get_variable(symbol_var, getattr(Variable, "__name__")))

            ctl.add_watch(_literal)
            ctl.add_watch(-_literal)

            self.literal2var.setdefault(_literal, []).append(variable)

            if isinstance(domain, atom.BoolDomain):
                literal_true = ctl.add_literal(freeze=True)
                literal_false = ctl.add_literal(freeze=True)
                variable.add_value(
                    expression.Val(type_.BaseType.bool, True),  # ty:ignore[unresolved-attribute]
                    literal_true,
                    _literal,
                )
                variable.add_value(
                    expression.Val(type_.BaseType.bool, False),  # ty:ignore[unresolved-attribute]
                    literal_false,
                    _literal,
                )
                ctl.add_watch(literal_true)
                ctl.add_watch(-literal_true)
                ctl.add_watch(literal_false)
                ctl.add_watch(-literal_false)

                # if the declaration is False, then the value it can give can not be true
                ctl.add_clause([-literal_true, _literal])
                ctl.add_clause([-literal_false, _literal])

                self.literal2var[literal_true] = [variable]
                self.literal2var[literal_false] = [variable]

            elif isinstance(domain, atom.FromList):
                for expr in domain.elements:
                    literal = ctl.add_literal(freeze=True)
                    variable.add_value(expr, literal, _literal)
                    ctl.add_watch(literal)
                    ctl.add_watch(-literal)

                    ctl.add_clause([-literal, _literal])

                    self.literal2var[literal] = [variable]

            elif isinstance(domain, atom.FromFacts):
                # values will be added from facts, nothing to do here
                from_facts_literals[symbol_var] = _literal
            else:
                self.errors.append(
                    warning.Warning(
                        warning.Propagator(),
                        (symbol_var,),
                        f"Unknown domain type '{domain}' for variable '{symbol_var}'",
                    )
                )

        for (name, symbol_var, expr), _literal in var_defines.items():
            if not self.symbol2var.has_var_type(symbol_var, getattr(Variable, "__name__")):
                define_variable = Variable(name, symbol_var)
                self.symbol2var.add_variable(symbol_var, define_variable)

            define_variable: Variable = cast(
                Variable, self.symbol2var.get_variable(symbol_var, getattr(Variable, "__name__"))
            )
            define_variable.add_value(expr, _literal, _literal)
            ctl.add_watch(_literal)
            ctl.add_watch(-_literal)

            self.literal2var.setdefault(_literal, []).append(define_variable)
            # here we dont add a nogood since its the same literal

        for (name, symbol_var, domain_expr), _literal in var_domains.items():
            # These values are assigned the "from_facts" domain literal for the given variable
            if not self.symbol2var.has_var_type(symbol_var, getattr(Variable, "__name__")):
                continue
            domain_variable: Variable = cast(
                Variable, self.symbol2var.get_variable(symbol_var, getattr(Variable, "__name__"))
            )
            # literal = ctl.add_literal(freeze=True)
            domain_literal = from_facts_literals[symbol_var]
            domain_variable.add_value(domain_expr, _literal, domain_literal)
            ctl.add_watch(_literal)
            ctl.add_watch(-_literal)

            ctl.add_clause([-_literal, domain_literal])
            # literal defining the domain should also be included, not just the variable declaration literal!
            # ctl.add_clause([-literal, _literal])

            self.literal2var.setdefault(_literal, []).append(domain_variable)

        for (name, optional), _literal in var_optionals.items():
            if not self.symbol2var.has_var_type(optional, getattr(Variable, "__name__")):
                continue

            optional_variable: Variable = cast(
                Variable, self.symbol2var.get_variable(optional, getattr(Variable, "__name__"))
            )
            literal = ctl.add_literal(freeze=True)
            optional_variable.add_value(
                expression.Val(type_.BaseType.none, None), literal, _literal
            )  # ty:ignore[unresolved-attribute]
            ctl.add_watch(literal)
            ctl.add_watch(-literal)

            ctl.add_clause([-literal, _literal])

            self.literal2var.setdefault(_literal, []).append(optional_variable)
            self.literal2var[literal] = [optional_variable]

        for var in self.symbol2var.get_variables_by_type(getattr(Variable, "__name__")):
            var = cast(Variable, var)
            if len(var.expressions) == 0:
                var.add_value(expression.Bad.bad, 1, 1)

    def get_ensure(self, ctl: clingo.PropagateInit):
        """
        Load ensure constraints from ASP facts and create EnsureVariable instances.

        Args:
            ctl: Clingo PropagateInit object.
        """

        ensures = myClorm.findInPropagateInit(ctl, atom.Propagator_ensure)
        for (name, expr), literal in ensures.items():
            ensure_var: EnsureVariable = EnsureVariable(name, expr, literal)
            ctl.add_watch(literal)
            ctl.add_watch(-literal)
            self.literal2var.setdefault(literal, []).append(ensure_var)
            # Var name is given here so it works well with the rest of the system
            # It should do nothing and also should never appear in any assignments!!
            self.symbol2var.add_variable(ensure_var.var, ensure_var)

    def get_evaluate(self, ctl: clingo.PropagateInit):
        """
        Load `evaluate` atoms into `EvaluateVariable` instances.
        Also load "bool_evaluate" atoms and create the corresponding variables.

        Args:
            ctl: Clingo PropagateInit object.
        """

        evaluate_atoms = myClorm.findInPropagateInit(ctl, atom.Propagator_evaluate)
        bool_evaluate_atoms = myClorm.findInPropagateInit(ctl, atom.Propagator_bool_evaluate)
        bool_evaluated_atoms = myClorm.findInPropagateInit(ctl, atom.Bool_evaluated)
        for (_, op, args), literal in evaluate_atoms.items():
            var = EvaluateVariable(op, args, literal)
            if literal != 1:
                self.errors.append(
                    warning.Warning(
                        warning.Propagator(),
                        (var,),
                        f"Evaluate atom {op} with args {args} is not a fact!",
                    )
                )
            self.evaluatevars.append(var)

        true_val = expression.Val(type_.BaseType.bool, True)  # ty:ignore[unresolved-attribute]
        false_val = expression.Val(type_.BaseType.bool, False)  # ty:ignore[unresolved-attribute]

        for (label, expr), literal in bool_evaluate_atoms.items():
            b_vals = {}
            for (bexpr, value), b_literal in bool_evaluated_atoms.items():
                if bexpr == expr:
                    b_vals[value] = b_literal
                    ctl.add_watch(b_literal)
                    ctl.add_watch(-b_literal)

            bool_var = BoolEvaluateVariable(
                label, expr, literal, b_vals[true_val], b_vals[false_val], b_vals[expression.Bad.bad]
            )

            ctl.add_watch(literal)
            ctl.add_watch(-literal)
            self.literal2var.setdefault(literal, []).append(bool_var)
            # Var name is given here so it works well with the rest of the system
            # It should do nothing and also should never appear in any assignments!!
            self.symbol2var.add_variable(bool_var.var, bool_var)

    def get_solver_identifier(self, ctl: clingo.PropagateInit):
        """
        Initialize the Python evaluation environment using the solver identifier.

        Args:
            ctl: Clingo PropagateInit object.
        """

        for id, _ in myClorm.findInPropagateInit(ctl, atom.Main_solverIdentifiers).items():
            self.environment = evaluator.get_environment(id.id)

    def get_optimization_sums(self, ctl: clingo.PropagateInit):
        """
        Load optimization sum declarations from ASP facts and create OptimizationSum instances.

        Args:
            ctl: Clingo PropagateInit object.
        """

        maxSums = myClorm.findInPropagateInit(ctl, atom.Propagator_optimize_maximizeSum)

        for prop_sum in ctl.symbolic_atoms.by_signature("propagator_optimize_maximizeSum", 4):
            self.prop_sum_atoms.append(prop_sum.symbol)

        for (_, expr, symbol, priority), literal in maxSums.items():
            self.using_optimization = True
            self.optimization_sum.add_value(symbol, expr, literal, priority)

        self.best_value = [-sys.maxsize] * self.optimization_sum.get_sum_count()

    def get_set_declarations(self, ctl: clingo.PropagateInit):
        """
        Load set declarations and assignments from ASP facts.

        Args:
            ctl: Clingo propagation initializer.
        """

        declares = myClorm.findInPropagateInit(ctl, atom.Propagator_set_declare)
        for (name, symbol_var), literal in declares.items():
            variable = SetVariable(name, symbol_var, literal)
            self.symbol2var.add_variable(symbol_var, variable)
            self.literal2var.setdefault(literal, []).append(variable)

            ctl.add_watch(literal)
            ctl.add_watch(-literal)

        assigns = myClorm.findInPropagateInit(ctl, atom.Propagator_set_assign)
        for (name, symbol_var, expr), literal in assigns.items():
            try:
                setvar: SetVariable = cast(
                    SetVariable, self.symbol2var.get_variable(symbol_var, getattr(SetVariable, "__name__"))
                )
            except KeyError:
                continue
            setvar.add_value(expr, literal)
            self.literal2var.setdefault(literal, []).append(setvar)

            ctl.add_watch(literal)
            ctl.add_watch(-literal)

        domains = myClorm.findInPropagateInit(ctl, atom.Propagator_set_baseDomain)
        for (name, symbol_var, domain_expr), _literal in domains.items():
            try:
                setvar: SetVariable = cast(
                    SetVariable, self.symbol2var.get_variable(symbol_var, getattr(SetVariable, "__name__"))
                )
            except KeyError:
                continue
            setvar.add_value(domain_expr, _literal)
            self.literal2var.setdefault(_literal, []).append(setvar)

            ctl.add_watch(_literal)
            ctl.add_watch(-_literal)

    def get_multimap_declarations(self, ctl: clingo.PropagateInit):
        """
        Load multimap (dict) declarations and assignments from ASP facts.

        Args:
            ctl: Clingo PropagateInit object.
        """
        declares = myClorm.findInPropagateInit(ctl, atom.Propagator_multimap_declare)
        for (name, symbol_var), literal in declares.items():
            variable = DictVariable(name, symbol_var, literal)
            self.symbol2var.add_variable(symbol_var, variable)
            self.literal2var.setdefault(literal, []).append(variable)

            ctl.add_watch(literal)
            ctl.add_watch(-literal)

        assigns = myClorm.findInPropagateInit(ctl, atom.Propagator_multimap_assign)
        for (name, symbol_var, key_expr, expr), literal in assigns.items():
            try:
                dictvar: DictVariable = cast(
                    DictVariable, self.symbol2var.get_variable(symbol_var, getattr(DictVariable, "__name__"))
                )
            except KeyError:
                continue
            dictvar.add_value(key_expr, expr, literal)
            self.literal2var.setdefault(literal, []).append(dictvar)

            ctl.add_watch(literal)
            ctl.add_watch(-literal)

    def get_execution_declarations(self, ctl: clingo.PropagateInit):
        """
        Load execution blocks and run-atoms from ASP facts and create Execution instances.

        Args:
            ctl: Clingo PropagateInit object.
        """
        declares = myClorm.findInPropagateInit(ctl, atom.Propagator_execution_declare)
        for (name, symbol_var, stmt, in_v, out_v), literal in declares.items():
            if not self.symbol2var.has_var_type(symbol_var, getattr(Execution, "__name__")):
                variable = Execution(name, symbol_var, in_v, out_v)
                self.symbol2var.add_variable(symbol_var, variable)

            variable = cast(Execution, self.symbol2var.get_variable(symbol_var, getattr(Execution, "__name__")))
            variable.add_statement(stmt, literal)
            self.literal2var.setdefault(literal, []).append(variable)

            ctl.add_watch(literal)
            ctl.add_watch(-literal)

        exec_runs = myClorm.findInPropagateInit(ctl, atom.Propagator_execution_run)
        for (name, symbol_var), literal in exec_runs.items():
            if not self.symbol2var.has_var_type(symbol_var, getattr(Execution, "__name__")):
                self.errors.append(
                    warning.Warning(
                        warning.Variable(warning.VariableWarning.undeclared),  # ty:ignore[unresolved-attribute]
                        (symbol_var,),
                        f"Execution variable '{symbol_var}' run exists but variable not declared!",
                    )
                )
                continue
            execvar: Execution = cast(
                Execution, self.symbol2var.get_variable(symbol_var, getattr(Execution, "__name__"))
            )
            execvar.add_run_literal(literal)
            self.literal2var.setdefault(literal, []).append(execvar)

            ctl.add_watch(literal)
            ctl.add_watch(-literal)

    def get_forbidden_warnings(self, ctl: clingo.PropagateInit) -> None:
        """
        Load `warning_forbid` atoms.

        Args:
            ctl: Clingo propagation initializer.
        """

        forbidden_warnings = myClorm.findInPropagateInit(ctl, atom.Propagator_warning_forbid)
        ignored_warnings = myClorm.findInPropagateInit(ctl, atom.Propagator_warning_ignore)

        for (name, error), literal in forbidden_warnings.items():
            self.forbidden_warnings[error] = literal

        for (name, error), literal in ignored_warnings.items():
            # Initially, set to False, and only set to True if the warning is actually observed
            # The actual value is set in the check function
            self.ignored_warnings[error] = literal, False

        # If a forbidden warning exists already, add empty constraint to make the program unsat
        # Since the warning comes from just reading the input
        for __warning in self.errors:
            if __warning.id in self.forbidden_warnings:
                literal = self.forbidden_warnings[__warning.id]
                if ctl.assignment.is_true(literal):
                    ctl.add_clause([])
                    return

    def set_parents(self):
        """
        Populate parent relationships between variables.

        Parents are variables that depend on another variable's value; if a child
        changes, parents are scheduled for re-evaluation.
        """
        useless_other_engine_vars: list[VariableType] = []

        for var in self.symbol2var.get_variables():
            for symbol_var in var.vars():
                if symbol_var.name.startswith(EXECUTION_OUTPUT):
                    # if the variable it depends on is an execution output,
                    # then we look for the name of the execution variable
                    symbol_var = symbol_var.arguments[0]
                if symbol_var == var.var:
                    # don't add self as parent
                    # for self referencing variables
                    continue
                if symbol_var not in self.symbol2var:
                    continue

                for dvar in self.symbol2var[symbol_var].values():
                    dvar.parents.append(var)

        for var in self.symbol2var.get_variables():
            if var.name == OTHER_ENGINE_VAR_NAME and var.parents == []:
                useless_other_engine_vars.append(var)

        for var in useless_other_engine_vars:
            # Variable is an compile/ground engine variable with no parents, removing it since it is useless for us
            self.symbol2var.delete_variable(var.var)

    def update_python_model(self):
        """
        Build the python-side model representation from current variable values.

        Populates `self.python_model` with result atoms (values, sets, multimaps,
        evaluated atoms) and warning atoms. This is used by `on_model` to extend
        the clingo model and by brave/cautious reasoning to accumulate results.
        """
        self.python_model = set()
        model_errors: propagator_warning_t = []
        for var in self.symbol2var.get_variables():
            self.handle_on_model_warning(var.get_errors())
            if isinstance(var, EnsureVariable) or isinstance(var, BoolEvaluateVariable):
                continue
            if var.name == OTHER_ENGINE_VAR_NAME:
                # these variables are only used to get values from other engines, they should not be exported to the model
                continue
            final_value = var.get_value()
            if final_value is ValueStatus.NOT_SET:
                model_errors.append(
                    warning.Warning(warning.Propagator(), (str(var),), "Variable has no value set in on_model!")
                )
                continue

            if final_value is ValueStatus.ASSIGNMENT_IS_FALSE:
                continue

            if isinstance(var, Execution):
                for var, value in final_value:
                    if value is ValueStatus.NOT_SET:
                        assert False, f"Execution variable {var} has output with no value set in on_model!"

                    self.handle_on_model_value(var, value)
            else:
                self.handle_on_model_value(var.var, final_value)

        for eval_var in self.evaluatevars:
            self.handle_on_model_warning(eval_var.get_errors())
            final_value = eval_var.get_value()
            pyVal, errors = evaluator.reducedExpr(final_value)  # TODO: handle errors
            pyAtom = atom.Evaluated(
                eval_var.op,
                eval_var.args,
                pyVal,
            )
            self.python_model.add(pyAtom)

        if self.using_optimization:
            self.handle_on_model_warning(self.optimization_sum.get_errors())

        self.handle_on_model_warning(model_errors + self.errors)

    def on_model(self, model: clingo.Model):
        """
        Extend the clingo model using python-side result atoms.

        Args:
            model: Current clingo model.
        """
        # add to the clingo output the final result based on reasoning mode
        # For brave and cautious, we output the accumulated result (similar to clingo)
        # For standard, we output the current model

        assert self.python_model is not None
        for pyAtom in self.python_model:
            clAtom = myClorm.pytocl(pyAtom)
            if not model.contains(clAtom):
                model.extend([clAtom])

        if self.using_optimization:
            self.add_optimization_values(model)
            if clingo.Function(OPTIMIZATION_STAGE_ATOM, [clingo.Number(2)]) in model.symbols(atoms=True):
                self.optimal_models_found += 1
            if self.optimal_models_wanted > 0 and self.optimal_models_found >= self.optimal_models_wanted:
                # Stop search once the desired number of optimal models is found by adding an empty clause to make the program unsat
                model.context.add_clause([])

    def handle_on_model_value(self, var: clingo.Symbol, final_value: Any):
        """
        Dispatch model export based on the final value type.

        Args:
            var: Variable symbol.
            final_value: Evaluated value for the variable.
        """
        if final_value is ValueStatus.NOT_SET:
            assert False, f"Variable {var} has no value set in on_model!"

        if isinstance(final_value, expression.constant | expression.Bad):
            self.handle_on_model_normal_type(var, final_value)

        elif isinstance(final_value, (set, frozenset)):
            self.handle_on_model_set(var, final_value)

        elif isinstance(final_value, (dict, multimap.HashableDict)):
            self.handle_on_model_dict(var, final_value)

        elif isinstance(final_value, tuple):
            self.handle_on_model_normal_type(var, final_value)
        else:
            # In here come Variable(Lambda) and others
            print(f"Unknown variable type {type(final_value)} for variable {var} in on_model!")

    def handle_on_model_set(self, var: clingo.Symbol, final_value: set | frozenset):
        """
        Add atoms for a set-typed variable to the python model.

        Args:
            var: Variable symbol.
            final_value: Set/frozenset value.
        """
        assert self.python_model is not None

        try:
            pyVal = expression.Ref(evaluator.get_baseType(final_value), clingo.Function("variable", [var]))
            pyAtoms = [atom.Value(var, pyVal)]

            for value in final_value:
                if value is ValueStatus.NOT_SET:
                    assert False, f"Set variable {var} has no value set in on_model!"

                if value == expression.Bad.bad:  # ty:ignore[unresolved-attribute]
                    set_pyVal = value
                else:
                    set_pyVal = expression.Val(evaluator.get_baseType(value), value)
                set_pyAtom = atom.Set_value(var, set_pyVal)
                pyAtoms.append(set_pyAtom)
            for pyAtom in pyAtoms:
                self.python_model.add(pyAtom)
        except Exception as exn:  # TODO: add warnings?
            self.python_model.add(atom.Value(var, expression.Bad.bad))

    def handle_on_model_dict(self, var: clingo.Symbol, final_value: dict):
        """
        Add atoms for a dict/multimap-typed variable to the python model.

        Args:
            var: Variable symbol.
            final_value: Mapping value (may be a `HashableDict`).
        """
        assert self.python_model is not None

        if final_value == expression.Bad.bad:  # ty:ignore[unresolved-attribute]
            pyVal = final_value
        else:
            try:
                pyVal = expression.Val(evaluator.get_baseType(final_value), var)
            except Exception:
                pyVal = expression.Bad.bad
        pyAtom = atom.Value(var, pyVal)
        self.python_model.add(pyAtom)

        if pyVal != expression.Bad.bad:
            for key, value in final_value.items():
                if value is ValueStatus.NOT_SET:
                    assert False, f"Dict variable {var} has key {key} with no value set in on_model!"

                for val in value:
                    mm_pyKey, keyErrors = evaluator.reducedExpr(key)  # TODO: handle errors
                    mm_pyVal, valErrors = evaluator.reducedExpr(val)
                    mm_pyAtom = atom.Multimap_value(var, mm_pyKey, mm_pyVal)

                    self.python_model.add(mm_pyAtom)

    def handle_on_model_normal_type(
        self,
        var: clingo.Symbol,
        final_value: (
            bool | int | float | str | clingo.Symbol | tuple[Any, ...] | expression.Bad.bad
        ),  # ty:ignore[unresolved-attribute]
    ):
        """
        Add atoms for a variable (bool/int/float/string/symbol) to the python model.

        Args:
            var: Variable symbol.
            final_value: Scalar value.
        """
        assert self.python_model is not None
        pyVal, errors = evaluator.reducedExpr(final_value)  # TODO: handle errors
        pyAtom = atom.Value(var, pyVal)
        self.python_model.add(pyAtom)

    def handle_on_model_warning(self, errors: propagator_warning_t):
        """
        Add warning atoms to the python model.

        Args:
            errors: Iterable of warning atoms.
        """
        assert self.python_model is not None

        for __warning in errors:
            if __warning.id in self.ignored_warnings:
                assigned = self.ignored_warnings[__warning.id][1]
                if not assigned:
                    # if warning is not ignored, add to model
                    self.python_model.add(__warning)

    def get_expr_values(self, variables: Iterable[VariableType | OptimizationHandler]) -> dict[Symbol, Symbol]:
        """
        Get the expressions and their evaluated values for a list of variables.
        This is intended to be used in the post processing

        Args:
            variables: Iterable ofVariableTypes or OptimizationHandlers for which to get the expressions and their evaluated values.
        """
        vals = {}
        for var in variables:
            for expr in var.expressions:
                if expr.value not in [ValueStatus.NOT_SET, ValueStatus.ASSIGNMENT_IS_FALSE, None, expression.Bad.bad]:
                    vals[myClorm.pytocl(expr.expr)] = post_processor._numeric_value_symbol(
                        expr.value, type(expr.value) is float
                    )

        return vals

    def add_optimization_values(self, model: clingo.Model):
        """
        Add optimization value atoms for optimization sums to the model.
        This uses the post_processor.py "_extend_optimize_values" function.

        Args:
            model: Clingo model to extend.
        """
        assert self.python_model is not None
        optimize_values = post_processor._extend_optimize_values(
            self.get_expr_values([self.optimization_sum]), self.prop_sum_atoms
        )
        for opt_val in optimize_values:
            clAtom = myClorm.pytocl(opt_val)
            if not model.contains(clAtom):
                model.extend([clAtom])
