import clingo
import constraint_handler.myClorm as myClorm
import constraint_handler.evaluator as evaluator

from collections import defaultdict

from typing import Any, Dict, NamedTuple, List, Sequence, Tuple
from dataclasses import dataclass

import queue

DEBUG_PRINT = False

def myprint(*args, **kwargs):
    if DEBUG_PRINT:
        print(*args, **kwargs)

class ValueNotSet:
    # this represents a value for a literal that has not been set yet
    # or a false literal
    pass

VALUE_NOT_SET = ValueNotSet()

@dataclass
class AtomNames:
    ASSIGN: str = "propagator_assign"
    ENSURE: str = "propagator_ensure"
    EVALUATE: str = "evaluate"
    SET_DECLARE: str = "set_declare"
    SET_ASSIGN: str = "set_assign"


class Value(NamedTuple):
    name: clingo.Symbol
    type_: evaluator.BaseType | None
    value: bool | int | float | str | clingo.Symbol

class Set_Value(NamedTuple):
    name: clingo.Symbol
    type_: evaluator.BaseType | None
    value: bool | int | float | str | clingo.Symbol

class Evaluated(NamedTuple):
    name: evaluator.Operator
    expr: list[evaluator.Expr]
    type_: evaluator.BaseType | None
    value: bool | int | float | str | clingo.Symbol

class EvaluateVariable:

    def __init__(self, op:evaluator.Operator, args: list[evaluator.Expr], literal: int = -1):
        self.op: evaluator.Operator = op
        self.args: list[evaluator.Expr] = args
        self.value: Any = VALUE_NOT_SET
        self.literal: int = literal

    def evaluate(self, evaluations: Dict[clingo.Symbol, Any], ctl: clingo.Control) -> bool:
        """Evaluate the expression and return True if the value has changed."""
        if not ctl.assignment.is_true(self.literal):
            return False
        # print(f"Evaluating {self.op}({self.args})")
        value = evaluator.evaluate_expr(evaluations, evaluator.Operation(self.op, self.args))
        # print(f"Evaluated {self.op}({self.args}) to {value}")
        # if type(value) == set:
        #     if None in value:
        #         # if something in the set is undefined
        #         # we do not assign a value
        #         return False
        #     value = frozenset(value)

        self.value = value
        return True

    def get_value(self) -> Any:
        return self.value

    def __eq__(self, other):
        if not isinstance(other, EvaluateVariable):
            return False
        return self.op == other.op and self.args == other.args and self.literal == other.literal

    def __hash__(self):
        return hash((str(self.op),str(self.args),self.literal))

class VariableValue:

    def __init__(self, expr: evaluator.Expr, lit: int):
        self.expr = expr
        self.value: Any = VALUE_NOT_SET

        self.literal: int = lit
        self.assigned: bool | None = None
        self.decision_level: int = float('inf')

    def evaluate(self, evaluations: Dict[clingo.Symbol, Any], ctl: clingo.Control) -> bool:
        """Evaluate the expression and return True if the value has changed."""
        self.assigned = ctl.assignment.value(self.literal)
        if not ctl.assignment.is_true(self.literal):
            return False
        myprint(f"Evaluating {self.expr}")
        value = evaluator.evaluate_expr(evaluations, self.expr)
        myprint(f"{self.expr} evaluated to {value}")
        if type(value) == set:
            if None in value:
                # if something in the set is undefined
                # we do not assign a value
                return False
            value = frozenset(value)

        if value == self.value:
            return False

        self.decision_level = ctl.assignment.level(self.literal)
        self.value = value
        return True

    def reset(self):
        self.value = VALUE_NOT_SET
        self.decision_level = float('inf')
        self.assigned = None

    def __eq__(self, other):
        if not isinstance(other, VariableValue):
            return False
        return self.expr == other.expr

    def __hash__(self):
        return hash(str(self.expr))

    def __str__(self):
        return f"VariableValue({self.expr}, {self.value})"

class Variable:
    """
        A variable with a name and a value expression.
        This is supposed to mirror the assign/3 atom(also propagator_assign/3) in the ASP encoding.
    """
    def __init__(self, name: str, var: clingo.Symbol):
        self.name = name
        self.var = var
        self.expressions: set[VariableValue] = set()
        self.value: Any = VALUE_NOT_SET
        self.parents: List[Variable | SetVariable] = []

    def add_value(self, expr: evaluator.Expr, lit: int) -> None:
        self.expressions.add(VariableValue(expr, lit))

    @property
    def literals(self) -> set[int]:
        lits = set()
        lits.update({value.literal for value in self.expressions if value.assigned})
        return lits

    def has_unassigned(self) -> bool:
        return any(arg.assigned is None for arg in self.expressions)
    
    def evaluate(self, evaluations: Dict[clingo.Symbol, Any], ctl: clingo.Control) -> tuple[bool, bool]:
        """
        Evaluate the expression and return a tuple (changed, conflict).
        changed is True if the value has changed.
        conflict is True if there is a conflict (multiple values assigned).
        """

        changed = False
        for value in self.expressions:
            changed |= value.evaluate(evaluations, ctl)

        if not changed:
            return False, False

        # if some value changed, we need to discern the new value
        val = set(value.value for value in self.expressions if value.value != VALUE_NOT_SET)
        if len(val) > 1:
            # multiple values assigned to the same variable
            myprint(f"Variable vals: {val}")
            return True, True
        elif len(val) == 0:
            val = None
        elif len(val) == 1:
            if val == self.value:
                # same value as before
                return False, False

        self.value = val.pop()
        return True, False

    def vars(self) -> set[clingo.Symbol]:
        vars = set()
        for value in self.expressions:
            vars.update(evaluator.collectVars(value.expr))
        return vars

    def get_value(self) -> Any:
        return self.value
    
    @property
    def decision_level(self) -> int:
        if self.value is VALUE_NOT_SET:
            return float('inf')
        return min(value.decision_level for value in self.expressions)

    def reset(self):
        self.value = VALUE_NOT_SET
        for value in self.expressions:
            value.reset()

    def __eq__(self, other):
        if not isinstance(other, Variable):
            assert False, "Variable can only be compared to another Variable"
        return self.var == other.var and self.expressions == other.expressions

    def __hash__(self):
        return hash((self.var, frozenset(self.expressions)))

    def __str__(self):
        return f"Variable({self.name}, {self.var})"
    
    def __repr__(self):
        return f"Variable({self.name}, {self.var}, {self.expressions.literal}, {self.expressions.expr})"

class SetVariable:
    """
        A set variable with a name and a set of value expressions.
        This is supposed to mirror the set_declare/2 and set_assign/3 atom in the ASP encoding.
    """
    def __init__(self, name: str, var: clingo.Symbol, lit: int):
        self.name = name
        self.var = var
        self.literals: set[int] = {lit}
        self.values: set[VariableValue] = set()

        self.decision_level: int = float('inf')
        self.parents: List[Variable | SetVariable] = []

    def add_argument(self, arg: evaluator.Expr, lit: int) -> None:
        self.values.add(VariableValue(arg, lit))

    def __contains__(self, item):
        return item in self.values
    
    def get_value(self) -> set[Any]:
        """
        If there is an unassigned value, return None.
        Otherwise return the set of assigned values without the None values.
        """
        if self.has_unassigned():
            return None
        
        return {arg.value for arg in self.values if arg.value is not None}

    def has_unassigned(self) -> bool:
        return any(arg.assigned is None for arg in self.values)

    def vars(self) -> set[clingo.Symbol]:
        vars = set()
        for arg in self.values:
            vars.update(evaluator.collectVars(arg.expr))
        return vars

    def evaluate(self, evaluations: Dict[clingo.Symbol, Any], ctl: clingo.Control) -> tuple[bool, bool]:
        """
        Evaluate the expression and return a tuple (changed, conflict).
        changed is True if the value has changed.
        conflict is True if there is a conflict.
        For sets, there should never be a conflict.
        """
        lit = self.literals.pop()
        self.literals.add(lit)
        if not ctl.assignment.is_true(lit):
            return False, False

        changed = False
        for arg in self.values:
            changed |= arg.evaluate(evaluations, ctl)

        if changed:
            self.decision_level = ctl.assignment.decision_level

        return changed, False

    def reset(self):
        for arg in self.values:
            arg.reset()
        self.decision_level = float('inf')

    def __eq__(self, value):
        if not isinstance(value, SetVariable):
            assert False, "SetVariable can only be compared to another SetVariable"
        return self.var == value.var and self.values == value.values
    
    def __hash__(self):
        return hash((self.var, frozenset(self.values)))
    
    def __str__(self):
        return f"SetVariable({self.name}, {self.var})"

def make_dict_from_variables(variables: Sequence[Variable | SetVariable]) -> Dict[clingo.Symbol, Any | set[Any]]:
    result: Dict[clingo.Symbol, Any | set[Any]] = {}
    for var in variables:
        if var.get_value() is not None and var.get_value() is not VALUE_NOT_SET:
            result[var.var] = var.get_value()
        else:
            # here value is none so we check to see if it is still possible to get a value
            # if not, we set it to none
            # if yes, then we just skip it
            if not var.has_unassigned():
                result[var.var] = None

    return result

class ConstraintHandlerPropagator:

    def __init__(self):
        self.symbol2var: Dict[clingo.Symbol, Variable | SetVariable] = {}
        self.assign2symbol_var: Dict[clingo.Symbol, clingo.Symbol] = {}
        self.literal2var: Dict[int, list[Variable | SetVariable]] = {}

        self.evaluatevars: list[EvaluateVariable] = []

        self.ensure_symbol_lit: Dict[clingo.Symbol, int] = {}
        self.ensure_symbol_parsed: Dict[clingo.Symbol, Tuple[str, evaluator.Expr]]

        # maybe reasons should also be inside the Variable classes?
        self.reasons: Dict[clingo.symbol, set[int]] = defaultdict(set)

        self.model: List[clingo.Symbol] = []

    def init(self, ctl: clingo.PropagateInit):
        self.get_ensure(ctl)
        self.get_assign(ctl)
        self.get_set_declarations(ctl)
        self.set_parents()

        self.get_evaluate(ctl)

        myprint("INIT DONE")
        myprint("#"*50)

    def check(self, ctl: clingo.PropagateControl):
        myprint("CHECKING")

        self.evaluated_solver_assignment(ctl, set(self.symbol2var.values()))

        myprint(f"Evaluated assignments: {make_dict_from_variables(self.symbol2var.values())}")
        backtrack = self.check_ensure(ctl)
        myprint(f"backtracking {backtrack}")
        if backtrack:
            return

        self.check_evaluate(ctl)

        myprint("CHECK DONE!")

    def check_evaluate(self, ctl: clingo.PropagateControl):
        myprint("Checking evaluate atoms")
        myprint(f"Evaluated assignments before evaluate: {make_dict_from_variables(self.symbol2var.values())}")
        for var in self.evaluatevars:
            var.evaluate(make_dict_from_variables(self.symbol2var.values()), ctl)

    def check_ensure(self, ctl: clingo.PropagateControl) -> bool:
        """
        This method checks the ensure constraints in the propagator.
        It evaluates the expressions and checks if they hold true.
        If any ensure constraint is violated, it adds a nogood and propagates
        """
        for symbol, lit in self.ensure_symbol_lit.items():
            name, expr = self.ensure_symbol_parsed[symbol]
            myprint(f"Checking ensure: {name} := {str(expr)} with literal {lit}")
            evaluated = evaluator.evaluate_expr(make_dict_from_variables(self.symbol2var.values()), expr)

            myprint(f"Ensure constraint {name}: {expr} evaluated to {evaluated}")
            if evaluated is None:
                continue

            if not evaluated:
                nogood = {lit}.union(*(self.reasons[dvar] for dvar in evaluator.collectVars(expr)))
                myprint(f"the reason for {expr} being {evaluated} is {nogood} based on vars in {evaluator.collectVars(expr)}")
                if ctl.add_nogood(list(nogood)):
                    assert False, "Added violated constraint but solver did not detect it"
                return True
        
        myprint("Ensures checked")
        return False
    
    def propagate(self, ctl: clingo.PropagateControl, changes: Sequence[int]) -> None:
        """
        This method is called to propagate the constraints in the propagator.
        It evaluates the expressions assigned to variables and checks the ensures.
        If any ensure constraint is violated, it adds a nogood and propagates.
        """
        # return
        myprint(f"PROPAGATING with changes: {changes} and decision level {ctl.assignment.decision_level}")
        to_evaluate: set[Variable | SetVariable] = set()
        for lit in changes:
            if lit in self.literal2var:
                to_evaluate.update(self.literal2var[lit])

        self.evaluated_solver_assignment(ctl, to_evaluate)
        myprint(f"Evaluated assignments: {make_dict_from_variables(self.symbol2var.values())}")

        backtrack = self.check_ensure(ctl)
        myprint(f"PROPAGATION DONE, backtracking {backtrack}")
        if backtrack:
            return

    def evaluated_solver_assignment(self, ctl: clingo.PropagateControl, to_evaluate: set[Variable | SetVariable]) -> bool:
        """
        This method evaluates the variables given using the current solver assignment.
        If a variable's value changes, it also evaluates its parents.
        """
        while len(to_evaluate) > 0:
            var = to_evaluate.pop()
            myprint(f"Evaluating variable {var} at decision level {ctl.assignment.decision_level}")

            result = self.evaluate_variable(ctl, var)
            if result is None:
                # variable had issue, stop propagation!
                return False
            elif result:
                # variable changed, evaluate parents
                for parent in var.parents:
                    to_evaluate.add(parent)
                    
    def evaluate_variable(self, ctl: clingo.PropagateControl, var: Variable | SetVariable) -> bool | None:
        """
        This method evaluates a variable in the propagator.
        It uses the current solver assignment to determine its value.
        """
        evaluated, conflict = var.evaluate(make_dict_from_variables(self.symbol2var.values()), ctl)
        myprint(f"Variable {var} is: {evaluated}, conflict: {conflict}")
        if evaluated or conflict:
            myprint(f"Var {var} evaluated to {var.get_value()} at decision level {var.decision_level}")
            self.reasons[var.var] = var.literals
            self.reasons[var.var] = self.reasons[var.var].union(*(self.reasons[dvar] for dvar in var.vars()))
            myprint(f"the reason(s) for {var} taking value {var.get_value()} is {self.reasons[var.var]}")
            if conflict:
                myprint(f"Var {var} is in conflict at decision level {var.decision_level}")
                ng = self.reasons[var.var].union(var.literals)
                myprint(f"Adding nogood {ng}")
                if ctl.add_nogood(ng):
                    assert False, "Added violated constraint but solver did not detect it"
                return None

        return evaluated

    def undo(self, thread_id: int, assignment: clingo.Assignment, changes: Sequence[int]) -> None:
        """
        Resets the evaluations and reasons based on the current assignment.
        """
        myprint(f"UNDOING for decision level {assignment.decision_level} with changes {changes}")
        for var in self.symbol2var.values():
            if var.decision_level >= assignment.decision_level:
                myprint(f"Resetting {var} and its reasons due to decision level {var.decision_level} >= {assignment.decision_level}")
                var.reset()
                if var.var in self.reasons:
                    del self.reasons[var.var]

    def parse_assign(self, symbol: clingo.Symbol) -> Tuple[str, clingo.Symbol, evaluator.Expr]:
        """
        Parses an assign atom and returns its name, variable, and expression.
        """
        name = myClorm.cltopy(symbol.arguments[0])
        var = myClorm.cltopy(symbol.arguments[1])
        expr = myClorm.cltopy(symbol.arguments[2],evaluator.Expr)
        return name, var, expr

    def parse_ensure(self, symbol: clingo.Symbol) -> Tuple[str, evaluator.Expr]:
        """
        Parses an ensure atom and returns its name and expression.
        """
        name = myClorm.cltopy(symbol.arguments[0])
        expr = myClorm.cltopy(symbol.arguments[1],evaluator.Expr)
        return name, expr

    def parse_evaluate(self, symbol: clingo.Symbol) -> evaluator.Expr:
        """
        Parses an evaluate atom and returns its expression.
        """
        op = myClorm.cltopy(symbol.arguments[0], evaluator.Operator)
        args = []
        for s in myClorm.unnest(symbol.arguments[1]):
            args.append(myClorm.cltopy(s,evaluator.Expr))

        return op, args

    def get_ensure(self, ctl: clingo.PropagateInit):
        """
        This method initializes the ensure constraints from the ASP encoding.
        It reads the propagator_ensure atoms and stores their literals and parsed expressions.
        """

        for atom in ctl.symbolic_atoms.by_signature(AtomNames.ENSURE,2):
            self.ensure_symbol_lit[atom.symbol] = ctl.solver_literal(atom.literal)
            self.ensure_symbol_parsed[atom.symbol] = self.parse_ensure(atom.symbol)

    def get_assign(self, ctl: clingo.PropagateInit):
        """
        This method initializes the variables from the ASP encoding.
        It reads the propagator_assign atoms and creates Variable instances.
        """

        for atom in ctl.symbolic_atoms.by_signature(AtomNames.ASSIGN,3):
            literal = ctl.solver_literal(atom.literal)        
            name, symbol_var, expr = self.parse_assign(atom.symbol)
            if symbol_var in self.symbol2var:
                variable = self.symbol2var[symbol_var]
            else:
                variable = Variable(name, symbol_var)
                self.symbol2var[symbol_var] = variable
                
            variable.add_value(expr, literal)
            self.assign2symbol_var[atom.symbol] = symbol_var
            if literal not in self.literal2var:
                self.literal2var[literal] = []
            self.literal2var[literal].append(variable)

            ctl.add_watch(literal)
 
            variable.evaluate(make_dict_from_variables(self.symbol2var.values()), ctl)

    def get_evaluate(self, ctl: clingo.PropagateInit):
        """
        This method initializes the variables from the ASP encoding.
        It reads the propagator_assign atoms and creates Variable instances.
        """

        for atom in ctl.symbolic_atoms.by_signature(AtomNames.EVALUATE,2):
            literal = ctl.solver_literal(atom.literal)        
            op, args = self.parse_evaluate(atom.symbol)

            var = EvaluateVariable(op, args, literal)
            self.evaluatevars.append(var)

    def get_set_declarations(self, ctl: clingo.PropagateInit):
        """
        This method initializes the set variables from the ASP encoding.
        It reads the set_declare and set_assign atoms and creates SetVariable instances.
        """

        for atom in ctl.symbolic_atoms.by_signature(AtomNames.SET_DECLARE, 2):
            literal = ctl.solver_literal(atom.literal)
            name = myClorm.cltopy(atom.symbol.arguments[0])
            symbol_var = myClorm.cltopy(atom.symbol.arguments[1])
            variable = SetVariable(name, symbol_var, literal)

            self.symbol2var[symbol_var] = variable
            self.assign2symbol_var[atom.symbol] = symbol_var
            if literal not in self.literal2var:
                self.literal2var[literal] = []
            self.literal2var[literal].append(variable)

            ctl.add_watch(literal)

        for atom in ctl.symbolic_atoms.by_signature(AtomNames.SET_ASSIGN, 3):
            literal = ctl.solver_literal(atom.literal)
            name, symbol_var, expr = self.parse_assign(atom.symbol)
            setvar = self.symbol2var[symbol_var]
            setvar.add_argument(expr, literal)
            self.assign2symbol_var[atom.symbol] = symbol_var
            if literal not in self.literal2var:
                self.literal2var[literal] = []
            self.literal2var[literal].append(setvar)

            ctl.add_watch(literal)

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

    def on_model(self,model):
        self.model = []
        for var in self.symbol2var.values():
            final_value = var.get_value()
            if final_value is None or final_value is VALUE_NOT_SET:
                continue
            if type(final_value) == frozenset:
                for value in final_value:
                    if value is None or value is VALUE_NOT_SET:
                        continue
                    pyAtom = Set_Value(var.var,evaluator.get_baseType(value),value)
                    myprint(f"adding set atom {pyAtom}",end=" ")
                    clAtom = myClorm.pytocl(pyAtom)
                    myprint(f"= {clAtom}")
                    if not model.contains(clAtom):
                        model.extend([clAtom])
                        self.model.append(clAtom)
            else:
                pyAtom = Value(var.var,evaluator.get_baseType(final_value),final_value)
                myprint(f"adding atom {pyAtom}",end=" ")
                clAtom = myClorm.pytocl(pyAtom)
                myprint(f"= {clAtom}")

                if not model.contains(clAtom):
                    model.extend([clAtom])
                    self.model.append(clAtom)

        
        for var in self.evaluatevars:
            # if var.value is None or var.value is VALUE_NOT_SET:
            #     continue
            pyAtom = Evaluated(var.op, var.args, evaluator.get_baseType(var.get_value()), var.get_value())
            myprint(f"adding evaluate atom {pyAtom}",end=" ")
            clAtom = myClorm.pytocl(pyAtom)
            print(f"= {clAtom}")
            if not model.contains(clAtom):
                model.extend([clAtom])
                self.model.append(clAtom)

