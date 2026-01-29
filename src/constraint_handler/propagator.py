from __future__ import annotations

import operator
from typing import Any, Callable, Iterable, Literal, Sequence, cast

import clingo

import constraint_handler.evaluator as evaluator
import constraint_handler.multimap as multimap
import constraint_handler.myClorm as myClorm
import constraint_handler.schemas.atom as atom
import constraint_handler.schemas.expression as expression
from constraint_handler.PropagatorConstants import (
    DEBUG_PRINT,
    ENSURE_VAR_NAME,
    EXECUTION_OUTPUT,
    REASONING_MODE_PROGRAM,
    REASONING_STAGE_ATOM,
    EmptyDomain,
    EvaluationResult,
    MultipleDeclarations,
    MultipleDefinitions,
    NoValueSet,
    ReasoningMode,
    Undeclared,
    ValueStatus,
)
from constraint_handler.PropagatorVariables import (
    DictVariable,
    EnsureVariable,
    EvaluateVariable,
    Execution,
    OptimizationSum,
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

        self.optimization_sum: OptimizationSum = OptimizationSum()
        self.best_value: int | float = -1
        self.using_optimization: bool = False
        self.optimization_check_func: Callable[[int | float, int | float], bool]
        self.set_optimization_check_strength("le")

        self.environment: dict[Any, Any] = {}

        self.check_only = check_only

        self.errors: list[Exception] = []

        self.reasoning_mode: ReasoningMode = ReasoningMode.STANDARD
        self.reasoning_mode_stage_lits: dict[int, int] = {1: -1, 2: -1}
        self.reasoning_stage: Literal[0, 1, 2] = 0
        # this is used for cautious reasoning
        # for the first model, the set is assigned the first model
        # This is will hold the model which is then used to update the result
        self.python_model: set[atom.ResultAtom] | None = None
        self.variable_lits: dict[VariableType, int] = {}
        self.nogood_queue: list[Iterable[int]] = []
        self.previously_stage_2: bool = False

        self.first_decision_level: int = -1

        self.forbidden_warnings: list[str] = []

    def get_configuration(self, ctl: clingo.Control):
        match ctl.configuration.solve.enum_mode:  # ty:ignore[possibly-missing-attribute]
            case "brave":
                self.reasoning_mode = ReasoningMode.BRAVE
            case "cautious":
                self.reasoning_mode = ReasoningMode.CAUTIOUS
            case _:
                self.reasoning_mode = ReasoningMode.STANDARD

        if self.reasoning_mode != ReasoningMode.STANDARD:
            ctl.configuration.solver.heuristic = "Domain"  # ty:ignore[invalid-assignment]
            ctl.add("base", [], REASONING_MODE_PROGRAM)

        print(f"Propagator reasoning mode set to {self.reasoning_mode}")

    def init(self, init: clingo.PropagateInit) -> None:
        self.symbol2var.clear()
        self.literal2var.clear()
        self.evaluatevars.clear()
        self.optimization_sum = OptimizationSum()
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
            # self.reasoning_mode_stage_lits[1] = ctl.add_literal(freeze=True)
            # self.reasoning_mode_stage_lits[2] = ctl.add_literal(freeze=True)
            # ctl.add_watch(self.reasoning_mode_stage_lits[1])
            # ctl.add_watch(self.reasoning_mode_stage_lits[2])
            # ctl.add_watch(-self.reasoning_mode_stage_lits[1])
            # ctl.add_watch(-self.reasoning_mode_stage_lits[2])
            # ctl.add_clause([-self.reasoning_mode_stage_lits[1], -self.reasoning_mode_stage_lits[2]])
            # ctl.add_clause([self.reasoning_mode_stage_lits[1], self.reasoning_mode_stage_lits[2]])

        for var in self.symbol2var.values():
            lit = ctl.add_literal(freeze=True)
            self.variable_lits[var] = lit

    # def decide(self, thread_id: int, assignment: clingo.Assignment, fallback: int) -> int:
    #     """
    #     This method is called to decide on literals in the propagator.
    #     When we are in brave or cautious mode, we make a special decision on decision level 1.
    #     we first decide on the first stage literal to be true.
    #     the second time we decide on the second stage literal to be true.
    #     """
    #     if self.first_decision_level == -1:
    #         self.first_decision_level = assignment.decision_level
    #     if self.reasoning_mode != ReasoningMode.STANDARD and self.first_decision_level == assignment.decision_level:
    #         if self.reasoning_stage == 0:
    #             assert not assignment.is_true(self.reasoning_mode_stage_lits[1])
    #             print("Deciding first stage literal for brave/cautious reasoning", self.reasoning_mode_stage_lits[1])
    #             self.reasoning_stage = 1
    #             return self.reasoning_mode_stage_lits[1]
    #         elif self.reasoning_stage == 1:
    #             assert not assignment.is_true(self.reasoning_mode_stage_lits[2])
    #             print("Deciding second stage literal for brave/cautious reasoning", self.reasoning_mode_stage_lits[2])
    #             self.reasoning_stage = 2
    #             return self.reasoning_mode_stage_lits[2]
    #     return fallback

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

    def set_optimization_best_value(self, value: int | float) -> None:
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
        myprint(f"Optimization sum evaluated to {self.optimization_sum.value}")
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
        if self.using_optimization and self.optimization_sum.value > self.best_value:
            print(f"New best optimization value found: {self.optimization_sum.value} (old: {self.best_value})")
            self.best_value = self.optimization_sum.value

    def evaluate_model(self, ctl: clingo.PropagateControl) -> bool:
        old_model = self.python_model
        self.update_python_model()

        if self.reasoning_mode == ReasoningMode.STANDARD:
            return False

        # This part onwards is only for brave/cautious reasoning
        print(f"old model: {old_model}\nnew model: {self.python_model}")
        assert type(self.python_model) is set
        if old_model is not None:
            if self.reasoning_mode == ReasoningMode.CAUTIOUS:
                self.python_model = old_model.intersection(self.python_model)
            if self.reasoning_mode == ReasoningMode.BRAVE:
                self.python_model = old_model.union(self.python_model)

            print(f"dif model: {self.python_model.difference(old_model)}")

        if not ctl.assignment.is_true(self.reasoning_mode_stage_lits[2]):
            return False

        assert ctl.assignment.is_true(self.reasoning_mode_stage_lits[2]), "stage 2 should be true!"

        if not self.previously_stage_2:
            # First time in stage 2
            self.previously_stage_2 = True

            # add nogoods for the stuff in the current model
            self.nogood_queue.extend(self.get_reasoning_mode_nogoods(self.python_model))

            # add nogoods to ensure at least 1 var changes
            self.nogood_queue.append([-lit for lit in self.variable_lits.values()])

            return self.add_nogoods_from_queue(ctl)

        elif self.previously_stage_2:
            # Subsequent times in stage 2
            assert old_model is not None

            # add nogoods for the new stuff
            self.nogood_queue.extend(self.get_reasoning_mode_nogoods(self.python_model.difference(old_model)))

            return self.add_nogoods_from_queue(ctl)

        assert False, "should never get here?"

    def get_reasoning_mode_nogoods(self, variables: set[atom.ResultAtom]) -> list[Iterable[int]]:
        nogoods: list[Iterable[int]] = []
        for result_var in variables:
            if isinstance(result_var, atom.Evaluated):
                continue
            assert type(result_var) in (atom.Value, atom.Set_value, atom.Multimap_value)
            assert isinstance(result_var.name, clingo.Symbol)

            var: VariableType = self.symbol2var[result_var.name]
            ng = self.get_reasons(var).union({self.variable_lits[var]})
            nogoods.append(ng)

        return nogoods

    def add_nogoods_from_queue(self, ctl: clingo.PropagateControl) -> bool:
        """
        Add nogoods from queue until propagation must be stopped or queue is empty.
        returns True if propagation must be stopped
        """
        while len(self.nogood_queue) > 0:
            ng = self.nogood_queue.pop(0)
            print(f"Adding nogood from queue: {ng}")
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
        myprint(f"Optimization sum evaluated to {self.optimization_sum.value}")

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

        self.optimization_sum.evaluate(make_dict_from_variables(self.symbol2var.values()), ctl, self.environment)

        if self.optimization_sum.value != ValueStatus.NOT_SET:
            if (
                self.optimization_check_func(self.optimization_sum.value, self.best_value)
                and not self.optimization_sum.has_unassigned()
            ):
                ng: set[int] = set()
                for symbol_var in self.optimization_sum.vars():
                    var = self.symbol2var[symbol_var]
                    ng = ng.union(self.get_reasons(var))
                # ng = (l for l in ng if l < 0)  # only keep negative literals
                myprint(f"Adding nogood {list(ng)} to enforce optimization")
                if ctl.add_nogood(ng, tag=True):
                    assert False, "Added violated constraint but solver did not detect it"
                return True

        return False

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
        eval_result = var.evaluate(make_dict_from_variables(self.symbol2var.values()), ctl, self.environment)
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
        for warning in var.get_errors():
            if type(warning).__name__.lower() in self.forbidden_warnings:
                myprint(f"Forbidden warning {type(warning).__name__} exists, making program unsat!")
                ng = self.get_reasons(var)
                myprint(f"Adding nogood {ng}")
                if ctl.add_nogood(ng):
                    assert False, (
                        f"Added violated constraint but solver did not detect it for variable {var} with reasons {ng}",
                    )
                    return None

        return eval_result == EvaluationResult.CHANGED

    def get_reasons(self, var: VariableType) -> set[int]:
        # TODO: optimize this in the future?
        # This might get the reasons from the same variable multiple times
        # maybe some caching would help here, but we have to reset the caching every time...
        # might not be worth it
        reasons = var.literals
        for dvar in var.vars():
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
        for (name, symbol_var, domain), __literal in var_declares.items():
            variable: Variable = Variable(name, symbol_var)

            if symbol_var in self.symbol2var:
                self.errors.append(MultipleDeclarations(f"Variable '{symbol_var}' declared multiple times!"))

            self.symbol2var[symbol_var] = variable

            if __literal != 1:
                self.errors.append(SyntaxError(f"Variable '{symbol_var}' declaration is not a fact!"))

            if isinstance(domain, atom.BoolDomain):
                literal_true = ctl.add_literal(freeze=True)
                literal_false = ctl.add_literal(freeze=True)
                variable.add_value(expression.Val(atom.BaseType.bool, True), literal_true)
                variable.add_value(expression.Val(atom.BaseType.bool, False), literal_false)
                ctl.add_watch(literal_true)
                ctl.add_watch(-literal_true)
                ctl.add_watch(literal_false)
                ctl.add_watch(-literal_false)

            elif isinstance(domain, atom.FromList):
                for expr in domain.elements:
                    literal = ctl.add_literal(freeze=True)
                    variable.add_value(expr, literal)
                    ctl.add_watch(literal)
                    ctl.add_watch(-literal)

            elif isinstance(domain, atom.FromFacts):
                # values will be added from facts, nothing to do here
                pass
            else:
                self.errors.append(ValueError(f"Unknown domain type '{domain}' for variable '{symbol_var}'"))

        for (name, symbol_var, expr), __literal in var_defines.items():
            if symbol_var in self.symbol2var:
                self.errors.append(MultipleDefinitions(f"Variable '{symbol_var}' has multiple definitions!"))
                continue
            define_variable = Variable(name, symbol_var)
            self.symbol2var[symbol_var] = define_variable
            define_variable.add_value(expr, __literal)
            ctl.add_watch(__literal)
            ctl.add_watch(-__literal)

        for (symbol_var, domain_expr), __literal in var_domains.items():
            if symbol_var not in self.symbol2var:
                self.errors.append(Undeclared(f"Variable '{symbol_var}' domain set but variable not declared!"))
                continue
            domain_variable: Variable = cast(Variable, self.symbol2var[symbol_var])
            literal = ctl.add_literal(freeze=True)
            domain_variable.add_value(domain_expr, literal)
            ctl.add_watch(literal)
            ctl.add_watch(-literal)

        for (optional,), __literal in var_optionals.items():
            optional_variable: Variable = cast(Variable, self.symbol2var[optional])
            literal = ctl.add_literal(freeze=True)
            optional_variable.add_value(expression.Val(atom.BaseType.none, None), literal)
            ctl.add_watch(literal)
            ctl.add_watch(-literal)

        # check that all variables have a domain
        for var in self.symbol2var.values():
            if not var.has_domain():
                self.errors.append(EmptyDomain(f"Variable '{var}' has no domain defined!"))

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

            variable.add_value(expr, literal)
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
        It reads the propagator_assign atoms and creates Variable instances.
        """

        for (op, args), literal in myClorm.findInPropagateInit(ctl, atom.Propagator_evaluate).items():
            var = EvaluateVariable(op, args, literal)
            if literal != 1:
                self.errors.append(SyntaxError(f"Evaluate atom {op} with args {args} is not a fact!"))
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
        for (_, expr, symbol), literal in maxSums.items():
            self.using_optimization = True
            self.optimization_sum.add_value(symbol, expr, literal)

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
                    SyntaxError(f"Set variable {name} declaration is not a fact! It has literal {literal}.")
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
                    SyntaxError(f"Dict variable {symbol_var} declaration is not a fact! It has literal {literal}.")
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
            variable = Execution(name, symbol_var, stmt, in_v, out_v)

            if literal != 1:
                self.errors.append(SyntaxError(f"Execution {name} declaration is not a fact!"))

            self.symbol2var[symbol_var] = variable

        exec_runs = myClorm.findInPropagateInit(ctl, atom.Propagator_execution_run)
        for (name, symbol_var), literal in exec_runs.items():
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

        forbidden_warnings = myClorm.findInPropagateInit(ctl, atom.Propagator_forbid_warning)
        for (name, warning), literal in forbidden_warnings.items():
            self.forbidden_warnings.append(str(warning).lower())

        # If a forbidden warning exists already, add empty constraint to make the program unsat
        # Since the warning comes from just reading the input
        for warning in self.errors:
            if type(warning).__name__.lower() in self.forbidden_warnings:
                myprint(f"Forbidden warning {type(warning).__name__} exists, making program unsat!")
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
                self.errors.append(NoValueSet(f"Variable {var} has no value set in on_model!"))
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
            print(eval_var, eval_var.get_value())
            self.handle_on_model_warning(eval_var.get_errors())
            pyAtom = atom.Evaluated(
                eval_var.op, eval_var.args, evaluator.get_baseType(eval_var.get_value()), eval_var.get_value()
            )
            self.python_model.add(pyAtom)

        if self.using_optimization:
            self.handle_on_model_warning(self.optimization_sum.get_errors())
            print(f"Optimization value: {self.optimization_sum.value}")

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

        if isinstance(final_value, atom.constant):
            self.handle_on_model_normal_type(var, final_value)

        elif isinstance(final_value, (set, frozenset)):
            self.handle_on_model_set(var, final_value)

        elif isinstance(final_value, (dict, multimap.HashableDict)):
            self.handle_on_model_dict(var, final_value)
        else:
            # In here come Variable(Lambda) and others
            myprint(f"Unknown model type {type(final_value)} for variable {var} in on_model!")

    def handle_on_model_set(self, var: clingo.Symbol, final_value: set | frozenset):
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
        # TODO: If we want to use the ref system for the output here(for sets, etc) then
        # we have to loop over the expressions in the dict, not just the final values
        # otherwise, we don't know what the ref is for each key and value
        # alternatively, we have a separate part of the dict that tells you which refs are for which key/value

        # TODO: Type for dict is not handled here which results in a none value being output for the type in the value atom
        pyVal = expression.Val(
            evaluator.get_baseType(final_value), clingo.Function("ref", [clingo.Function("variable", [var])])
        )
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
        pyVal = expression.Val(evaluator.get_baseType(final_value), final_value)
        pyAtom = atom.Value(var, pyVal)
        self.python_model.add(pyAtom)

    def handle_on_model_warning(self, errors: list[Exception]):
        for error in errors:
            atom_ = atom.Warning1(
                clingo.Function("", [clingo.Function(type(error).__name__), clingo.String(str(error))])
            )
            self.python_model.add(atom_)
