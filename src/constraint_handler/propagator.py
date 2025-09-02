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

@dataclass
class AtomNames:
    ASSIGN: str = "propagator_assign"
    ENSURE: str = "propagator_ensure"
    SET_DECLARE: str = "set_declare"
    SET_ASSIGN: str = "set_assign"


class Value(NamedTuple):
    name: clingo.Symbol
    type_: evaluator.BaseType | None
    value: bool | int | float | str | clingo.Symbol


class VariableValue:

    def __init__(self, expr: evaluator.Expr, lit: int):
        self.expr = expr
        self.value: Any = None

        self.literal: int = lit

    def evaluate(self, evaluations: Dict[clingo.Symbol, Any], ctl: clingo.Control) -> bool:
        """Evaluate the expression and return True if the value has changed."""
        if not ctl.assignment.is_true(self.literal):
            return False

        value = evaluator.evaluate_expr(evaluations, self.expr)
        
        if type(value) == set:
            if None in value:
                # if something in the set is undefined
                # we do not add it to as a value
                value.remove(None)
            value = frozenset(value)

        if value == self.value:
            return False
        
        self.value = value
        return True

    def reset(self):
        self.value = None

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
    def __init__(self, name: str, var: clingo.Symbol, lit: int, expr: clingo.Symbol):
        self.name = name
        self.var = var
        self.value: VariableValue = VariableValue(expr, lit)

        self.decision_level: int = float('inf')
        self.parents: List[Variable | SetVariable] = []

    @property
    def literal(self) -> int:
        return self.value.literal

    def evaluate(self, evaluations: Dict[clingo.Symbol, Any], ctl: clingo.Control) -> bool:
        """Evaluate the expression and return True if the value has changed."""        
        if self.value.evaluate(evaluations, ctl):
            self.decision_level = ctl.assignment.decision_level
            return True
        return False

    def vars(self) -> set[clingo.Symbol]:
        return evaluator.collectVars(self.value.expr)

    def get_value(self) -> Any:
        return self.value.value

    def reset(self):
        self.value.reset()
        self.decision_level = float('inf')

    def __eq__(self, other):
        if not isinstance(other, Variable):
            assert False, "Variable can only be compared to another Variable"
        return self.var == other.var and self.value == other.value

    def __hash__(self):
        return hash((self.var, self.value))

    def __str__(self):
        return f"Variable({self.name}, {self.var})"
    
    def __repr__(self):
        return f"Variable({self.name}, {self.var}, {self.value.literal}, {self.value.expr})"

class SetVariable:
    """
        A set variable with a name and a set of value expressions.
        This is supposed to mirror the set_declare/2 and set_assign/3 atom in the ASP encoding.
    """
    def __init__(self, name: str, var: clingo.Symbol, lit: int):
        self.name = name
        self.var = var
        self.literal = lit
        self.value: set[VariableValue] = set()

        self.decision_level: int = float('inf')
        self.parents: List[Variable | SetVariable] = []

    def add_argument(self, arg: evaluator.Expr, lit: int) -> None:
        self.value.add(VariableValue(arg, lit))

    def __contains__(self, item):
        return item in self.value
    
    def get_value(self) -> set[Any]:
        return {arg.value for arg in self.value if arg.value is not None}

    def vars(self) -> set[clingo.Symbol]:
        return set.union(*(evaluator.collectVars(arg.expr) for arg in self.value))

    def evaluate(self, evaluations: Dict[clingo.Symbol, Any], ctl: clingo.Control) -> bool:
        """Evaluate all arguments and return True if any value has changed."""
        if not ctl.assignment.is_true(self.literal):
            return False

        changed = False
        for arg in self.value:
            changed |= arg.evaluate(evaluations, ctl)

        if changed:
            self.decision_level = ctl.assignment.decision_level

        return changed

    def reset(self):
        for arg in self.value:
            arg.reset()
        self.decision_level = float('inf')

    def __eq__(self, value):
        if not isinstance(value, SetVariable):
            assert False, "SetVariable can only be compared to another SetVariable"
        return self.var == value.var and self.value == value.value
    
    def __hash__(self):
        return hash((self.var, frozenset(self.value)))
    
    def __str__(self):
        return f"SetVariable({self.name}, {self.var})"


def make_dict_from_set_variables(variables: Sequence[SetVariable]) -> Dict[clingo.Symbol, set[Any]]:
    result: Dict[clingo.Symbol, set[Any]] = {}
    for var in variables:
        result[var.var] = var.get_value()
    return result

def make_dict_from_variables(variables: Sequence[Variable | SetVariable]) -> Dict[clingo.Symbol, Any | set[Any]]:
    result: Dict[clingo.Symbol, Any | set[Any]] = {}
    for var in variables:
        if var.get_value() is not None:
            result[var.var] = var.get_value()
    return result

class ConstraintHandlerPropagator:

    def __init__(self):
        self.symbol2var: Dict[clingo.Symbol, Variable | SetVariable] = {}
        self.assign2symbol_var: Dict[clingo.Symbol, clingo.Symbol] = {}
        self.literal2var: Dict[int, list[Variable | SetVariable]] = {}

        self.evaluated: set[Variable] = set()
        self.evaluated_sets: set[SetVariable] = set()

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

        myprint("INIT DONE")
        myprint("#"*50)

    def check(self, ctl: clingo.PropagateControl):
        myprint("CHECKING")

        self.evaluated_solver_assignment(ctl, set(self.symbol2var.values()))

        backtrack = self.check_ensure(ctl)
        myprint(f"CHECK DONE, backtracking {backtrack}")
        if backtrack:
            return

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

    def evaluated_solver_assignment(self, ctl: clingo.PropagateControl, to_evaluate: set[Variable | SetVariable]) -> None:
        """
        This method evaluates the variables given using the current solver assignment.
        If a variable's value changes, it also evaluates its parents.
        """
        while len(to_evaluate) > 0:
            var = to_evaluate.pop()
            myprint(f"Evaluating variable {var} at decision level {ctl.assignment.decision_level}")

            if self.evaluate_variable(ctl, var):
                for parent in var.parents:
                    to_evaluate.add(parent)
    
    def evaluate_variable(self, ctl: clingo.PropagateControl, var: Variable | SetVariable) -> bool:
        """
        This method evaluates a variable in the propagator.
        It uses the current solver assignment to determine its value.
        """
        evaluated = var.evaluate(make_dict_from_variables(self.symbol2var.values()), ctl)
        if evaluated:
            myprint(f"Var {var} evaluated to {var.get_value()} at decision level {var.decision_level}")
            self.reasons[var.var] = { var.literal }
            self.reasons[var.var] = self.reasons[var.var].union(*(self.reasons[dvar] for dvar in var.vars()))
            myprint(f"the reason(s) for {var} taking value {var.get_value()} is {self.reasons[var.var]}")

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
                # else:
                #     assert False, f"Variable {var} not in reasons but should be"

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
            variable = Variable(name, symbol_var, literal, expr)

            self.evaluated.add(variable)
            self.symbol2var[symbol_var] = variable
            self.assign2symbol_var[atom.symbol] = symbol_var
            if literal not in self.literal2var:
                self.literal2var[literal] = []
            self.literal2var[literal].append(variable)

            ctl.add_watch(ctl.solver_literal(atom.literal))

            variable.evaluate(make_dict_from_variables(self.symbol2var.values()), ctl)

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

            self.evaluated_sets.add(variable)
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

        for symbol_var in self.evaluated_sets:
            symbol_var.evaluate(make_dict_from_variables(self.symbol2var.values()), ctl)

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
                    assert False, f"Variable {symbol_var} not found in symbol2var"
                self.symbol2var[symbol_var].parents.append(var)

    def on_model(self,model):
        self.model = []
        for var in self.evaluated.union(self.evaluated_sets):
            if var.get_value() is None:
                continue
            pyAtom = Value(var.var,evaluator.get_baseType(var.get_value()),var.get_value())
            myprint(f"adding atom {pyAtom}",end=" ")
            clAtom = myClorm.pytocl(pyAtom)
            myprint(f"= {clAtom}")
            if not model.contains(clAtom):
                model.extend([clAtom])
                self.model.append(clAtom)

