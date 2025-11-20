from typing import Any, Dict, NamedTuple, Sequence

import clingo

import constraint_handler.evaluator as evaluator
import constraint_handler.myClorm as myClorm
from constraint_handler.PropagatorConstants import DEBUG_PRINT, ValueStatus
from constraint_handler.PropagatorVariables import (
    DictVariable,
    EvaluateVariable,
    OptimizationSum,
    SetVariable,
    Variable,
    make_dict_from_variables,
)

VariableType = Variable | SetVariable | DictVariable


def myprint(*args, **kwargs):
    if DEBUG_PRINT:
        print(*args, **kwargs)


class Evaluated(NamedTuple):
    name: evaluator.Operator
    expr: list[evaluator.Expr]
    type_: evaluator.BaseType | None
    value: bool | int | float | str | clingo.Symbol


class ConstraintHandlerPropagator:

    def __init__(self, check_only: bool = False):
        self.symbol2var: Dict[clingo.Symbol, VariableType] = {}
        self.literal2var: Dict[int, list[VariableType]] = {}

        self.evaluatevars: list[EvaluateVariable] = []

        self.optimization_sum: OptimizationSum = OptimizationSum()
        self.best_value: int | float = -1
        self.using_optimization: bool = False

        self.ensure_lits: Dict[evaluator.Propagator_ensure, int] = {}

        self.environment: Dict[Any, Any] = {}

        self.check_only = check_only

    def init(self, ctl: clingo.PropagateInit):
        if self.check_only:
            ctl.check_mode = clingo.PropagatorCheckMode.Total

        self.get_solver_identifier(ctl)

        self.ensure_lits = myClorm.findInPropagateInit(ctl, evaluator.Propagator_ensure)
        self.get_assign(ctl)
        self.get_set_declarations(ctl)
        self.get_multimap_declarations(ctl)
        self.get_optimization_sums(ctl)
        self.set_parents()

        self.get_evaluate(ctl)

        myprint("INIT DONE")
        myprint("#" * 50)

    def check(self, ctl: clingo.PropagateControl):
        """
        This method is called to check the constraints in the propagator.
        It evaluates all variables in case there were changes from the last propagation call.
        It then checks the ensure constraints and evaluates the optimization sums.
        If a variable evaluation has a conflict, any ensure constraint is violated
        or the optimization value if below the best it adds a nogood and backtracks.
        """
        myprint("CHECKING")

        backtrack = self.evaluated_solver_assignment(ctl, set(self.symbol2var.values()))

        if backtrack:
            myprint(f"backtracking {backtrack} due to conflicts in evaluation of variables")
            return

        myprint(f"Evaluated assignments: {make_dict_from_variables(self.symbol2var.values())}")
        backtrack = self.check_ensure(ctl, True)
        if backtrack:
            myprint(f"backtracking {backtrack} due to ensures")
            return

        self.check_evaluate(ctl)

        # If not backtracking, check optimization sums
        backtrack = self.evaluate_optimization_sum(ctl)
        myprint(f"Optimization sum evaluated to {self.optimization_sum.value}")
        if backtrack:
            print(f"backtracking {backtrack} due to optimization sum being worse than best value {self.best_value}")
            return

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

    def check_ensure(self, ctl: clingo.PropagateControl, is_total: bool = False) -> bool:
        """
        This method checks the ensure constraints in the propagator.
        It evaluates the expressions and checks if they hold true.
        If any ensure constraint is violated, it adds a nogood and propagates
        """
        for (name, expr), lit in self.ensure_lits.items():
            myprint(f"Checking ensure: {name} := {str(expr)} with literal {lit}")
            evaluated = evaluator.evaluate_expr(
                expr, make_dict_from_variables(self.symbol2var.values()), self.environment
            )

            myprint(f"Ensure constraint {name}: {expr} evaluated to {evaluated}")

            if evaluated is None and not is_total:
                continue

            if not evaluated:
                #  False (or None in total check mode)
                nogood = {lit}.union(*(self.get_reasons(self.symbol2var[dvar]) for dvar in evaluator.collectVars(expr)))
                myprint(
                    f"the reason for {expr} being {evaluated} is {nogood} based on vars in {evaluator.collectVars(expr)}"
                )
                if ctl.add_nogood(list(nogood)):
                    assert False, "Added violated constraint but solver did not detect it"
                return True

        myprint("Ensures checked")
        return False

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

        backtrack = self.check_ensure(ctl)

        if backtrack:
            myprint(f"PROPAGATION DONE, backtracking due to ensures: {backtrack}")
            return

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
        changed, conflict = var.evaluate(make_dict_from_variables(self.symbol2var.values()), ctl, self.environment)
        myprint(f"Variable {var} is changed: {changed}, conflict: {conflict}")

        if conflict:
            myprint(f"Var {var} is in conflict at decision level {var.decision_level}")
            ng = self.get_reasons(var)
            myprint(f"Adding nogood {ng}")
            if ctl.add_nogood(ng):
                assert False, "Added violated constraint but solver did not detect it"
            return None

        return changed

    def get_reasons(self, var: VariableType) -> set[int]:
        # TODO: optimize this in the future?
        reasons = var.literals
        reasons = reasons.union(*(self.symbol2var[dvar].literals for dvar in var.vars()))
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

            variable.evaluate(make_dict_from_variables(self.symbol2var.values()), ctl, self.environment)

    def get_evaluate(self, ctl: clingo.PropagateInit):
        """
        This method initializes the variables from the ASP encoding.
        It reads the propagator_assign atoms and creates Variable instances.
        """

        for (op, args), literal in myClorm.findInPropagateInit(ctl, evaluator.Evaluate).items():
            var = EvaluateVariable(op, args, literal)
            self.evaluatevars.append(var)

    def get_solver_identifier(self, ctl: clingo.PropagateInit):
        """
        This method initializes the solver identifier from the ASP encoding.
        """

        for id, _ in myClorm.findInPropagateInit(ctl, evaluator.Main_solverIdentifier).items():
            self.environment = evaluator.get_environment(id)
            # print("hello",self.environment)

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
        # TODO: this was done by copilot, check if it is correct!

        declares = myClorm.findInPropagateInit(ctl, evaluator.Propagator_multimap_declare)
        for (name, symbol_var), literal in declares.items():
            variable = DictVariable(name, symbol_var, literal)
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

    def set_parents(self):
        """
        Sets the parents of each variable based on the variables they depend on.
        """
        for var in self.symbol2var.values():
            for symbol_var in var.vars():
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

    def on_model(self, model):
        for var in self.symbol2var.values():
            final_value = var.get_value()
            # myprint(var.var, final_value, type(final_value))
            if final_value is ValueStatus.NOT_SET:
                assert False, f"Variable {var} has no value set in on_model!"

            if final_value is ValueStatus.ASSIGNMENT_IS_FALSE:
                continue

            if type(final_value) in (set, frozenset):
                for value in final_value:
                    if value is None or value is ValueStatus.NOT_SET:
                        continue
                    pyAtom = evaluator.Set_value(var.var, evaluator.get_baseType(value), value)
                    # myprint(f"adding set atom {pyAtom}", end=" ")
                    clAtom = myClorm.pytocl(pyAtom)
                    myprint(f"= {clAtom}")
                    if not model.contains(clAtom):
                        model.extend([clAtom])
            elif type(final_value) in (evaluator.HashableDict, dict):
                for key, value in final_value.items():
                    if value is None or value is ValueStatus.NOT_SET:
                        continue

                    pyAtom = evaluator.Multimap_value(
                        var.var, evaluator.get_baseType(key), key, evaluator.get_baseType(value), value
                    )
                    # myprint(f"adding multimap atom {pyAtom}", end=" ")
                    clAtom = myClorm.pytocl(pyAtom)
                    myprint(f"= {clAtom}")
                    if not model.contains(clAtom):
                        model.extend([clAtom])
            else:
                pyAtom = evaluator.Value(var.var, evaluator.get_baseType(final_value), final_value)
                # myprint(f"adding atom {pyAtom}", end=" ")
                clAtom = myClorm.pytocl(pyAtom)
                myprint(f"= {clAtom}")

                if not model.contains(clAtom):
                    model.extend([clAtom])

        for var in self.evaluatevars:
            # if var.value is None or var.value is VALUE_NOT_SET:
            #     continue
            pyAtom = Evaluated(var.op, var.args, evaluator.get_baseType(var.get_value()), var.get_value())
            # myprint(f"adding evaluate atom {pyAtom}", end=" ")
            clAtom = myClorm.pytocl(pyAtom)
            myprint(f"= {clAtom}")
            if not model.contains(clAtom):
                model.extend([clAtom])

        if self.using_optimization:
            print(f"Optimization value: {self.optimization_sum.value}")
