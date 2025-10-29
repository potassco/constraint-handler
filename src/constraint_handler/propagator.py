import enum
import clingo
import constraint_handler.myClorm as myClorm
import constraint_handler.evaluator as evaluator

from collections import defaultdict

from typing import Any, Dict, NamedTuple, List, Sequence, Tuple
from dataclasses import dataclass

DEBUG_PRINT = True

def myprint(*args, **kwargs):
    if DEBUG_PRINT:
        print(*args, **kwargs)

# enum for value_not_set, assignment_is_false, and value_is_none
class ValueStatus(enum.Enum):
    NOT_SET = "value_not_set"
    ASSIGNMENT_IS_FALSE = "assignment_is_false"

@dataclass
class AtomNames:
    ASSIGN: str = "propagator_assign"
    ENSURE: str = "propagator_ensure"
    EVALUATE: str = "evaluate"
    SET_DECLARE: str = "propagator_set_declare"
    SET_ASSIGN: str = "propagator_set_assign"
    MULTIMAP_DECLARE: str = "propagator_multimap_declare"
    MULTIMAP_ASSIGN: str = "propagator_multimap_assign"


class Value(NamedTuple):
    name: clingo.Symbol
    type_: evaluator.BaseType | None
    value: bool | int | float | str | clingo.Symbol

class Set_Value(NamedTuple):
    name: clingo.Symbol
    type_: evaluator.BaseType | None
    value: bool | int | float | str | clingo.Symbol

class Multimap_Value(NamedTuple):
    name: clingo.Symbol
    key_type: evaluator.BaseType | None
    value_type: evaluator.BaseType | None
    key: bool | int | float | str | clingo.Symbol
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
        self.value: Any = ValueStatus.NOT_SET
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
        self.value: Any = ValueStatus.NOT_SET

        self.literal: int = lit
        self.assigned: bool | None = None
        self.decision_level: int = float('inf')

    def evaluate(self, evaluations: Dict[clingo.Symbol, Any], ctl: clingo.Control) -> bool:
        """Evaluate the expression and return True if the value has changed."""
        self.assigned = ctl.assignment.value(self.literal)
        if ctl.assignment.is_false(self.literal):
            if self.value is None:
                return False
            
            self.value = None
            self.decision_level = ctl.assignment.level(self.literal)
            return True
        
        for var in self.vars():
            if var not in evaluations:
                # can't evaluate yet
                return False
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

    def vars(self) -> set[clingo.Symbol]:
        return evaluator.collectVars(self.expr)

    def reset(self, dl):
        if self.decision_level >= dl: 
            self.value = ValueStatus.NOT_SET
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

    def __repr__(self):
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
        self.value: Any = ValueStatus.NOT_SET
        self.parents: List["Variable" | "SetVariable" | "DictVariable"] = []

    def add_value(self, expr: evaluator.Expr, lit: int) -> None:
        self.expressions.add(VariableValue(expr, lit))

    def __contains__(self, item):
        return item in self.expressions

    def get_value(self) -> Any:
        return self.value

    def has_unassigned(self) -> bool:
        return any(var_value.value == ValueStatus.NOT_SET for var_value in self.expressions)
        return any(arg.assigned is None for arg in self.expressions)

    def vars(self) -> set[clingo.Symbol]:
        vars = set()
        for value in self.expressions:
            vars.update(value.vars())
        return vars

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
        val = self.get_values()
        if len(val) > 1:
            # multiple values assigned to the same variable
            myprint(f"Variable vals: {val}")
            return True, True
        elif len(val) == 0:
            if self.has_unassigned():
                # some values are unassigned
                # so we cannot determine the value yet
                val = {ValueStatus.NOT_SET}
            else:
                # if all values are set and none are true, then it is None
                val = {None}
        elif len(val) == 1:
            if val == self.value:
                # same value as before
                return False, False

        self.value = val.pop()
        return True, False

    def get_values(self) -> set[Any]:
        vals = set(value.value for value in self.expressions if value.value != ValueStatus.NOT_SET)
        return vals

    @property
    def literals(self) -> set[int]:
        lits = set()
        for value in self.expressions:
            if value.assigned is not None:
                if value.assigned:
                    lits.add(value.literal)
                else:
                    lits.add(-value.literal)
        return lits

    @property
    def decision_level(self) -> int:
        # if self.value is VALUE_NOT_SET:
        #     return float('inf')
        return min(value.decision_level for value in self.expressions)

    def reset(self, dl: int) -> None:
        for value in self.expressions:
            value.reset(dl)
            
        val = self.get_values()
        if len(val) == 0:
            if self.has_unassigned():
                # some values are unassigned
                # so we cannot determine the value yet
                self.value = ValueStatus.NOT_SET
            else:
                # if all values are set and none are true, then it is None
                self.value = None
        elif len(val) == 1:
            self.value = val.pop()
        else:
            print(f"Reset variable {self.name} at decision level {dl}, values after reset: {val}")
            assert False, "Variable has multiple values after reset, should not happen"

    def __eq__(self, other):
        if not isinstance(other, Variable):
            assert False, "Variable can only be compared to another Variable"
        return self.var == other.var and self.expressions == other.expressions

    def __hash__(self):
        return hash((self.var, frozenset(self.expressions)))

    def __str__(self):
        return f"Variable({self.name}, {self.var}, {self.literals}, {self.expressions})"

class SetVariableValue:
    def __init__(self):
        self.values: set[VariableValue] = set()

    def add_value(self, arg: evaluator.Expr, lit: int) -> None:
        self.values.add(VariableValue(arg, lit))

    @property
    def literals(self) -> set[int]:
        lits = set()
        for value in self.values:
            if value.assigned is not None:
                if value.assigned:
                    lits.add(value.literal)
                else:
                    lits.add(-value.literal)
        return lits

    @property
    def decision_level(self) -> int:
        return min(value.decision_level for value in self.values)

    def get_value(self) -> set[Any]:
        """
        If there is an unassigned value, return None.
        Otherwise return the set of assigned values without the None values.
        """
        if self.has_unassigned():
            return ValueStatus.NOT_SET
        return {arg.value for arg in self.values if arg.value is not None}

    def has_unassigned(self) -> bool:
        return any(arg.value == ValueStatus.NOT_SET for arg in self.values)

    def vars(self) -> set[clingo.Symbol]:
        vars = set()
        for arg in self.values:
            vars.update(arg.vars())
        return vars

    def evaluate(self, evaluations: Dict[clingo.Symbol, Any], ctl: clingo.Control) -> bool:
        """Evaluate the expression and return True if the value has changed."""
        changed = False
        for arg in self.values:
            changed |= arg.evaluate(evaluations, ctl)

        return changed

    def reset(self, dl: int):
        for arg in self.values:
            arg.reset(dl)

    def __eq__(self, other):
        if not isinstance(other, SetVariableValue):
            return False
        return self.values == other.values

    def __hash__(self):
        return hash(frozenset(self.values))

    def __str__(self):
        return f"SetVariableValue({self.values})"

class SetVariable:
    """
        A set variable with a name and a set of value expressions.
        This is supposed to mirror the set_declare/2 and set_assign/3 atom in the ASP encoding.
        set_declare is this class, while each set_assign adds a value to the set(which uses the SetVariableValue class).
    """
    def __init__(self, name: str, var: clingo.Symbol, lit: int):
        self.name = name
        self.var = var
        self.values: SetVariableValue = SetVariableValue()
        
        self.literal = lit # this is the literal for the set declaration
        self.truth_value: bool | None = None # Truth value of the set declaration
        self.decision_level: int = float('inf') # decision level of the set declaration

        self.parents: List["Variable" | "SetVariable" | "DictVariable"] = []

    def add_value(self, arg: evaluator.Expr, lit: int) -> None:
        self.values.add_value(arg, lit)

    @property
    def literals(self) -> set[int]:
        lits = self.values.literals
        lits.add(self.literal)
        return lits

    def get_value(self) -> set[Any]:
        """
        If there is an unassigned value, return None.
        Otherwise return the set of assigned values without the None values.
        """
        if self.truth_value:
            return self.values.get_value()

        return None

    def has_unassigned(self) -> bool:
        return self.values.has_unassigned()

    def vars(self) -> set[clingo.Symbol]:
        return self.values.vars()

    def evaluate(self, evaluations: Dict[clingo.Symbol, Any], ctl: clingo.Control) -> tuple[bool, bool]:
        """
        Evaluate the expression and return a tuple (changed, conflict).
        changed is True if the value has changed.
        conflict is True if there is a conflict.
        For sets, there should never be a conflict.
        """
        self.truth_value = ctl.assignment.value(self.literal)
        self.decision_level = ctl.assignment.level(self.literal)            

        if self.truth_value is not None and not self.truth_value: # if it is not assigned or false
            return False, False

        changed = self.values.evaluate(evaluations, ctl)

        return changed, False

    def reset(self, dl: int) -> None:
        self.values.reset(dl)
        if self.decision_level > dl: 
            self.decision_level = float('inf')

    def __eq__(self, value):
        if not isinstance(value, SetVariable):
            assert False, "SetVariable can only be compared to another SetVariable"
        return self.var == value.var and self.values == value.values
    
    def __hash__(self):
        return hash((self.var, self.values))
    
    def __str__(self):
        return f"SetVariable({self.name}, {self.var})"


class DictVariable:
    """
        A dict variable with a name and a set of key-value expressions.
        This is supposed to mirror the multimap_declare/2 and multimap_assign/4 atom in the ASP encoding.
        multimap_declare is this class, while each multimap_assign adds a key-value pair to the dict(which uses the SetVariableValue class).
    """
    def __init__(self, name: str, var: clingo.Symbol, lit: int):
        self.name = name
        self.var = var
        self.values: Dict[clingo.Symbol, SetVariableValue] = {}
        
        self.literal : int = lit
        self.truth_value: bool | None = None
        self.decision_level: int = float('inf')

        self.parents: List[Variable | SetVariable | DictVariable] = []
        
    def add_value(self, key: clingo.Symbol, expr: evaluator.Expr, lit: int) -> None:
        if key not in self.values:
            self.values[key] = SetVariableValue()
        self.values[key].add_value(expr, lit)

    @property
    def literals(self) -> set[int]:
        lits = set()
        for value in self.values.values():
            lits.update(value.literals)
        lits.add(self.literal)

        return lits
    
    def get_value(self) -> Dict[clingo.Symbol, Any]:
        """
        Returns a dictionary mapping keys to their assigned values.
        If any value is unassigned, returns None for that key.
        """
        if self.truth_value:
            result = {}
            for key, value in self.values.items():
                if value.get_value() is ValueStatus.NOT_SET or value.get_value() is None:
                    continue
                result[key] = value.get_value()
            return result
    
        return None

    def has_unassigned(self) -> bool:
        return any(value.has_unassigned() for value in self.values.values())

    def vars(self) -> set[clingo.Symbol]:
        # TODO: check if keys can also have variables
        vars = set()
        for value in self.values.values():
            vars.update(value.vars())
        return vars

    def evaluate(self, evaluations: Dict[clingo.Symbol, Any], ctl: clingo.Control) -> tuple[bool, bool]:
        """
        Evaluate all values in the dictionary and return (changed, conflict).
        For DictVariable, conflict should never occur.
        """

        self.truth_value = ctl.assignment.value(self.literal)
        self.decision_level = ctl.assignment.level(self.literal)

        if self.truth_value is not None and not self.truth_value:
            return False, False

        changed = False
        for value in self.values.values():
            changed |= value.evaluate(evaluations, ctl)
        
        return changed, False

    def reset(self, dl: int) -> None:
        for value in self.values.values():
            value.reset(dl)

        if self.decision_level > dl: 
            self.decision_level = float('inf')

    def __eq__(self, other):
        if not isinstance(other, DictVariable):
            assert False, "DictVariable can only be compared to another DictVariable"
        return self.var == other.var and self.values == other.values

    def __hash__(self):
        return hash((self.var, frozenset(self.values.items())))

    def __str__(self):
        return f"DictVariable({self.name}, {self.var})"

def make_dict_from_variables(variables: Sequence[Variable | SetVariable | DictVariable]) -> Dict[clingo.Symbol, Any | set[Any] | Dict[Any, Any]]:
    result: Dict[clingo.Symbol, Any | set[Any] | Dict[Any, Any]] = {}
    for var in variables:
        value = var.get_value()
        if isinstance(var, Variable):
            if value is not ValueStatus.NOT_SET:
                result[var.var] = value
        elif isinstance(var, SetVariable) or isinstance(var, DictVariable):
            if value == ValueStatus.NOT_SET:
                continue
            elif value is not None:
                result[var.var] = value
            elif not var.has_unassigned():
                result[var.var] = None
    # print(f"make_dict_from_variables: {result}")
    return result


class ConstraintHandlerPropagator:

    def __init__(self, check_only: bool = False):
        self.symbol2var: Dict[clingo.Symbol, Variable | SetVariable | DictVariable] = {}
        self.assign2symbol_var: Dict[clingo.Symbol, clingo.Symbol] = {}
        self.literal2var: Dict[int, list[Variable | SetVariable | DictVariable]] = {}

        self.evaluatevars: list[EvaluateVariable] = []

        self.ensure_symbol_lit: Dict[clingo.Symbol, int] = {}
        self.ensure_symbol_parsed: Dict[clingo.Symbol, Tuple[str, evaluator.Expr]]

        self.check_only = check_only


    def init(self, ctl: clingo.PropagateInit):
        if self.check_only:
            ctl.check_mode = clingo.PropagatorCheckMode.Total

        self.get_ensure(ctl)
        self.get_assign(ctl)
        self.get_set_declarations(ctl)
        self.get_multimap_declarations(ctl)
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
                nogood = {lit}.union(*(self.get_reasons(dvar) for dvar in evaluator.collectVars(expr)))
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
                myprint(f"Variable {var} changed, adding parents to evaluate queue: {var.parents}")
                for parent in var.parents:
                    to_evaluate.add(parent)

    def evaluate_variable(self, ctl: clingo.PropagateControl, var: Variable | SetVariable | DictVariable) -> bool | None:
        """
        This method evaluates a variable in the propagator.
        It uses the current solver assignment to determine its value.
        """
        changed, conflict = var.evaluate(make_dict_from_variables(self.symbol2var.values()), ctl)
        myprint(f"Variable {var} is changed: {changed}, conflict: {conflict}")

        if conflict:
            myprint(f"Var {var} is in conflict at decision level {var.decision_level}")
            ng = self.get_reasons(var)
            myprint(f"Adding nogood {ng}")
            if ctl.add_nogood(ng):
                assert False, "Added violated constraint but solver did not detect it"
            return None

        return changed

    def get_reasons(self, var: Variable | SetVariable | DictVariable) -> set[int]:
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
            myprint(f"Resetting {var} and its reasons due to decision level {var.decision_level} >= {assignment.decision_level}")
            var.reset(assignment.decision_level)

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
            setvar.add_value(expr, literal)
            self.assign2symbol_var[atom.symbol] = symbol_var
            if literal not in self.literal2var:
                self.literal2var[literal] = []
            self.literal2var[literal].append(setvar)

            ctl.add_watch(literal)

    def get_multimap_declarations(self, ctl: clingo.PropagateInit):
        """
        This method initializes the dict variables from the ASP encoding.
        It reads the multimap_declare and multimap_assign atoms and creates DictVariable instances.
        """
        # TODO: this was done by copilot, check if it is correct!

        for atom in ctl.symbolic_atoms.by_signature(AtomNames.MULTIMAP_DECLARE, 2):
            literal = ctl.solver_literal(atom.literal)
            name = myClorm.cltopy(atom.symbol.arguments[0])
            symbol_var = myClorm.cltopy(atom.symbol.arguments[1])
            variable = DictVariable(name, symbol_var, literal)
            self.symbol2var[symbol_var] = variable
            self.assign2symbol_var[atom.symbol] = symbol_var
            if literal not in self.literal2var:
                self.literal2var[literal] = []
            self.literal2var[literal].append(variable)

            ctl.add_watch(literal)

        for atom in ctl.symbolic_atoms.by_signature(AtomNames.MULTIMAP_ASSIGN, 4):
            literal = ctl.solver_literal(atom.literal)
            name = myClorm.cltopy(atom.symbol.arguments[0])
            symbol_var = myClorm.cltopy(atom.symbol.arguments[1])
            key = myClorm.cltopy(atom.symbol.arguments[2])
            expr = myClorm.cltopy(atom.symbol.arguments[3], evaluator.Expr)
            dictvar: DictVariable = self.symbol2var[symbol_var]
            dictvar.add_value(key, expr, literal)
            self.assign2symbol_var[atom.symbol] = symbol_var
            if literal not in self.literal2var:
                self.literal2var[literal] = []
            self.literal2var[literal].append(dictvar)

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
        for var in self.symbol2var.values():
            final_value = var.get_value()
            myprint(var.var, final_value, type(final_value))
            if final_value is None or final_value is ValueStatus.NOT_SET:
                continue
            if type(final_value) == frozenset:
                for value in final_value:
                    if value is None or value is ValueStatus.NOT_SET:
                        continue
                    pyAtom = Set_Value(var.var,evaluator.get_baseType(value),value)
                    myprint(f"adding set atom {pyAtom}",end=" ")
                    clAtom = myClorm.pytocl(pyAtom)
                    myprint(f"= {clAtom}")
                    if not model.contains(clAtom):
                        model.extend([clAtom])
            elif type(final_value) == evaluator.HashableDict or type(final_value) == dict:
                for key, value in final_value.items():
                    if value is None or value is ValueStatus.NOT_SET:
                        continue
                    pyAtom = Multimap_Value(var.var,evaluator.get_baseType(key),key,evaluator.get_baseType(value),value)
                    myprint(f"adding multimap atom {pyAtom}",end=" ")
                    clAtom = myClorm.pytocl(pyAtom)
                    myprint(f"= {clAtom}")
                    if not model.contains(clAtom):
                        model.extend([clAtom])
            else:
                pyAtom = Value(var.var,evaluator.get_baseType(final_value),final_value)
                myprint(f"adding atom {pyAtom}",end=" ")
                clAtom = myClorm.pytocl(pyAtom)
                myprint(f"= {clAtom}")

                if not model.contains(clAtom):
                    model.extend([clAtom])

        
        for var in self.evaluatevars:
            # if var.value is None or var.value is VALUE_NOT_SET:
            #     continue
            pyAtom = Evaluated(var.op, var.args, evaluator.get_baseType(var.get_value()), var.get_value())
            myprint(f"adding evaluate atom {pyAtom}",end=" ")
            clAtom = myClorm.pytocl(pyAtom)
            myprint(f"= {clAtom}")
            if not model.contains(clAtom):
                model.extend([clAtom])

