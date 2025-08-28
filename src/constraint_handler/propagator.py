import clingo
import constraint_handler.myClorm as myClorm
import constraint_handler.evaluator as evaluator

from collections import defaultdict

from typing import Any, Dict, NamedTuple, List, Sequence, Tuple
from dataclasses import dataclass

import queue

@dataclass
class AtomNames:
    ASSIGN: str = "propagator_assign"
    ENSURE: str = "propagator_ensure"
    SET_DECLARE: str = "set_declare"
    SET_ASSIGN: str = "set_assign"


class Val(NamedTuple):
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

        print("INIT DONE")
        print("#"*50)

    def check(self, ctl: clingo.PropagateControl):
        print("CHECKING")

        self.evaluated_solver_assignment(ctl)
        print(f"after evaluation, the reasons are {self.reasons}")

        backtrack = self.check_ensure(ctl)
        print(f"CHECK DONE, backtracking {backtrack}")
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
            print(f"Checking ensure: {name} := {str(expr)} with literal {lit}")
            evaluated = evaluator.evaluate_expr(self.evaluated | self.evaluated_sets, expr)

            print(f"Ensure constraint {name}: {expr} evaluated to {evaluated}")
            if evaluated is None:
                continue

            if not evaluated:
                nogood = {lit}.union(*(self.reasons[dvar] for dvar in evaluator.collectVars(expr)))
                print(f"the reason for {expr} being {evaluated} is {nogood} based on vars in {evaluator.collectVars(expr)}")
                if ctl.add_nogood(list(nogood)):
                    assert False, "Added violated constraint but solver did not detect it"
                return True
        
        print("Ensures checked")
        return False
    
    def propagate(self, ctl: clingo.PropagateControl, changes: Sequence[int]) -> None:
        """
        This method is called to propagate the constraints in the propagator.
        It evaluates the expressions assigned to variables and checks the ensures.
        If any ensure constraint is violated, it adds a nogood and propagates.
        """
        # return
        print(f"PROPAGATING with changes: {changes} and decision level {ctl.assignment.decision_level}")
        self.evaluated_solver_assignment(ctl)
        print(f"Evaluated assignments: {self.evaluated | self.evaluated_sets}")
        backtrack = self.check_ensure(ctl)
        print(f"PROPAGATION DONE, backtracking {backtrack}")
        if backtrack:
            return

    def evaluated_solver_assignment(self, ctl: clingo.PropagateControl) -> Dict[clingo.symbol, Any]:
        """
        This method evaluates the expressions assigned to variables in the propagator.
        It uses the current solver assignment to determine which expressions to evaluate.
        It returns a dictionary with the evaluated variables and their values.
        """
        changed: bool = True
        max_iterations: int = 10 # these 2 are just for safety in the testing phase
        iterations: int = 0
        
        # Each loop evaluates the assignments
        # and updates the evaluations dictionary
        while changed and iterations < max_iterations:
            iterations += 1
            changed = False
            print(f"Evaluating... Iteration {iterations}\nCurrent evaluations: {make_dict_from_variables(self.evaluated.union(self.evaluated_sets))}")
            for var in self.symbol2var.values():
                print(f"Looking at variable {var}")

                evaluated = var.evaluate(make_dict_from_variables(self.evaluated.union(self.evaluated_sets)), ctl)
                if evaluated:
                    print(f"Var {var} evaluated to {evaluated}")
                    changed = True
                    self.reasons[var] = { var.literal }
                    self.reasons[var] = self.reasons[var].union(*(self.reasons[dvar] for dvar in var.vars()))
                    print(f"the reason(s) for {var} taking value {evaluated} is {self.reasons[var]}")
    
    def undo(self, thread_id: int, assignment: clingo.Assignment, changes: Sequence[int]) -> None:
        """
        Resets the evaluations and reasons based on the current assignment.
        """
        print(f"UNDOING for decision level {assignment.decision_level} with changes {changes}")
        for var in self.symbol2var.values():
            if var.decision_level >= assignment.decision_level:
                print(f"Resetting {var} and its reasons due to decision level {var.decision_level} >= {assignment.decision_level}")
                var.reset()
                if var.var in self.reasons:
                    del self.reasons[var.var]
                # else:
                #     assert False, f"Variable {var} not in reasons but should be"

    def parse_assign(self, symbol: clingo.Symbol) -> Tuple[str, clingo.Symbol, evaluator.Expr]:
        name = myClorm.cltopy(symbol.arguments[0])
        var = myClorm.cltopy(symbol.arguments[1])
        expr = myClorm.cltopy(symbol.arguments[2],evaluator.Expr)
        return name, var, expr

    def parse_ensure(self, symbol: clingo.Symbol) -> Tuple[str, evaluator.Expr]:
        name = myClorm.cltopy(symbol.arguments[0])
        expr = myClorm.cltopy(symbol.arguments[1],evaluator.Expr)
        return name, expr

    def get_ensure(self, ctl: clingo.PropagateInit):
        for atom in ctl.symbolic_atoms.by_signature(AtomNames.ENSURE,2):
            self.ensure_symbol_lit[atom.symbol] = ctl.solver_literal(atom.literal)
            self.ensure_symbol_parsed[atom.symbol] = self.parse_ensure(atom.symbol)
        
    def get_assign(self, ctl: clingo.PropagateInit):
        for atom in ctl.symbolic_atoms.by_signature(AtomNames.ASSIGN,3):
            literal = ctl.solver_literal(atom.literal)        
            name, var, expr = self.parse_assign(atom.symbol)
            variable = Variable(name, var, literal, expr)
            self.evaluated.add(variable)
            self.symbol2var[atom.symbol] = variable
            self.assign2symbol_var[atom.symbol] = var
            ctl.add_watch(ctl.solver_literal(atom.literal))

            variable.evaluate(make_dict_from_variables(self.evaluated.union(self.evaluated_sets)), ctl)

    def get_set_declarations(self, ctl: clingo.PropagateInit):
        for atom in ctl.symbolic_atoms.by_signature(AtomNames.SET_DECLARE, 2):
            name = myClorm.cltopy(atom.symbol.arguments[0])
            var = myClorm.cltopy(atom.symbol.arguments[1])
            variable = SetVariable(name, var, ctl.solver_literal(atom.literal)) 
            self.evaluated_sets.add(variable)
            self.symbol2var[var] = variable
            self.assign2symbol_var[atom.symbol] = var
            ctl.add_watch(ctl.solver_literal(atom.literal))

        for atom in ctl.symbolic_atoms.by_signature(AtomNames.SET_ASSIGN, 3):
            name, var, expr = self.parse_assign(atom.symbol)
            self.symbol2var[var].add_argument(expr, ctl.solver_literal(atom.literal))
            self.assign2symbol_var[atom.symbol] = var
            ctl.add_watch(ctl.solver_literal(atom.literal))

        for var in self.evaluated_sets:
            var.evaluate(make_dict_from_variables(self.evaluated.union(self.evaluated_sets)), ctl)

    def on_model(self,model):
        self.model = []
        for var in self.evaluated.union(self.evaluated_sets):
            pyAtom = Val(var.var,evaluator.get_baseType(var.get_value()),var.get_value())
            print(f"adding atom {pyAtom}",end=" ")
            clAtom = myClorm.pytocl(pyAtom)
            print(f"= {clAtom}")
            if not model.contains(clAtom):
                model.extend([clAtom])
                self.model.append(clAtom)

