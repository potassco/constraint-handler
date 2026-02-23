from __future__ import annotations

import operator
import sys
from typing import Any, Iterable, Literal, Sequence, cast

import clingo

import constraint_handler.evaluator as evaluator
import constraint_handler.multimap as multimap
import constraint_handler.myClorm as myClorm
import constraint_handler.schemas.atom as atom
import constraint_handler.schemas.expression as expression
import constraint_handler.schemas.warning as warning
from constraint_handler.PropagatorConstants import (
    DEBUG_PRINT,
    ENSURE_VAR_NAME,
    EXECUTION_OUTPUT,
    REASONING_MODE_PROGRAM,
    REASONING_STAGE_ATOM,
    EvaluationResult,
    OptimizationStrength,
    ReasoningMode,
    ValueStatus,
    propagator_warning_t,
)
from constraint_handler.PropagatorVariables import (
    DictVariable,
    EnsureVariable,
    EvaluateVariable,
    Execution,
    OptimizationHandler,
    SetVariable,
    Variable,
    VariableType,
    make_dict_from_variables,
)


def myprint(*args, **kwargs):
    if DEBUG_PRINT:
        print(*args, **kwargs)


class ConstraintHandlerPropagator(clingo.Propagator):
    def __init__(self, check_only: bool = False):
        self.symbol2var: dict[clingo.Symbol, VariableType] = {}
        self.literal2var: dict[int, list[VariableType]] = {}

        self.evaluatevars: list[EvaluateVariable] = []

        self.optimization_sum: OptimizationHandler = OptimizationHandler()
        self.best_value: list[int | float] = [-sys.maxsize]
        self.using_optimization: bool = False
        self.optimization_strength: OptimizationStrength = OptimizationStrength.STRICT

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
        self.variable_lits: dict[VariableType, int] = {}
        self.nogood_queue: list[Iterable[int]] = []
        self.previously_stage_2: bool = False

        self.forbidden_warnings: dict[warning.Kind, int] = {}

    def get_configuration(self, ctl: clingo.Control):
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

        myprint(f"Propagator reasoning mode set to {self.reasoning_mode}")

    def init(self, init: clingo.PropagateInit) -> None:
        self.symbol2var.clear()
        self.literal2var.clear()
        self.evaluatevars.clear()
        self.optimization_sum = OptimizationHandler()
        self.environment = {}
        self.errors.clear()

        self.get_solver_identifier(init)

        self.get_variables(init)
        self.get_assign(init)
        self.get_ensure(init)
        self.get_set_declarations(init)
        self.get_multimap_declarations(init)
        self.get_optimization_sums(init)
        self.get_execution_declarations(init)
        self.set_parents()

        self.get_evaluate(init)

        self.add_reasoning_mode_helper_atoms(init)

        self.get_forbidden_warnings(init)

        myprint("INIT DONE")
        myprint("#" * 50)

    def add_reasoning_mode_helper_atoms(self, ctl: clingo.PropagateInit) -> None:
        """
        This method adds helper atoms for brave and cautious reasoning modes.
        An atom marks the stage where we let clingo do the reasoning for variables handled by the solver
        The second atom marks the stage where we evaluate the atoms of the propagator.
        """
        if self.reasoning_mode in (ReasoningMode.BRAVE, ReasoningMode.CAUTIOUS):
            myprint("Adding reasoning mode helper atoms")
            for a in ctl.symbolic_atoms.by_signature(REASONING_STAGE_ATOM, 1):
                if a.symbol.arguments[0].number == 1:
                    self.reasoning_mode_stage_lits[1] = ctl.solver_literal(a.literal)

                elif a.symbol.arguments[0].number == 2:
                    self.reasoning_mode_stage_lits[2] = ctl.solver_literal(a.literal)

                elif a.symbol.arguments[0].number == 3:
                    self.reasoning_mode_stage_lits[3] = ctl.solver_literal(a.literal)

                else:
                    assert False, f"Unknown reasoning stage atom: {a.symbol}"

            for var in self.symbol2var.values():
                if isinstance(var, EnsureVariable):
                    continue
                lit = ctl.add_literal(freeze=True)
                self.variable_lits[var] = lit

    def set_optimization_check_strength(self, strength: Literal["lt", "le"]) -> None:
        """
        This method sets the optimization check strength.
        'lt' means that only better solutions are accepted(i.e. solution with lower sum).
        'le' means that better or equal solutions are accepted(i.e. solution with lower or equal sum).
        """

        assert strength in ("lt", "le"), f"Unknown optimization check strength: {strength}"

        if strength == "lt":
            self.optimization_check_func = operator.lt
        elif strength == "le":
            self.optimization_check_func = operator.le
        else:
            raise ValueError(f"Unknown optimization check strength: {strength}")

    def set_optimization_best_value(self, value: list[int | float]) -> None:
        """
        This method sets the best optimization value.
        """
        self.best_value = value

    def check(self, control: clingo.PropagateControl) -> None:
        """
        This method is called to check the constraints in the propagator.
        It evaluates all variables in case there were changes from the last propagation call.
        It then evaluates the optimization sums.
        If a variable evaluation has a conflict, any ensure constraint is violated
        or the optimization value is below the best it adds a nogood and backtracks.
        """
        myprint("CHECKING")
        if self.add_nogoods_from_queue(control):
            myprint("backtracking due to nogoods in queue")
            return

        backtrack = self.evaluated_solver_assignment(control, set(self.symbol2var.values()))

        if backtrack:
            myprint(f"backtracking {backtrack} due to conflicts in evaluation of variables")
            return

        myprint(f"Evaluated assignments: {make_dict_from_variables(self.symbol2var.values())}")

        # If not backtracking, check optimization sums
        backtrack = self.evaluate_optimization_sum(control)
        myprint(f"Optimization sum evaluated to {self.optimization_sum.get_value()}")
        if backtrack:
            myprint(f"backtracking {backtrack} due to optimization sum being worse than best value {self.best_value}")
            return

        if control.assignment.is_total:
            self.check_total(control)

    def check_total(self, control: clingo.PropagateControl) -> None:
        self.check_evaluate(control)
        backtrack = self.evaluate_model(control)
        myprint(f"Standard/Brave/Cautious model evaluated to {self.python_model}")
        if backtrack:
            myprint(f"backtracking {backtrack} due to brave/cautious model being updated")
            return

        # if everything is good, we update the best value
        # TODO: Maybe we have to move this next stuff to the on_model function
        # in case there are multiple propagators?
        if self.using_optimization and self.optimization_sum.get_value() > self.best_value:
            print(f"New best optimization value found: {self.optimization_sum.get_value()} (old: {self.best_value})")
            self.best_value = self.optimization_sum.get_value()

    def evaluate_model(self, ctl: clingo.PropagateControl) -> bool:
        old_model = self.python_model
        self.update_python_model()

        if self.reasoning_mode == ReasoningMode.STANDARD:
            return False

        # This part onwards is only for brave/cautious reasoning
        myprint(f"old model: {old_model}\nnew model: {self.python_model}")
        assert type(self.python_model) is set
        if old_model is not None:
            if self.reasoning_mode == ReasoningMode.CAUTIOUS:
                self.python_model = old_model.intersection(self.python_model)
            if self.reasoning_mode == ReasoningMode.BRAVE:
                self.python_model = old_model.union(self.python_model)

            myprint(f"dif model: {self.python_model.difference(old_model)}")

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

    def get_reasoning_mode_nogoods(self, variables: set[atom.ResultAtom], first_call) -> list[Iterable[int]]:
        """
        Add nogoods for brave/cautious reasoning mode based on the variables in the model.
        For brave reasoning, we add nogoods to ensure that the next models found contain at least 1 variable with a different value.
        This way we expand the amount of values in the brave model after every model found.

        For Cautious reasoning, on the first call, we add nogoods to ensure that the next models found contain at least 1 variable with a different value.
        Similar to brave reasoning.
        On Subsequent calls, we expect that the variable in the argument is the difference between the old and new model.
        Specifically, the variables which CHANGED.
        For those variables, we add a nogood to disable the change for that variable.
        """
        assert self.reasoning_mode in (ReasoningMode.BRAVE, ReasoningMode.CAUTIOUS)

        nogoods: list[Iterable[int]] = []
        for result_var in variables:
            if isinstance(result_var, atom.Evaluated):
                continue
            assert type(result_var) in (atom.Value, atom.Set_value, atom.Multimap_value)
            assert isinstance(result_var.name, clingo.Symbol)

            if self.reasoning_mode == ReasoningMode.BRAVE or first_call:
                # The first time we add nogoods, it is the same for brave and cautious
                var: VariableType = self.symbol2var[result_var.name]
                ng = self.get_reasons(var).union({self.variable_lits[var]})
                ng.add(self.reasoning_mode_stage_lits[2])
                nogoods.append(ng)

            elif self.reasoning_mode == ReasoningMode.CAUTIOUS and not first_call:
                # Second time for cautious we only add nogoods that disable the changes for the variable
                var: VariableType = self.symbol2var[result_var.name]
                ng = {self.variable_lits[var]}
                ng.add(self.reasoning_mode_stage_lits[2])
                nogoods.append(ng)
            else:
                assert False, "Should not reach here"

        return nogoods

    def add_nogoods_from_queue(self, ctl: clingo.PropagateControl) -> bool:
        """
        Add nogoods from queue until propagation must be stopped or queue is empty.
        returns True if propagation must be stopped
        """
        while len(self.nogood_queue) > 0:
            ng = self.nogood_queue.pop(0)
            if not ctl.add_nogood(ng):
                return True

        return False

    def check_evaluate(self, ctl: clingo.PropagateControl):
        myprint("Checking evaluate atoms")
        myprint(f"Evaluated assignments before evaluate: {make_dict_from_variables(self.symbol2var.values())}")
        for var in self.evaluatevars:
            var.evaluate(make_dict_from_variables(self.symbol2var.values()), ctl, self.environment)

    def propagate(self, control: clingo.PropagateControl, changes: Sequence[int]) -> None:
        """
        This method is called to propagate the constraints in the propagator.
        It evaluates the expressions assigned to variables and checks the ensures.
        If a variable evaluation has a conflict, any ensure constraint is violated
        or the optimization value if below the best and has been completely assigned
        it adds a nogood and backtracks.
        """
        if self.check_only:
            return

        if self.add_nogoods_from_queue(control):
            myprint("backtracking due to nogoods in queue")
            return

        to_evaluate: set[VariableType] = set()
        for rlit in changes:
            lit = abs(rlit)
            if lit in self.literal2var:
                to_evaluate.update(self.literal2var[lit])

        backtrack = self.evaluated_solver_assignment(control, to_evaluate)
        if backtrack:
            myprint(f"PROPAGATION DONE, backtracking {backtrack} due to conflicts in evaluation of variables")
            return

        myprint(f"Evaluated assignments: {make_dict_from_variables(self.symbol2var.values())}")

        # If not backtracking, check optimization sums
        self.evaluate_optimization_sum(control)
        myprint(f"Optimization sum evaluated to {self.optimization_sum.get_value()}")

    def evaluate_optimization_sum(self, ctl: clingo.PropagateControl) -> bool:
        """
        This method evaluates the optimization sum in the propagator.
        It uses the current solver assignment to determine its value.
        If the optimization sum value is worse than the best value and all variables are assigned,
        it adds a nogood to enforce the optimization.
        return True if a backtrack is needed, False otherwise.
        """
        if not self.using_optimization:
            return False

        changed = self.optimization_sum.evaluate(
            make_dict_from_variables(self.symbol2var.values()), ctl, self.environment
        )
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
                    self.add_nogood_for_variable(ctl, self.optimization_sum)
                    return True
                else:
                    # not last priority or lenient mode, keep looking at next priority
                    continue
            elif _sum < self.best_value[i] and not self.optimization_sum.has_unassigned(i):
                # if the value is worse and fully assigned, we can already add a nogood to exclude this solution
                self.add_nogood_for_variable(ctl, self.optimization_sum)
                return True

        return False

    def add_nogood_for_variable(self, ctl: clingo.PropagateControl, var: VariableType | OptimizationHandler) -> None:
        ng: set[int] = set()
        for symbol_var in var.vars():
            v = self.symbol2var[symbol_var]
            ng = ng.union(self.get_reasons(v))
        myprint(f"Adding nogood {list(ng)} for variable {var}")
        if ctl.add_nogood(ng, tag=True):
            assert False, f"Added violated constraint but solver did not detect it for variable {var} with reasons {ng}"

    def evaluated_solver_assignment(self, ctl: clingo.PropagateControl, to_evaluate: set[VariableType]) -> bool:
        """
        This method evaluates the variables given using the current solver assignment.
        If a variable's value changes, it also evaluates its parents.
        Return value should say if a backtrack is needed!
        It returns False if a conflict is detected (No backtracking needed), True otherwise.
        """
        while len(to_evaluate) > 0:
            var = to_evaluate.pop()
            myprint(f"Evaluating variable {var} at decision level {ctl.assignment.decision_level}")

            result = self.evaluate_variable(ctl, var)
            if result is None:
                # variable had issue, stop propagation!
                return True
            elif result:
                # variable changed, evaluate parents
                myprint(f"Variable {var} changed, adding parents to evaluate queue: {var.parents}")
                for parent in var.parents:
                    to_evaluate.add(parent)
        return False

    def evaluate_variable(self, ctl: clingo.PropagateControl, var: VariableType) -> bool | None:
        """
        This method evaluates a variable in the propagator.
        It uses the current solver assignment to determine its value.
        It returns True if the variable's value changed, False if it did not change,
        and None if there was a conflict.
        """
        eval_result: EvaluationResult = var.evaluate(
            make_dict_from_variables(self.symbol2var.values()), ctl, self.environment
        )
        myprint(f"Variable {var} evaluation result: {eval_result}")

        if eval_result == EvaluationResult.CONFLICT:
            myprint(f"Var {var} is in conflict at decision level {var.decision_level}")
            ng = self.get_reasons(var)
            myprint(f"Adding nogood {ng}")
            if ctl.add_nogood(ng):
                assert False, (
                    f"Added violated constraint but solver did not detect it for variable {var} with reasons {ng}",
                )
            return None

        # check if any errors are forbidden
        for __warning in var.get_errors():
            if __warning.id in self.forbidden_warnings:
                literal = self.forbidden_warnings[__warning.id]
                if ctl.assignment.is_true(literal):
                    myprint(f"Forbidden warning {(__warning, literal)} exists, making program unsat!")
                    ng = self.get_reasons(var)
                    myprint(f"Adding nogood {ng}")
                    if ctl.add_nogood(ng):
                        assert False, (
                            f"Added violated constraint but solver did not detect it for variable {var} with reasons {ng}",
                        )
                    return None

        return eval_result == EvaluationResult.CHANGED

    def get_reasons(self, var: VariableType) -> set[int]:
        reasons = var.literals
        for dvar in var.vars():
            if dvar.name == EXECUTION_OUTPUT:
                dvar = dvar.arguments[0]
            reasons = reasons.union(self.get_reasons(self.symbol2var[dvar]))
        myprint(f"Reasons for variable {var}: {reasons}")
        return reasons

    def undo(self, thread_id: int, assignment: clingo.Assignment, changes: Sequence[int]) -> None:
        """
        Resets the evaluations and reasons based on the current assignment.
        """
        myprint(f"UNDOING for decision level {assignment.decision_level} with changes {changes}")
        for var in self.symbol2var.values():
            myprint(
                f"Resetting {var} and its reasons due to decision level {var.decision_level} >= {assignment.decision_level}"
            )
            var.reset(assignment.decision_level)

        self.optimization_sum.reset(assignment.decision_level)

    def get_variables(self, ctl: clingo.PropagateInit):
        """
        This method initializes the variables from the ASP encoding.
        It reads the propagator_variable_declare, propagator_variable_define, propagator_variable_domain
        atoms and creates Variable instances.
        """
        var_declares = myClorm.findInPropagateInit(ctl, atom.Propagator_variable_declare)
        var_defines = myClorm.findInPropagateInit(ctl, atom.Propagator_variable_define)
        var_domains = myClorm.findInPropagateInit(ctl, atom.Propagator_variable_domain)
        var_optionals = myClorm.findInPropagateInit(ctl, atom.Propagator_variable_declareOptional)

        from_facts_literals: dict[symbol_var, int] = {}
        for (name, symbol_var, domain), __literal in var_declares.items():
            if symbol_var not in self.symbol2var:
                variable: Variable = Variable(name, symbol_var)
                self.symbol2var[symbol_var] = variable
            else:
                variable: Variable = cast(Variable, self.symbol2var[symbol_var])

            ctl.add_watch(__literal)
            ctl.add_watch(-__literal)

            if __literal not in self.literal2var:
                self.literal2var[__literal] = []

            self.literal2var[__literal].append(variable)

            if isinstance(domain, atom.BoolDomain):
                literal_true = ctl.add_literal(freeze=True)
                literal_false = ctl.add_literal(freeze=True)
                variable.add_value(
                    expression.Val(expression.BaseType.bool, True),  # ty:ignore[unresolved-attribute]
                    literal_true,
                    __literal,
                )
                variable.add_value(
                    expression.Val(expression.BaseType.bool, False),  # ty:ignore[unresolved-attribute]
                    literal_false,
                    __literal,
                )
                ctl.add_watch(literal_true)
                ctl.add_watch(-literal_true)
                ctl.add_watch(literal_false)
                ctl.add_watch(-literal_false)

                # if the declaration is False, then the value it can give can not be true
                ctl.add_clause([-literal_true, __literal])
                ctl.add_clause([-literal_false, __literal])

                self.literal2var[literal_true] = [variable]
                self.literal2var[literal_false] = [variable]

            elif isinstance(domain, atom.FromList):
                for expr in domain.elements:
                    literal = ctl.add_literal(freeze=True)
                    variable.add_value(expr, literal, __literal)
                    ctl.add_watch(literal)
                    ctl.add_watch(-literal)

                    ctl.add_clause([-literal, __literal])

                    self.literal2var[literal] = [variable]

            elif isinstance(domain, atom.FromFacts):
                # values will be added from facts, nothing to do here
                from_facts_literals[symbol_var] = __literal
            else:
                self.errors.append(
                    warning.Warning(
                        warning.Propagator(),
                        (symbol_var,),
                        f"Unknown domain type '{domain}' for variable '{symbol_var}'",
                    )
                )

        for (name, symbol_var, expr), __literal in var_defines.items():
            if symbol_var in self.symbol2var:
                define_variable: Variable = cast(Variable, self.symbol2var[symbol_var])
            else:
                define_variable = Variable(name, symbol_var)
                self.symbol2var[symbol_var] = define_variable

            define_variable.add_value(expr, __literal, __literal)
            ctl.add_watch(__literal)
            ctl.add_watch(-__literal)

            if __literal not in self.literal2var:
                self.literal2var[__literal] = []
            self.literal2var[__literal].append(define_variable)
            # here we dont add a nogood since its the same literal

        for (symbol_var, domain_expr), __literal in var_domains.items():
            # These values are assgiend the "from_facts" domain literal for the given variable
            if symbol_var not in self.symbol2var:
                self.errors.append(
                    warning.Warning(
                        warning.Variable(warning.VariableWarning.undeclared),  # ty:ignore[unresolved-attribute]
                        (symbol_var,),
                        f"Variable '{symbol_var}' domain set but variable not declared!",
                    )
                )
                continue
            domain_variable: Variable = cast(Variable, self.symbol2var[symbol_var])
            literal = ctl.add_literal(freeze=True)
            domain_literal = from_facts_literals[symbol_var]
            domain_variable.add_value(domain_expr, literal, domain_literal)
            ctl.add_watch(literal)
            ctl.add_watch(-literal)

            ctl.add_clause([-literal, domain_literal])

            self.literal2var[literal] = [domain_variable]

        for (optional,), __literal in var_optionals.items():
            if optional not in self.symbol2var:
                # If the optinal variable is not declared we add a warning, since this is probably not intended
                self.errors.append(
                    warning.Warning(
                        warning.Variable(warning.VariableWarning.undeclared),  # ty:ignore[unresolved-attribute]
                        (optional,),
                        f"Variable '{optional}' declared optional but variable not declared!",
                    )
                )
                continue

            optional_variable: Variable = cast(Variable, self.symbol2var[optional])
            literal = ctl.add_literal(freeze=True)
            optional_variable.add_value(
                expression.Val(expression.BaseType.none, None), literal, __literal
            )  # ty:ignore[unresolved-attribute]
            ctl.add_watch(literal)
            ctl.add_watch(-literal)

            ctl.add_clause([-literal, __literal])

            if __literal not in self.literal2var:
                self.literal2var[__literal] = []
            self.literal2var[__literal].append(optional_variable)
            self.literal2var[literal] = [optional_variable]

        # check that all variables have a domain
        for var in self.symbol2var.values():
            if not var.has_domain():
                self.errors.append(
                    warning.Warning(
                        warning.Variable(warning.VariableWarning.emptyDomain),  # ty:ignore[unresolved-attribute]
                        (var,),
                        f"Variable '{var}' has no domain defined!",
                    )
                )

    def get_assign(self, ctl: clingo.PropagateInit):
        """
        This method initializes the variables from the ASP encoding.
        It reads the propagator_assign atoms and creates Variable instances.
        """

        assigns = myClorm.findInPropagateInit(ctl, atom.Propagator_assign)
        for (name, symbol_var, expr), literal in assigns.items():
            variable: Variable
            if symbol_var in self.symbol2var:
                variable = cast(Variable, self.symbol2var[symbol_var])
            else:
                variable = Variable(name, symbol_var)
                self.symbol2var[symbol_var] = variable

            variable.add_value(expr, literal, literal)
            if literal not in self.literal2var:
                self.literal2var[literal] = []
            self.literal2var[literal].append(variable)

            ctl.add_watch(literal)
            ctl.add_watch(-literal)

    def get_ensure(self, ctl: clingo.PropagateInit):
        """
        This method initializes the ensure constraints from the ASP encoding.
        It reads the propagator_ensure atoms and stores them with their literals.
        """

        ensures = myClorm.findInPropagateInit(ctl, atom.Propagator_ensure)
        c = 0
        for (name, expr), literal in ensures.items():
            c += 1
            ensure_var: EnsureVariable = EnsureVariable(name, expr, literal)
            ctl.add_watch(literal)
            ctl.add_watch(-literal)
            self.literal2var.setdefault(literal, []).append(ensure_var)
            # Var name is given here so it works well with the rest of the system
            # It should do nothing and also should never appear in any assignments!!
            self.symbol2var[clingo.Function(f"{ENSURE_VAR_NAME}{c}")] = ensure_var

    def get_evaluate(self, ctl: clingo.PropagateInit):
        """
        This method initializes the variables from the ASP encoding.
        It reads the evaluate atoms and creates EvaluateVariable instances.
        """

        for (op, args), literal in myClorm.findInPropagateInit(ctl, atom.Propagator_evaluate).items():
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

    def get_solver_identifier(self, ctl: clingo.PropagateInit):
        """
        This method initializes the solver identifier from the ASP encoding.
        """

        for id, _ in myClorm.findInPropagateInit(ctl, atom.Main_solverIdentifier).items():
            self.environment = evaluator.get_environment(id.id)

    def get_optimization_sums(self, ctl: clingo.PropagateInit):
        """
        This method initializes the optimization sum from the ASP encoding.
        It reads the optimize_maximizeSum atoms and creates an OptimizationSum instance.
        """

        maxSums = myClorm.findInPropagateInit(ctl, atom.Propagator_optimize_maximizeSum)
        for (_, expr, symbol, priority), literal in maxSums.items():
            self.using_optimization = True
            self.optimization_sum.add_value(symbol, expr, literal, priority)

        self.best_value = [-sys.maxsize] * self.optimization_sum.get_sum_count()

    def get_set_declarations(self, ctl: clingo.PropagateInit):
        """
        This method initializes the set variables from the ASP encoding.
        It reads the set_declare and set_assign atoms and creates SetVariable instances.
        """

        declares = myClorm.findInPropagateInit(ctl, atom.Propagator_set_declare)
        for (name, symbol_var), literal in declares.items():
            variable = SetVariable(name, symbol_var, literal)
            if literal != 1:
                self.errors.append(
                    warning.Warning(
                        warning.Propagator(),
                        (variable,),
                        f"Set variable {name} declaration is not a fact! It has literal {literal}.",
                    )
                )

            self.symbol2var[symbol_var] = variable
            if literal not in self.literal2var:
                self.literal2var[literal] = []
            self.literal2var[literal].append(variable)

            ctl.add_watch(literal)
            ctl.add_watch(-literal)

        assigns = myClorm.findInPropagateInit(ctl, atom.Propagator_set_assign)
        for (name, symbol_var, expr), literal in assigns.items():
            setvar: SetVariable = cast(SetVariable, self.symbol2var[symbol_var])
            setvar.add_value(expr, literal)
            if literal not in self.literal2var:
                self.literal2var[literal] = []
            self.literal2var[literal].append(setvar)

            ctl.add_watch(literal)
            ctl.add_watch(-literal)

    def get_multimap_declarations(self, ctl: clingo.PropagateInit):
        """
        This method initializes the dict variables from the ASP encoding.
        It reads the multimap_declare and multimap_assign atoms and creates DictVariable instances.
        """
        declares = myClorm.findInPropagateInit(ctl, atom.Propagator_multimap_declare)
        for (name, symbol_var), literal in declares.items():
            variable = DictVariable(name, symbol_var, literal)

            if literal != 1:
                self.errors.append(
                    warning.Warning(
                        warning.Propagator(),
                        (variable,),
                        f"Dict variable {symbol_var} declaration is not a fact! It has literal {literal}.",
                    )
                )

            self.symbol2var[symbol_var] = variable
            if literal not in self.literal2var:
                self.literal2var[literal] = []
            self.literal2var[literal].append(variable)

            ctl.add_watch(literal)
            ctl.add_watch(-literal)

        assigns = myClorm.findInPropagateInit(ctl, atom.Propagator_multimap_assign)
        for (name, symbol_var, key_expr, expr), literal in assigns.items():
            dictvar: DictVariable = cast(DictVariable, self.symbol2var[symbol_var])
            dictvar.add_value(key_expr, expr, literal)
            if literal not in self.literal2var:
                self.literal2var[literal] = []
            self.literal2var[literal].append(dictvar)

            ctl.add_watch(literal)
            ctl.add_watch(-literal)

    def get_execution_declarations(self, ctl: clingo.PropagateInit):
        """
        This method initializes the execution declarations from the ASP encoding.
        It reads the execution_declare and execution_run atoms and creates Execution instances.
        """
        declares = myClorm.findInPropagateInit(ctl, atom.Propagator_execution_declare)
        for (name, symbol_var, stmt, in_v, out_v), literal in declares.items():
            if symbol_var in self.symbol2var:
                variable = cast(Execution, self.symbol2var[symbol_var])
            else:
                variable = Execution(name, symbol_var, in_v, out_v)
                self.symbol2var[symbol_var] = variable

            variable.add_statement(stmt, literal)
            if literal not in self.literal2var:
                self.literal2var[literal] = []
            self.literal2var[literal].append(variable)

            ctl.add_watch(literal)
            ctl.add_watch(-literal)

        exec_runs = myClorm.findInPropagateInit(ctl, atom.Propagator_execution_run)
        for (name, symbol_var), literal in exec_runs.items():
            if symbol_var not in self.symbol2var:
                self.errors.append(
                    warning.Warning(
                        warning.Variable(warning.VariableWarning.undeclared),  # ty:ignore[unresolved-attribute]
                        (symbol_var,),
                        f"Execution variable '{symbol_var}' run exists but variable not declared!",
                    )
                )
                continue
            execvar: Execution = cast(Execution, self.symbol2var[symbol_var])
            execvar.add_run_literal(literal)
            if literal not in self.literal2var:
                self.literal2var[literal] = []
            self.literal2var[literal].append(execvar)

            ctl.add_watch(literal)
            ctl.add_watch(-literal)

    def get_forbidden_warnings(self, ctl) -> None:
        """
        Returns the list of forbidden warnings given by the atoms in the input program.
        """

        forbidden_warnings = myClorm.findInPropagateInit(ctl, warning.Forbid_warning)
        for (name, error), literal in forbidden_warnings.items():
            self.forbidden_warnings[error] = literal

        # If a forbidden warning exists already, add empty constraint to make the program unsat
        # Since the warning comes from just reading the input
        for __warning in self.errors:
            if __warning.id in self.forbidden_warnings:
                literal = self.forbidden_warnings[__warning.id]
                if ctl.assignment.is_true(literal):
                    myprint(f"Forbidden warning {__warning} exists, making program unsat!")
                    ctl.add_clause([])
                    return

    def set_parents(self):
        """
        Sets the parents of each variable based on the variables they depend on.
        """
        for var in self.symbol2var.values():
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
                    myprint(self.symbol2var.keys())
                    myprint(type(symbol_var), symbol_var)
                    continue
                    assert False, f"Variable {symbol_var} not found in symbol2var"
                self.symbol2var[symbol_var].parents.append(var)

    def update_python_model(self):
        self.python_model = set()

        for var in self.symbol2var.values():
            self.handle_on_model_warning(var.get_errors())
            if isinstance(var, EnsureVariable):
                continue
            final_value = var.get_value()
            # myprint(var.var, final_value, type(final_value))
            if final_value is ValueStatus.NOT_SET:
                self.errors.append(
                    warning.Warning(warning.Propagator(), (var,), "Variable has no value set in on_model!")
                )
                continue

            if final_value is ValueStatus.ASSIGNMENT_IS_FALSE:
                continue

            elif isinstance(var, Execution):
                for var, value in final_value:
                    if value is ValueStatus.NOT_SET:
                        assert False, f"Execution variable {var} has output with no value set in on_model!"

                    self.handle_on_model_value(var, value)
            else:
                self.handle_on_model_value(var.var, final_value)

        for eval_var in self.evaluatevars:
            myprint(eval_var, eval_var.get_value())
            self.handle_on_model_warning(eval_var.get_errors())
            pyAtom = atom.Evaluated(
                eval_var.op,
                eval_var.args,
                expression.Val(evaluator.get_baseType(eval_var.get_value()), eval_var.get_value()),
            )
            self.python_model.add(pyAtom)

        if self.using_optimization:
            self.handle_on_model_warning(self.optimization_sum.get_errors())
            myprint(f"Optimization value: {self.optimization_sum.get_value()}")

        self.handle_on_model_warning(self.errors)

    def on_model(self, model: clingo.Model):
        # add to the clingo output the final result based on reasoning mode
        # For brave and cautious, we output the accumulated result (similar to clingo)
        # For standard, we output the current model
        assert self.python_model is not None
        for pyAtom in self.python_model:
            clAtom = myClorm.pytocl(pyAtom)
            myprint(f"adding atom {pyAtom}", end=" ")
            myprint(f"= {clAtom}")
            if not model.contains(clAtom):
                model.extend([clAtom])

    def handle_on_model_value(self, var: clingo.Symbol, final_value: Any):
        if final_value is ValueStatus.NOT_SET:
            assert False, f"Variable {var} has no value set in on_model!"

        if isinstance(final_value, expression.constant):
            self.handle_on_model_normal_type(var, final_value)

        elif isinstance(final_value, (set, frozenset)):
            self.handle_on_model_set(var, final_value)

        elif isinstance(final_value, (dict, multimap.HashableDict)):
            self.handle_on_model_dict(var, final_value)
        else:
            # In here come Variable(Lambda) and others
            myprint(f"Unknown model type {type(final_value)} for variable {var} in on_model!")

    def handle_on_model_set(self, var: clingo.Symbol, final_value: set | frozenset):
        assert self.python_model is not None

        pyVal = expression.Val(
            evaluator.get_baseType(final_value), clingo.Function("ref", [clingo.Function("variable", [var])])
        )
        pyAtom = atom.Value(var, pyVal)
        self.python_model.add(pyAtom)

        for value in final_value:
            if value is ValueStatus.NOT_SET:
                assert False, f"Set variable {var} has no value set in on_model!"

            set_pyVal = expression.Val(evaluator.get_baseType(value), value)
            set_pyAtom = atom.Set_value(var, set_pyVal)
            # myprint(f"adding set atom {pyAtom}", end=" ")
            self.python_model.add(set_pyAtom)

    def handle_on_model_dict(self, var: clingo.Symbol, final_value: dict):
        assert self.python_model is not None

        pyVal = expression.Val(evaluator.get_baseType(final_value), var)
        pyAtom = atom.Value(var, pyVal)
        self.python_model.add(pyAtom)

        for key, value in final_value.items():
            if value is ValueStatus.NOT_SET:
                assert False, f"Dict variable {var} has key {key} with no value set in on_model!"

            for val in value:
                mm_pyKey = expression.Val(evaluator.get_baseType(key), key)
                mm_pyVal = expression.Val(evaluator.get_baseType(val), val)
                mm_pyAtom = atom.Multimap_value(var, mm_pyKey, mm_pyVal)

                self.python_model.add(mm_pyAtom)

    def handle_on_model_normal_type(self, var: clingo.Symbol, final_value: bool | int | float | str | clingo.Symbol):
        assert self.python_model is not None

        pyVal = expression.Val(evaluator.get_baseType(final_value), final_value)
        pyAtom = atom.Value(var, pyVal)
        self.python_model.add(pyAtom)

    def handle_on_model_warning(self, errors: propagator_warning_t):
        assert self.python_model is not None

        for __warning in errors:
            self.python_model.add(__warning)
