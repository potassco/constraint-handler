from collections.abc import Iterable, Sequence
from itertools import product
from typing import Any, cast

import clingo
from clingo import Symbol

import constraint_handler.schemas.propagator_atom as prop_atom
from constraint_handler import evaluator, myClorm
from constraint_handler.model_builder import ModelBuilder
from constraint_handler.optimization_modes import OptimizationModeHandler
from constraint_handler.PropagatorConstants import (
    OTHER_ENGINE_VAR_NAME,
    PROPAGATOR_CHECK_MODE_ATOM,
    EvaluationResult,
    ValueStatus,
    propagator_warning_t,
)
from constraint_handler.PropagatorVariables import (
    BoolEvaluateVariable,
    DictVariable,
    EnsureVariable,
    EvaluateVariable,
    Evaluations,
    OptimizationHandler,
    SharedValue,
    VariableManager,
    VariableType,
    VariableValue,
    VariableValueRegistry,
    is_evaluation_possible,
)
from constraint_handler.reasoning_modes import ReasoningModeHandler
from constraint_handler.schemas import expression, internal, result, warning
from constraint_handler.variable_loader import VariableLoader


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
        optimization: Controller for objective sums, pruning, and optimal-model enumeration.
        environment: Evaluation environment built from solver identifier.
        check_only: If True, `propagate` becomes a no-op. Will only evaluate variables in `check`.
        errors: Warnings collected while evaluating variables or reading the input program.
        reasoning_mode: STANDARD/BRAVE/CAUTIOUS mode.
        python_model: Stores the python-level model for output.
    """

    def __init__(self):
        """
        Initialize the propagator.

        Args:
            check_only: If True, do not perform propagation (only allow checks).
        """
        self.variable_manager: VariableManager = VariableManager()
        self.literal2var: dict[int, list[VariableType]] = {}
        self.evaluations: Evaluations = Evaluations()

        self.expr2var: dict[VariableValue, list[VariableType]] = {}
        self.var2expr: dict[Symbol, set[VariableValue]] = {}
        self.lit2expr: dict[int, set[VariableValue]] = {}
        self.value_registry = VariableValueRegistry()

        self.evaluatevars: list[EvaluateVariable] = []

        self.optimization: OptimizationModeHandler = OptimizationModeHandler()
        self.shared_values: list[SharedValue] = []

        self.environment: myClorm.ImmutableList[expression.constant] = myClorm.ImmutableList()

        self.check_only = False

        self.errors: propagator_warning_t = []

        self.reasoning_mode_handler = ReasoningModeHandler()
        self.python_model: set[result.ResultAtom] | None = None

        self.nogood_queue: list[Iterable[int]] = []

        self.var_ranks: dict[Symbol, int] = {}
        self.var_ranks_expr: dict[VariableValue, int] = {}

        self.forbidden_warnings: dict[warning.Kind, int] = {}
        self.ignored_warnings: dict[warning.Kind, tuple[int, bool]] = {}

        self.watches: set[int] = set()

    def get_configuration(self, ctl: clingo.Control):
        """
        Read clingo configuration and initialize reasoning and optimization settings.

        The mode handlers configure their respective encodings and report incompatible heuristics.

        Args:
            ctl: Clingo control instance.
        """
        reasoning_warning = self.reasoning_mode_handler.configure(ctl)
        if reasoning_warning is not None:
            self.errors.append(reasoning_warning)

        optimization_warning = self.optimization.configure(ctl)
        if optimization_warning is not None:
            self.errors.append(optimization_warning)

    def init(self, init: clingo.PropagateInit) -> None:
        """
        Function implementing the init method of a Propagator.
        See clingo Propagator documentation for more details.

        Args:
            init: Clingo PropagateInit object
        """
        self.variable_manager = VariableManager()
        self.evaluations = Evaluations()
        self.literal2var.clear()
        self.evaluatevars.clear()
        self.expr2var.clear()
        self.var2expr.clear()
        self.lit2expr.clear()
        self.value_registry = VariableValueRegistry()
        self.optimization.reset()
        self.reasoning_mode_handler.reset()
        self.environment = {}
        self.errors.clear()

        init.check_mode = clingo.PropagatorCheckMode.Total

        if PROPAGATOR_CHECK_MODE_ATOM in init.symbolic_atoms:
            self.check_only = True

        self.get_solver_identifier(init)

        loader = VariableLoader(
            self.variable_manager,
            self.errors,
            self.evaluatevars,
            self.shared_values,
            get_variable_value=self.get_variable_value,
            register_variable_value=self.register_variable_value,
            add_literal2var=self.add_literal2var,
            add_watch=self.add_watch,
        )
        loader.load_variables(init)
        self.get_optimization_sums(init)
        loader.load_evaluations(init)

        self.set_parents()

        self.reasoning_mode_handler.add_helper_atoms(init, self.variable_manager.get_variables())
        self.optimization.add_helper_atoms(init, self.add_watch)

        self.get_forbidden_warnings(init)

        for expr in self.value_registry.get_all():
            for var in expr.vars():
                self.var2expr.setdefault(var, set()).add(expr)

        self.get_variable_ranks()

        # valuations = self.preprocess()
        # self.ensure_pairs_dict = self.ensure_pairs(valuations)

        # self.apply_preprocessing(valuations, init)

        self.evaluations.init(list(self.variable_manager.get_variables()))

        self.add_watches_to_ctl(init)

    def add_watch(self, lit: int) -> None:
        """
        Add a watch literal to the set of watched literals if check_only is disabled

        Args:
            lit: Literal to watch.
        """
        if not self.check_only:
            self.watches.add(lit)

    def add_literal2var(self, literal: int, variable: VariableType) -> None:
        """
        Associate a variable with the positive form of a solver literal.
        Args:
            literal: Solver literal.
            variable: Variable to associate with the literal.
        """
        self.literal2var.setdefault(abs(literal), []).append(variable)

    def get_literal2var(self, literal: int) -> list[VariableType]:
        """
        Get variables associated with a solver literal, regardless of sign.

        Args:
            literal: Solver literal.

        Returns:
            list[VariableType]: List of associated variables.
        """
        return self.literal2var.get(abs(literal), [])

    def get_expr2var(self, expr: VariableValue) -> list[VariableType]:
        """
        Get variables associated with an expression, or an empty list.

        Args:
            expr: Expression value.

        Returns:
            list[VariableType]: List of associated variables.
        """
        return self.expr2var.get(expr, [])

    def delete_literal2var(self, literal: int, variable: VariableType) -> bool:
        """
        Remove a literal-variable association, returning whether it existed.

        Args:
            literal: Solver literal.
            variable: Variable to disassociate from the literal.

        Returns:
            bool: True if the association existed and was removed, False otherwise.
        """
        key = abs(literal)
        variables = self.literal2var.get(key)
        if variables is None:
            return False

        try:
            variables.remove(variable)
        except ValueError:
            return False

        if not variables:
            del self.literal2var[key]
        return True

    def set_literal2expr(self, literal: int, value: VariableValue) -> None:
        """
        Associate a value with the positive form of a solver literal.

        Args:
            literal: Solver literal.
            value: Expression value to associate with the literal.
        """
        self.lit2expr.setdefault(abs(literal), set()).add(value)

    def get_literal2expr(self, literal: int) -> set[VariableValue]:
        """
        Get values associated with a solver literal, regardless of sign.

        Args:
            literal: Solver literal.

        Returns:
            set[VariableValue]: Set of associated expression values.
        """
        return self.lit2expr.get(abs(literal), set())

    def get_variable_value(self, expr: expression.Expr, literal: int) -> VariableValue:
        """
        Intern a value and index it by its solver literal.

        Args:
            expr: Expression object.
            literal: Solver literal.

        Returns:
            VariableValue: Interned expression value.
        """
        value = self.value_registry.get(expr, literal)
        self.set_literal2expr(literal, value)
        return value

    def register_variable_value(self, variable: VariableType, value: VariableValue) -> None:
        """
        Associate an interned value with its owning variable.

        Args:
            variable: Owning variable.
            value: Interned expression value.
        """
        owners = self.expr2var.setdefault(value, [])
        if not any(owner is variable for owner in owners):
            owners.append(variable)

    def add_watches_to_ctl(self, ctl: clingo.PropagateInit) -> None:
        """
        Register all watch literals

        Args:
            ctl: Clingo PropagateInit object.
        """
        for lit in self.watches:
            ctl.add_watch(lit)

    def get_variable_ranks(self) -> None:
        """
        Variables get a rank based on rank of dependencies.
        """

        # loop over vars and get the ones without deps, those have rank 0
        # loop again and get vars with satisfied deps based on known ranks
        # those get rank +1
        known_vars: set[Symbol] = set()
        changed = True
        rank = 0
        while changed:
            changed = False
            vars_this_loop: set[Symbol] = set()
            for var in self.variable_manager.keys():  # noqa: SIM118
                if var in known_vars:
                    continue
                if self.variable_manager.get_dependencies(var).issubset(known_vars):
                    self.var_ranks[var] = rank
                    changed = True
                    vars_this_loop.add(var)

            known_vars.update(vars_this_loop)
            rank += 1

        for v in set(self.variable_manager.keys()) - known_vars:
            # if a variable can't have its dependencies satisfied
            # (e.g., one of them does not exist)
            # then we just assign rank -1
            # print(f"warning: Variable {v} can't have its dependencies satisfied.")
            self.var_ranks[v] = -1

        for expr in self.value_registry.get_all():
            try:
                self.var_ranks_expr[expr] = max((self.var_ranks[var] + 1 for var in expr.vars()), default=0)
            except KeyError:
                # print(f"Warning: Expression {expr} has unknown variable as dependency.")
                self.var_ranks_expr[expr] = -1

    def ensure_pairs(
        self, valuations: dict[Symbol, set[Any]]
    ) -> dict[EnsureVariable, dict[Symbol, dict[Any, set[Any]]]]:
        """
        Return a dictionary mapping ensure to a list of dicts X

        Only works with ensure with 2 variables

        A dict X maps a symbol, that is a variable used in the ensure, to a dict of possible values for that variable
        and the possible values for the other variable in the ensure that can work with the first variable's value.
        E.g. d["ensure_1"] = {
            "var1": {
                1: [2,3],
                2: [3,4]
            },
            "var2": {
                2: [1],
                3: [1,2],
                4: [2]
            }
        }
        Args:
            valuations: A dictionary mapping variable symbols to their possible values.

        Returns:
            dict[EnsureVariable, dict[Symbol, dict[Any, set[Any]]]]: A dictionary mapping ensure variables to their corresponding value pairs.
        """

        # TODO: parts of this are very similar to check_ensure. Maybe make the similar parts into a function?
        ensure_pairs = {}
        for ensure_var in self.variable_manager.get_variables_by_type(EnsureVariable.__name__):
            ensure_var = cast(EnsureVariable, ensure_var)
            if len(ensure_var.vars()) != 2:
                continue

            ensure_pairs[ensure_var] = {var: {} for var in ensure_var.vars()}

            for var in ensure_var.vars():
                if var not in valuations:
                    assert False, f"Variable {var} not in valuations, but is used in ensure {ensure_var}"

            deps: list[Symbol] = list(ensure_var.vars())
            dep1, dep2 = deps[0], deps[1]
            for values in product(*(valuations[dep1], valuations[dep2])):
                eval_dict = dict(zip(deps, values))
                success = ensure_var.simple_evaluate(eval_dict, self.environment)
                if success:
                    ensure_pairs[ensure_var][dep1].setdefault(eval_dict[dep1], set()).add(eval_dict[dep2])
                    ensure_pairs[ensure_var][dep2].setdefault(eval_dict[dep2], set()).add(eval_dict[dep1])

        return ensure_pairs

    def preprocess(self, cycles: int = -1) -> dict[Symbol, set[Any]]:
        """
        Preprocess the propagator before solving.

        This finds the possible domains for all variables, checks the ensures to see which ones are the possible ones
        and prunes the variables based on their ability to be used in variables that depend on them.

        Args:
            cycles: The number of preprocessing cycles to perform. Defaults to -1, which means unlimited cycles.
        Returns:
            dict[Symbol, set[Any]]: A dictionary mapping variable symbols to their possible values.
        """
        valuations: dict[Symbol, set[Any]] = {}
        evaluation_order = []

        self.infer_domain(valuations, evaluation_order)

        cycles_done = 0

        while cycles < 0 or cycles_done < cycles:
            cycles_done += 1
            change1 = self.backward_prune(valuations, evaluation_order)
            change2 = self.forward_prune(valuations, evaluation_order)
            if not change1 and not change2:
                break

        # print(f"Preprocessing done in {cycles_done} cycles.")
        return valuations

    def forward_prune(self, valuations: dict[Symbol, set[Any]], evaluation_order: list[Symbol]) -> bool:
        """
        Forward prune the valuations of variables based on their dependencies.

        This is useful when during backward pruning a variable's domain is reduced, which may allow for further pruning of dependent variables.
        E.g. y = x+1, z = x-1
            x domain is {1,2,3}
            y domain is {2,3,4} z domain is {0,1,2}
            due to an ensure, y domain is now {2,3}
            backward pruning will reduce x domain to {1,2}
            now forward pruning will reduce z domain to {0,1} since x can only be 1 or 2.

        Args:
            valuations: Current valuations of variables.
            evaluation_order: Order in which variables were evaluated.

        Returns:
            bool: True if any valuations were pruned, False otherwise.
        """
        changed = False
        for var in evaluation_order:
            deps = list(self.variable_manager.get_dependencies(var))
            if len(deps) == 0:
                continue

            possible_values = set()
            for _var in self.variable_manager[var].values():
                possible_values.update(_var.simple_evaluate(valuations, self.environment))

            if valuations[var].issubset(possible_values):
                continue

            valuations[var].intersection_update(possible_values)
            changed = True

        # TODO: optimization to not check ensures if nothing changed?
        vals_after_ensures = self.check_ensures(valuations)
        for s, vals in vals_after_ensures.items():
            if len(vals) != len(valuations[s]):
                changed = True
        valuations.update(vals_after_ensures)

        return changed

    def backward_prune(self, valuations: dict[Symbol, set[Any]], evaluation_order: list[Symbol]) -> bool:
        """
        Prune the valuations of variables based on their dependencies.

        Args:
            valuations: Current valuations of variables.
            evaluation_order: Order in which variables were evaluated.

        Returns:
            bool: True if any valuations were pruned, False otherwise.
        """

        var_values: dict[Symbol, set[Any]] = {}
        changed = False

        for var_symb in reversed(evaluation_order):
            if var_symb not in var_values:
                var_values[var_symb] = valuations[var_symb]
            for var in self.variable_manager[var_symb].values():
                for dep, values in var.asses_dependencies_values(valuations, self.environment).items():
                    var_values.setdefault(dep, set()).update(values)

        # Cant update valuations after every var since some values might be useful in other variables as well.
        # so we must update after all variables are processed.
        for dep, values in var_values.items():
            if len(valuations[dep]) != len(values):
                changed = True
                valuations[dep] = values

        vals_after_ensures = self.check_ensures(valuations)
        for s, vals in vals_after_ensures.items():
            if len(vals) != len(valuations[s]):
                changed = True
        valuations.update(vals_after_ensures)

        return changed

    def apply_preprocessing(self, valuations: dict[Symbol, set[Any]], init: clingo.PropagateInit) -> None:
        """
        Apply the preprocessed valuations to the propagator's variables.

        Args:
            valuations: A dictionary mapping variable symbols to their possible values.
            init: The clingo.PropagateInit instance used for setting possible values.
        """
        for var_symb, values in valuations.items():
            for var in self.variable_manager[var_symb].values():
                var.set_possible_values(values, init)

        del_list = []
        for ensure_var in self.variable_manager.get_variables_by_type(EnsureVariable.__name__):
            ensure_var = cast(EnsureVariable, ensure_var)

            deps: list[Symbol] = list(ensure_var.vars())

            if not all(dep in valuations for dep in deps):
                continue

            always_possible: bool = True
            for values in product(*(valuations[dep] for dep in deps)):
                eval_dict = dict(zip(deps, values))
                success = ensure_var.simple_evaluate(eval_dict, self.environment)

                # if the ensure variable can fail then only_possible becomes False eventually
                always_possible &= success

            if always_possible:
                # if the ensure variable never fails
                # then we don't have to keep it around since it is useless
                del_list.append(ensure_var)

        for ensure_var in del_list:
            self.variable_manager.remove(ensure_var.var)

    def infer_domain(self, valuations: dict[Symbol, set[Any]], eval_order: list[Symbol]) -> None:
        """
        Loop over all variables and calculate domains for the ones that have all dependencies known.
        This function must be called repeatedly to do get the domain for all variables.

        Args:
            valuations: Current valuations of variables. This is modified in-place to add new possible values for variables.
            eval_order: List of variable symbols in the order they were evaluated. This is modified in-place to add new variables that were evaluated.
        """
        preprocessed_something = False
        current_vars = set(valuations.keys())
        for var in self.variable_manager.keys():  # noqa: SIM118
            if var in valuations:
                continue

            if (
                self.variable_manager.has_var_type(var, EnsureVariable.__name__)
                or self.variable_manager.has_var_type(var, BoolEvaluateVariable.__name__)
                or self.variable_manager.has_var_type(var, DictVariable.__name__)
            ):
                continue
            preprocessed = self.preprocess_variable(valuations, var, current_vars)
            preprocessed_something |= preprocessed
            if preprocessed:
                eval_order.append(var)

        vals_after_ensures = self.check_ensures(valuations)
        valuations.update(vals_after_ensures)

        if preprocessed_something:
            self.infer_domain(valuations, eval_order)

    def preprocess_variable(self, valuations: dict[Symbol, set[Any]], var: Symbol, current_vars: set[Symbol]) -> bool:
        """
        Preprocess a single variable to calculate its possible domain.

        Args:
            valuations: Current valuations of variables.
            var: The variable symbol to preprocess.
            current_vars: Set of variable symbols that can contain the dependencies of the variable being preprocessed.

        Returns:
            bool: True if the variable was preprocessed, False if var does not exist or is already in valuations.
        """
        if var not in self.variable_manager:
            return False

        if self.variable_manager.has_var_type(var, EnsureVariable.__name__) or self.variable_manager.has_var_type(
            var, BoolEvaluateVariable.__name__
        ):
            # Ensure variables are not preprocessed here, they are handled in check_ensures
            return False

        deps = list(self.variable_manager.get_dependencies(var))

        possible_values: set[Any] = set()

        if all(dep in current_vars for dep in deps):
            for _var in self.variable_manager[var].values():
                possible_values.update(_var.simple_evaluate(valuations, self.environment))
        else:
            return False

        valuations[var] = possible_values

        return True

    def check_ensures(self, valuations: dict[Symbol, set[Any]]) -> dict[Symbol, set[Any]]:
        """
        Check ensure constraints for all variables and update their possible values.

        Args:
            valuations: Current valuations of variables.

        Returns:
            dict[Symbol, set[Any]]: A dictionary mapping variable symbols to their updated possible values.
        """

        possible_values: dict[Symbol, set[Any]] = {}
        for ensure_var in self.variable_manager.get_variables_by_type(EnsureVariable.__name__):
            ensure_var = cast(EnsureVariable, ensure_var)
            if ensure_var.expression.literal != 1:
                # only ensures that are always active can prune values
                continue

            deps: list[Symbol] = list(ensure_var.vars())

            if not all(dep in valuations for dep in deps):
                continue

            # have to preemptively create the set for a dep
            # in case it has no possible values
            # otherwise, it will not be present in the dict at all
            # and it will not update valuations correctly later on
            for dep in deps:
                possible_values[dep] = set()

            for values in product(*(valuations[dep] for dep in deps)):
                eval_dict = dict(zip(deps, values))
                success = ensure_var.simple_evaluate(eval_dict, self.environment)

                if success:
                    for k, v in eval_dict.items():
                        possible_values.setdefault(k, set()).add(v)

        return possible_values

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

        if self.check_only:
            # Since there are no watches, undo is never called
            # Hence, we undo stuff here
            # This is probably severly inefficient as we re-evaluate everything every time
            # maybe there is a way to do this more efficiently?
            if self.optimization.activate_equal_stage(control.assignment):
                # if we are now in the second stage of optimization,
                # we can now look for equal valued solutions
                print("Now in optimization stage 2, looking for equal or better solutions")

            self.reset_evaluations(0)

            to_evaluate: set[VariableType] = set()
            to_evaluate_expressions: set[VariableValue] = set()
            for var in self.variable_manager.get_variables():
                if var.get_value() == ValueStatus.NOT_SET:
                    # print("var checking in check: ", var)
                    to_evaluate.add(var)

            for expr in self.value_registry.get_all():
                if expr.value == ValueStatus.NOT_SET:
                    to_evaluate_expressions.add(expr)

            backtrack = self.evaluated_solver_assignment(control, to_evaluate, to_evaluate_expressions)

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
        self.check_shared_values(control)
        self.handle_warning_ignore(control)
        backtrack = self.evaluate_model(control)
        if backtrack:
            # backtracking due to brave/cautious model being updated
            return

        # if everything is good, we update the best value
        # TODO: Maybe we have to move this next stuff to the on_model function
        # in case there are multiple propagators?
        best_value_update = self.optimization.update_best_value()
        if best_value_update is not None:
            old_value, new_value = best_value_update
            print(f"New best optimization value found: {new_value} (old: {old_value})")

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
        self.update_python_model()
        assert self.python_model is not None
        model, nogoods, enqueue_now = self.reasoning_mode_handler.process_model(
            self.python_model,
            ctl,
            lambda symbol: self.variable_manager[symbol].values(),
            self.get_reasons,
        )
        self.python_model = model
        self.nogood_queue.extend(nogoods)
        if enqueue_now:
            return self.add_nogoods_from_queue(ctl)
        return False

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
            if not ctl.add_nogood(ng, lock=True):
                return True

        return False

    def check_evaluate(self, ctl: clingo.PropagateControl):
        """
        Evaluate `evaluate` atoms against the current assignments.

        Args:
            ctl: Clingo PropagateControl object.
        """
        for var in self.evaluatevars:
            var.evaluate(self.evaluations, ctl, self.environment)

    def check_shared_values(self, ctl: clingo.PropagateControl):
        """
        Evaluate `evaluate` atoms against the current assignments.

        Args:
            ctl: Clingo PropagateControl object.
        """
        for var in self.shared_values:
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
        # print("Propagating...", changes)
        if self.check_only:
            return

        if self.add_nogoods_from_queue(control):
            # backtracking due to nogoods in queue
            return

        to_evaluate: set[VariableType] = set()
        to_evaluate_expressions: set[VariableValue] = set()
        for rlit in changes:
            self.optimization.activate_equal_stage(control.assignment, rlit)

            to_evaluate.update(self.get_literal2var(rlit))

            to_evaluate_expressions.update(self.get_literal2expr(rlit))

        backtrack = self.evaluated_solver_assignment(control, to_evaluate, to_evaluate_expressions)
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
        extra_literals = self.optimization.evaluate_optimization_sums(ctl)
        if extra_literals is None:
            return False
        self.add_nogood_for_variable(ctl, self.optimization.sums, extra_literals=extra_literals)
        return True

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
        prop_stop = ctl.add_nogood(ng, lock=True)
        if conflict and prop_stop:
            assert False, (
                f"Added violated constraint but solver did not detect it for variable {var} with reasons {ng} and truth values {[ctl.assignment.value(lit) for lit in ng]}"
            )

        return not prop_stop

    def evaluated_solver_assignment(
        self,
        ctl: clingo.PropagateControl,
        to_evaluate: set[VariableType],
        to_evaluate_expressions: set[VariableValue],
    ) -> bool:
        """
        Evaluate a set of variables under the current solver assignment.

        If a variable changes, its parents are scheduled for evaluation.

        Args:
            ctl: Clingo PropagateControl object.
            to_evaluate: Variables that may have been affected by recent changes.
            to_evaluate_expressions: Expressions that may have been affected by recent changes.

        Returns:
            bool: True if propagation should stop (conflict/forbidden warning),
            False otherwise.
        """

        if len(to_evaluate) == 0 and len(to_evaluate_expressions) == 0:
            return False

        eval_by_rank: dict[int, set[VariableType]] = {}
        eval_by_rank_expr: dict[int, set[VariableValue]] = {}
        for v in to_evaluate:
            eval_by_rank.setdefault(self.var_ranks[v.var], set()).add(v)
        for expr in to_evaluate_expressions:
            eval_by_rank_expr.setdefault(self.var_ranks_expr[expr], set()).add(expr)

        rank = 0
        max_rank = max(max(eval_by_rank.keys(), default=0), max(eval_by_rank_expr.keys(), default=0))

        while rank <= max_rank:
            # print("Evaluating rank: ", rank)

            max_rank = self.evaluate_expressions_at_rank(
                ctl,
                rank,
                eval_by_rank_expr,
                eval_by_rank,
                max_rank,
            )

            backtrack, max_rank = self.evaluate_variables_at_rank(
                ctl,
                rank,
                eval_by_rank,
                eval_by_rank_expr,
                max_rank,
            )
            if backtrack:
                return True
            rank += 1

        return False

    def evaluate_expressions_at_rank(
        self,
        ctl: clingo.PropagateControl,
        rank: int,
        eval_by_rank_expr: dict[int, set[VariableValue]],
        eval_by_rank: dict[int, set[VariableType]],
        max_rank: int,
    ) -> int:
        """
        Evaluate expressions at one rank and schedule their eligible owners.

        Args:
            ctl: Clingo PropagateControl object.
            rank: The current rank to evaluate.
            eval_by_rank_expr: Dictionary mapping ranks to sets of expressions to evaluate.
            eval_by_rank: Dictionary mapping ranks to sets of variables to evaluate.
            max_rank: The maximum rank encountered so far.

        Returns:
            int: The updated maximum rank.
        """
        if rank not in eval_by_rank_expr:
            return max_rank

        while eval_by_rank_expr[rank]:
            expr = eval_by_rank_expr[rank].pop()
            if not is_evaluation_possible(expr):
                continue

            expr_result = expr.evaluate(self.evaluations, ctl, self.environment)
            if not expr_result:
                continue

            for var in self.get_expr2var(expr):
                var.expressions_evaluated_counter += 1
                if is_evaluation_possible(var):
                    var_rank = self.var_ranks[var.var]
                    eval_by_rank.setdefault(var_rank, set()).add(var)
                    max_rank = max(max_rank, var_rank)

        return max_rank

    def evaluate_variables_at_rank(
        self,
        ctl: clingo.PropagateControl,
        rank: int,
        eval_by_rank: dict[int, set[VariableType]],
        eval_by_rank_expr: dict[int, set[VariableValue]],
        max_rank: int,
    ) -> tuple[bool, int]:
        """
        Evaluate variables at one rank and schedule their dependent expressions.

        Args:
            ctl: Clingo PropagateControl object.
            rank: The current rank to evaluate.
            eval_by_rank: Dictionary mapping ranks to sets of variables to evaluate.
            eval_by_rank_expr: Dictionary mapping ranks to sets of expressions to evaluate.
            max_rank: The maximum rank encountered so far.

        Returns:
            tuple[bool, int]:
                - True if a conflict was detected and backtracking is needed, False otherwise.
                - The updated maximum rank.
        """
        if rank not in eval_by_rank:
            return False, max_rank

        while eval_by_rank[rank]:
            var = eval_by_rank[rank].pop()
            if not is_evaluation_possible(var):
                continue

            result = self.evaluate_variable(ctl, var)
            if result is None:
                return True, max_rank
            if not result:
                continue

            self.evaluations.add_var_to_evaluations(var)
            for expr in self.var2expr.get(var.var, set()):
                expr.vars_counter += 1
                if is_evaluation_possible(expr):
                    expr_rank = self.var_ranks_expr[expr]
                    eval_by_rank_expr.setdefault(expr_rank, set()).add(expr)
                    max_rank = max(max_rank, expr_rank)

        return False, max_rank

    def evaluate_variable(self, ctl: clingo.PropagateControl, var: VariableType) -> bool | None:
        """
        Evaluate one variable against the current assignment.

        Args:
            ctl: Clingo PropagateControl object.
            var: Variable to evaluate.
            expr_lits: Set of expression literals relevant for the evaluation. Defaults to None.

        Returns:
            bool | None:
                - True if the variable's value changed.
                - False if it did not change.
                - None if evaluation detected a conflict (nogood added).
        """
        eval_result: EvaluationResult = var.evaluate(ctl)

        if eval_result == EvaluationResult.CONFLICT:
            self.add_nogood_for_variable(ctl, var)
            return None
        elif eval_result == EvaluationResult.INFER:
            if self.add_nogood_for_variable(ctl, var, extra_literals=var.infer(), conflict=False):
                return None

        # check if any errors are forbidden
        for _warning in var.get_errors():
            if _warning.id in self.forbidden_warnings:
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
            seen: Set of variables already visited to avoid infinite recursion. Defaults to None.
        Returns:
            set[int]: Set of signed solver literals.
        """
        if seen is None:
            seen = set()
        reasons = var.active_literals
        for dvar in var.vars():
            if dvar not in self.variable_manager:
                continue
            for vartype in self.variable_manager[dvar].values():
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
        self.reset_evaluations(assignment.decision_level)

    def reset_evaluations(self, decision_level: int) -> None:
        """Reset evaluations and dependency counters at or above a decision level.

        Args:
            decision_level: Decision level threshold for resetting expressions,
                variables, and optimization sums.
        """
        for expr in self.value_registry.get_all():
            if expr.reset(decision_level):
                for var in self.get_expr2var(expr):
                    var.expressions_evaluated_counter -= 1

        for var in self.variable_manager.get_variables():
            if var.reset(decision_level):
                self.evaluations.remove_var_from_evaluations(var)
                for expr in self.var2expr.get(var.var, []):
                    expr.vars_counter -= 1

        self.optimization.reset_sums(decision_level)

    def get_solver_identifier(self, ctl: clingo.PropagateInit):
        """
        Initialize the Python evaluation environment using the solver identifier.

        Args:
            ctl: Clingo PropagateInit object.
        """

        for id in myClorm.findInPropagateInit(ctl, internal.Main_solverIdentifiers):
            self.environment = id.id

    def get_optimization_sums(self, ctl: clingo.PropagateInit):
        """
        Load optimization sum declarations from ASP facts into the optimization controller.

        Args:
            ctl: Clingo PropagateInit object.
        """

        maxSums = myClorm.findInPropagateInit(ctl, prop_atom.Propagator_optimize_maximizeSum)

        for (expr, symbol, priority, _), literal in maxSums.items():
            value = self.get_variable_value(expr, literal)
            self.add_watch(literal)
            self.add_watch(-literal)
            self.optimization.add_value(symbol, value, priority)

        self.optimization.initialize_best_value()

    def get_forbidden_warnings(self, ctl: clingo.PropagateInit) -> None:
        """
        Load `warning_forbid` atoms.

        Args:
            ctl: Clingo propagation initializer.
        """

        forbidden_warnings = myClorm.findInPropagateInit(ctl, prop_atom.Propagator_warning_forbid)
        ignored_warnings = myClorm.findInPropagateInit(ctl, prop_atom.Propagator_warning_ignore)

        for (error, name), literal in forbidden_warnings.items():
            self.forbidden_warnings[error] = literal

        for (error, name), literal in ignored_warnings.items():
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

        for var in self.variable_manager.get_variables():
            for symbol_var in var.vars():
                if symbol_var == var.var:
                    # don't add self as parent
                    # for self referencing variables
                    continue
                if symbol_var not in self.variable_manager:
                    continue

                for dvar in self.variable_manager[symbol_var].values():
                    dvar.parents.append(var)

        for var in self.variable_manager.get_variables():
            if var.name == OTHER_ENGINE_VAR_NAME and var.parents == []:
                useless_other_engine_vars.append(var)

        for var in useless_other_engine_vars:
            # Variable is an compile/ground engine variable with no parents, removing it since it is useless for us
            self.variable_manager.delete_variable(var.var)

            # Now we delete this variable from the literal2var mapping
            for lit in var.literals:
                self.delete_literal2var(lit, var)
            for expr in var.expressions:
                for lit in expr.literals:
                    # Might already be removed if the literal is shared with another expression.
                    self.delete_literal2var(lit, var)
                owners = self.get_expr2var(expr)
                if var in owners:
                    owners.remove(var)

    def update_python_model(self):
        """
        Build the python-side model representation from current variable values.

        Populates `self.python_model` with result atoms (values, sets, multimaps,
        evaluated atoms) and warning atoms. This is used by `on_model` to extend
        the clingo model and by brave/cautious reasoning to accumulate results.
        """
        errors = []
        if self.optimization.enabled:
            errors.extend(self.optimization.get_errors())
        errors.extend(self.errors)
        self.python_model = ModelBuilder(self.ignored_warnings).build(
            self.variable_manager.get_variables(), self.evaluatevars, errors
        )

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

        self.add_shared_values(model)
        if self.optimization.record_model(model):
            # Stop search once the requested number of optimal models is found.
            model.context.add_clause([])

    def add_shared_values(self, model: clingo.Model):
        """
        Add optimization value atoms for optimization sums to the model.
        This uses the post_processor.py "_extend_optimize_values" function.

        Args:
            model: Clingo model to extend.
        """
        assert self.python_model is not None

        for shared_value in self.shared_values:
            val, errors = evaluator.reducedExpr(shared_value.value)
            clAtom = myClorm.pytocl(internal._shared_value(shared_value.expr, val))
            if not model.contains(clAtom):
                model.extend([clAtom])
