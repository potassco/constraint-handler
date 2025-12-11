from __future__ import annotations

from typing import Any, Dict, NamedTuple, Sequence

import clingo

import constraint_handler.evaluator as evaluator
import constraint_handler.myClorm as myClorm
from constraint_handler.PropagatorConstants import (
    DEBUG_PRINT,
    ENSURE_VAR_NAME,
    EXECUTION_OUTPUT,
    EvaluationResult,
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

# VariableType = Variable | SetVariable | DictVariable | Execution


def myprint(*args, **kwargs):
    if DEBUG_PRINT:
        print(*args, **kwargs)


class Evaluated(NamedTuple):
    name: evaluator.Operator
    expr: list[evaluator.Expr]
    type_: evaluator.BaseType | None
    value: bool | int | float | str | clingo.Symbol


class ConstraintHandlerPropagator(clingo.Propagator):

    def __init__(self, check_only: bool = False):
        self.symbol2var: Dict[clingo.Symbol, VariableType] = {}
        self.literal2var: Dict[int, list[VariableType]] = {}

        self.evaluatevars: list[EvaluateVariable] = []

        self.optimization_sum: OptimizationSum = OptimizationSum()
        self.best_value: int | float = -1
        self.using_optimization: bool = False

        self.environment: Dict[Any, Any] = {}

        self.check_only = check_only

        self.errors: list[Exception] = []

    def init(self, ctl: clingo.PropagateInit):
        if self.check_only:
            self.propagate = lambda ctl, changes: None

        self.get_solver_identifier(ctl)

        self.get_variables(ctl)
        self.get_assign(ctl)
        self.get_ensure(ctl)
        self.get_set_declarations(ctl)
        self.get_multimap_declarations(ctl)
        self.get_optimization_sums(ctl)
        self.get_execution_declarations(ctl)
        self.set_parents()

        self.get_evaluate(ctl)

        myprint("INIT DONE")
        myprint("#" * 50)

    def check(self, ctl: clingo.PropagateControl):
        """
        This method is called to check the constraints in the propagator.
        It evaluates all variables in case there were changes from the last propagation call.
        It then evaluates the optimization sums.
        If a variable evaluation has a conflict, any ensure constraint is violated
        or the optimization value if below the best it adds a nogood and backtracks.
        """
        myprint("CHECKING")

        backtrack = self.evaluated_solver_assignment(ctl, set(self.symbol2var.values()))

        if backtrack:
            myprint(f"backtracking {backtrack} due to conflicts in evaluation of variables")
            return

        myprint(f"Evaluated assignments: {make_dict_from_variables(self.symbol2var.values())}")

        # If not backtracking, check optimization sums
        backtrack = self.evaluate_optimization_sum(ctl)
        myprint(f"Optimization sum evaluated to {self.optimization_sum.value}")
        if backtrack:
            print(f"backtracking {backtrack} due to optimization sum being worse than best value {self.best_value}")
            return

        self.check_evaluate(ctl)
        # if everything is good, we update the best value
        if self.using_optimization and self.optimization_sum.value > self.best_value:
            myprint(f"New best optimization value found: {self.optimization_sum.value} (old: {self.best_value})")
            self.best_value = self.optimization_sum.value

        myprint("CHECK DONE!")

    def check_evaluate(self, ctl: clingo.PropagateControl):
        myprint("Checking evaluate atoms")
        myprint(f"Evaluated assignments before evaluate: {make_dict_from_variables(self.symbol2var.values())}")
        for var in self.evaluatevars:
            var.evaluate(make_dict_from_variables(self.symbol2var.values()), ctl, self.environment)

    def propagate(self, ctl: clingo.PropagateControl, changes: Sequence[int]) -> None:
        """
        This method is called to propagate the constraints in the propagator.
        It evaluates the expressions assigned to variables and checks the ensures.
        If a variable evaluation has a conflict, any ensure constraint is violated
        or the optimization value if below the best and has been completely assigned
        it adds a nogood and backtracks.
        """
        myprint(f"PROPAGATING with changes: {changes} and decision level {ctl.assignment.decision_level}")
        to_evaluate: set[VariableType] = set()
        for rlit in changes:
            lit = abs(rlit)
            if lit in self.literal2var:
                to_evaluate.update(self.literal2var[lit])

        backtrack = self.evaluated_solver_assignment(ctl, to_evaluate)
        if backtrack:
            myprint(f"PROPAGATION DONE, backtracking {backtrack} due to conflicts in evaluation of variables")
            return

        myprint(f"Evaluated assignments: {make_dict_from_variables(self.symbol2var.values())}")

        # If not backtracking, check optimization sums
        self.evaluate_optimization_sum(ctl)
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
            if self.optimization_sum.value <= self.best_value and not self.optimization_sum.has_unassigned():
                ng = set()
                for symbol_var in self.optimization_sum.vars():
                    var = self.symbol2var[symbol_var]
                    ng = ng.union(self.get_reasons(var))
                # ng = (l for l in ng if l < 0)  # only keep negative literals
                myprint(f"Adding nogood {list(ng)} to enforce optimization")
                if ctl.add_nogood(ng):
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
                assert (
                    False
                ), f"Added violated constraint but solver did not detect it for variable {var} with reasons {ng}"
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
        var_declares = myClorm.findInPropagateInit(ctl, evaluator.Propagator_variable_declare)
        var_defines = myClorm.findInPropagateInit(ctl, evaluator.Propagator_variable_define)
        var_domains = myClorm.findInPropagateInit(ctl, evaluator.Propagator_variable_domain)
        var_optionals = myClorm.findInPropagateInit(ctl, evaluator.Propagator_variable_declareOptional)
        for (name, symbol_var, domain), __literal in var_declares.items():
            variable: Variable = Variable(name, symbol_var)
            self.symbol2var[symbol_var] = variable

            self.errors.append(SyntaxError(f"Variable {name} declaration is not a fact!"))

            if isinstance(domain, evaluator.BoolDomain):
                literal_true = ctl.add_literal(freeze=True)
                literal_false = ctl.add_literal(freeze=True)
                variable.add_value(evaluator.Val(bool, True), literal_true)
                variable.add_value(evaluator.Val(bool, False), literal_false)
                ctl.add_watch(literal_true)
                ctl.add_watch(-literal_true)
                ctl.add_watch(literal_false)
                ctl.add_watch(-literal_false)

            elif isinstance(domain, evaluator.FromList):
                for expr in domain.elements:
                    literal = ctl.add_literal(freeze=True)
                    variable.add_value(expr, literal)
                    ctl.add_watch(literal)
                    ctl.add_watch(-literal)
            elif isinstance(domain, evaluator.FromFacts):
                # values will be added from facts, nothing to do here
                pass
            else:
                self.errors.append(ValueError(f"Unknown domain type {domain} for variable {name}"))

        for (name, symbol_var, expr), __literal in var_defines.items():
            if symbol_var in self.symbol2var:
                self.errors.append(SyntaxError(f"Variable {name} declared and defined! variable_define will do nothing!"))
                continue
            variable: Variable = Variable(name, symbol_var)
            self.symbol2var[symbol_var] = variable
            variable.add_value(expr, __literal)
            ctl.add_watch(__literal)
            ctl.add_watch(-__literal)

        for (symbol_var, domain_expr), __literal in var_domains.items():
            variable: Variable = self.symbol2var[symbol_var]
            literal = ctl.add_literal(freeze=True)
            variable.add_value(domain_expr, literal)
            ctl.add_watch(literal)
            ctl.add_watch(-literal)

        for (optional,), __literal in var_optionals.items():
            variable: Variable = self.symbol2var[optional]
            literal = ctl.add_literal(freeze=True)
            variable.add_value(evaluator.Val(type(None), None), literal)
            ctl.add_watch(literal)
            ctl.add_watch(-literal)

        # check that all variables have a domain
        for var in self.symbol2var.values():
            if not var.has_domain():
                self.errors.append(ValueError(f"Variable {var} has no domain defined!"))

    def get_assign(self, ctl: clingo.PropagateInit):
        """
        This method initializes the variables from the ASP encoding.
        It reads the propagator_assign atoms and creates Variable instances.
        """

        assigns = myClorm.findInPropagateInit(ctl, evaluator.Propagator_assign)
        for (name, symbol_var, expr), literal in assigns.items():
            if symbol_var in self.symbol2var:
                variable: Variable = self.symbol2var[symbol_var]
            else:
                variable: Variable = Variable(name, symbol_var)
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

        ensures = myClorm.findInPropagateInit(ctl, evaluator.Propagator_ensure)
        c = 0
        for (name, expr), literal in ensures.items():
            c += 1
            ensure_var = EnsureVariable(name, expr, literal)
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

        for (op, args), literal in myClorm.findInPropagateInit(ctl, evaluator.Evaluate).items():
            var = EvaluateVariable(op, args, literal)
            if literal != 1:
                self.errors.append(SyntaxError(f"Evaluate atom {op} with args {args} is not a fact!"))
            self.evaluatevars.append(var)

    def get_solver_identifier(self, ctl: clingo.PropagateInit):
        """
        This method initializes the solver identifier from the ASP encoding.
        """

        for id, _ in myClorm.findInPropagateInit(ctl, evaluator.Main_solverIdentifier).items():
            self.environment = evaluator.get_environment(id.id)

    def get_optimization_sums(self, ctl: clingo.PropagateInit):
        """
        This method initializes the optimization sum from the ASP encoding.
        It reads the optimize_maximizeSum atoms and creates an OptimizationSum instance.
        """

        maxSums = myClorm.findInPropagateInit(ctl, evaluator.Propagator_optimize_maximizeSum)
        for (_, expr, symbol), literal in maxSums.items():
            self.using_optimization = True
            self.optimization_sum.add_value(symbol, expr, literal)

    def get_set_declarations(self, ctl: clingo.PropagateInit):
        """
        This method initializes the set variables from the ASP encoding.
        It reads the set_declare and set_assign atoms and creates SetVariable instances.
        """

        declares = myClorm.findInPropagateInit(ctl, evaluator.Propagator_set_declare)
        for (name, symbol_var), literal in declares.items():
            variable = SetVariable(name, symbol_var, literal)
            self.errors.append(SyntaxError(f"Set variable {name} declaration is not a fact!"))

            self.symbol2var[symbol_var] = variable
            if literal not in self.literal2var:
                self.literal2var[literal] = []
            self.literal2var[literal].append(variable)

            ctl.add_watch(literal)
            ctl.add_watch(-literal)

        assigns = myClorm.findInPropagateInit(ctl, evaluator.Propagator_set_assign)
        for (name, symbol_var, expr), literal in assigns.items():
            setvar: SetVariable = self.symbol2var[symbol_var]
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
        declares = myClorm.findInPropagateInit(ctl, evaluator.Propagator_multimap_declare)
        for (name, symbol_var), literal in declares.items():
            variable = DictVariable(name, symbol_var, literal)

            self.errors.append(SyntaxError(f"Dict variable {name} declaration is not a fact!"))

            self.symbol2var[symbol_var] = variable
            if literal not in self.literal2var:
                self.literal2var[literal] = []
            self.literal2var[literal].append(variable)

            ctl.add_watch(literal)
            ctl.add_watch(-literal)

        assigns = myClorm.findInPropagateInit(ctl, evaluator.Propagator_multimap_assign)
        for (name, symbol_var, key_expr, expr), literal in assigns.items():
            dictvar: DictVariable = self.symbol2var[symbol_var]
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
        declares = myClorm.findInPropagateInit(ctl, evaluator.Propagator_execution_declare)
        for (name, symbol_var, stmt, in_v, out_v), literal in declares.items():
            variable = Execution(name, symbol_var, stmt, in_v, out_v)

            self.errors.append(SyntaxError(f"Execution {name} declaration is not a fact!"))

            self.symbol2var[symbol_var] = variable

        exec_runs = myClorm.findInPropagateInit(ctl, evaluator.Propagator_execution_run)
        for (name, symbol_var), literal in exec_runs.items():
            execvar: Execution = self.symbol2var[symbol_var]
            execvar.add_run_literal(literal)
            if literal not in self.literal2var:
                self.literal2var[literal] = []
            self.literal2var[literal].append(execvar)

            ctl.add_watch(literal)
            ctl.add_watch(-literal)

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

    def on_model(self, model: clingo.Model):
        self.handle_on_model_warning(self.errors, model)

        for var in self.symbol2var.values():
            self.handle_on_model_warning(var.get_errors(), model)
            if isinstance(var, EnsureVariable):
                continue
            final_value = var.get_value()
            # myprint(var.var, final_value, type(final_value))
            if final_value is ValueStatus.NOT_SET:
                assert False, f"Variable {var} has no value set in on_model!"

            elif final_value is ValueStatus.ASSIGNMENT_IS_FALSE:
                continue

            elif isinstance(var, Execution):
                for var, value in final_value:
                    if value is ValueStatus.NOT_SET:
                        assert False, f"Execution variable {var} has output with no value set in on_model!"

                    self.handle_on_model_value(var, value, model)
            else:
                self.handle_on_model_value(var.var, final_value, model)

        for var in self.evaluatevars:
            self.handle_on_model_warning(var.get_errors(), model)
            pyAtom = Evaluated(var.op, var.args, evaluator.get_baseType(var.get_value()), var.get_value())
            myprint(f"adding evaluate atom {pyAtom}", end=" ")
            clAtom = myClorm.pytocl(pyAtom)
            myprint(f"= {clAtom}")
            if not model.contains(clAtom):
                model.extend([clAtom])

        if self.using_optimization:
            self.handle_on_model_warning(self.optimization_sum.get_errors(), model)
            print(f"Optimization value: {self.optimization_sum.value}")

    def handle_on_model_value(self, var: clingo.Symbol, final_value: Any, model: clingo.Model):

        if final_value is ValueStatus.NOT_SET:
            assert False, f"Variable {var} has no value set in on_model!"

        if isinstance(final_value, evaluator.constant):
            self.handle_on_model_normal_type(var, final_value, model)

        elif isinstance(final_value, (set, frozenset)):
            self.handle_on_model_set(var, final_value, model)

        elif isinstance(final_value, (dict, evaluator.HashableDict)):
            self.handle_on_model_dict(var, final_value, model)
        else:
            # In here come Variable(Lambda) and others
            myprint(f"Unknown model type {type(final_value)} for variable {var} in on_model!")

    def handle_on_model_set(self, var: clingo.Symbol, final_value: set | frozenset, model: clingo.Model):
        for value in final_value:

            if value is ValueStatus.NOT_SET:
                assert False, f"Set variable {var} has no value set in on_model!"

            pyAtom = evaluator.Set_value(var, evaluator.get_baseType(value), value)
            # myprint(f"adding set atom {pyAtom}", end=" ")
            clAtom = myClorm.pytocl(pyAtom)
            myprint(f"= {clAtom}")
            if not model.contains(clAtom):
                model.extend([clAtom])

    def handle_on_model_dict(self, var: clingo.Symbol, final_value: dict, model: clingo.Model):
        for key, value in final_value.items():

            if value is ValueStatus.NOT_SET:
                assert False, f"Dict variable {var} has key {key} with no value set in on_model!"

            pyAtom = evaluator.Multimap_value(
                var, evaluator.get_baseType(key), key, evaluator.get_baseType(value), value
            )
            # myprint(f"adding multimap atom {pyAtom}", end=" ")
            clAtom = myClorm.pytocl(pyAtom)
            myprint(f"= {clAtom}")
            if not model.contains(clAtom):
                model.extend([clAtom])

    def handle_on_model_normal_type(
        self, var: clingo.Symbol, final_value: bool | int | float | str | clingo.Symbol, model: clingo.Model
    ):
        pyAtom = evaluator.Value(var, evaluator.get_baseType(final_value), final_value)
        # myprint(f"adding atom {pyAtom}", end=" ")
        clAtom = myClorm.pytocl(pyAtom)
        myprint(f"= {clAtom}")

        if not model.contains(clAtom):
            model.extend([clAtom])

    def handle_on_model_warning(self, errors: list[Exception], model: clingo.Model):
        for error in errors:
            atom = evaluator.Warning(clingo.Function("", [clingo.Function(type(error).__name__), clingo.String(str(error))]))
            if not model.contains(myClorm.pytocl(atom)):
                model.extend([myClorm.pytocl(atom)])