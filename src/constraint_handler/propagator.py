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

    def __init__(self, expr: evaluator.Expr):
        self.expr = expr
        self.value: Any = None

    def evaluate(self, evaluations: Dict[clingo.Symbol, Any]) -> bool:
        """Evaluate the expression and return True if the value has changed."""
        value = evaluator.evaluate_expr(evaluations, self.expr)
        if value == self.value:
            return False
        self.value = value
        return True

    def __eq__(self, other):
        if not isinstance(other, VariableValue):
            return False
        return self.expr == other.expr

class Variable:
    """
        A variable with a name and a value expression.
        This is supposed to mirror the assign/3 atom(also propagator_assign/3) in the ASP encoding.
    """
    def __init__(self, name: clingo.Symbol, expr: clingo.Symbol):
        self.name = name
        self.value: VariableValue = VariableValue(expr)

    def evaluate(self, evaluations: Dict[clingo.Symbol, Any]) -> bool:
        """Evaluate the expression and return True if the value has changed."""
        return self.value.evaluate(evaluations)

    def get_value(self) -> Any:
        return self.value.value

    def __eq__(self, other):
        if not isinstance(other, Variable):
            assert False, "Variable can only be compared to another Variable"
        return self.name == other.name and self.value == other.value


class SetVariable:
    """
        A set variable with a name and a set of value expressions.
        This is supposed to mirror the set_declare/2 and set_assign/3 atom in the ASP encoding.
    """
    def __init__(self, name: clingo.Symbol, args: List[evaluator.Expr] = None):
        self.name = name
        self.value: set[Any] = set()
        if args is not None:
            self.value = {VariableValue(arg) for arg in args}

    def add_argument(self, arg: evaluator.Expr) -> None:
        self.value.add(VariableValue(arg))

    def __contains__(self, item):
        return item in self.value
    
    def get_value(self) -> set[Any]:
        return {arg.value for arg in self.value if arg.value is not None}

    def evaluate(self, evaluations: Dict[clingo.Symbol, Any]) -> bool:
        """Evaluate all arguments and return True if any value has changed."""
        changed = False
        for arg in self.value:
            changed |= arg.evaluate(evaluations)
        return changed

    def __eq__(self, value):
        if not isinstance(value, SetVariable):
            assert False, "SetVariable can only be compared to another SetVariable"
        return self.name == value.name and self.value == value.value

def make_dict_from_set_variables(variables: Sequence[SetVariable]) -> Dict[clingo.Symbol, set[Any]]:
    result: Dict[clingo.Symbol, set[Any]] = {}
    for var in variables:
        result[var.name] = var.get_value()
    return result

def make_dict_from_variable(variables: Sequence[Variable]) -> Dict[clingo.Symbol, Any]:
    result: Dict[clingo.Symbol, Any] = {}
    for var in variables:
        if var.get_value() is not None:
            result[var.name] = var.get_value()
    return result

class ConstraintHandlerPropagator:

    def __init__(self):
        self.ensure_symbol_lit: Dict[clingo.symbol,int] = {}
        self.ensure_symbol_parsed: Dict[clingo.symbol, Tuple[str, evaluator.Expr]] = {}
        self.assign_symbol_lit: Dict[clingo.symbol,int] = {}
        self.assign_symbol_parsed: Dict[clingo.symbol, Tuple[str, clingo.Symbol, evaluator.Expr]] = {}

        # holds evaluations of assignments in the root level
        self.evaluated: Dict[clingo.symbol, Any] = {}
        self.evaluated_sets: Dict[clingo.symbol, set[Any]] = {}
        self.evaluation_level: Dict[clingo.symbol, int] = {}
        self.evaluation_level_sets: Dict[Tuple[clingo.symbol, Any], int] = {}

        # holds the evuluations after checking on a complete assignment
        # Used to add symbols to the model
        self.final_eval: Dict[clingo.symbol, Any] = {}

        self.reasons: Dict[clingo.symbol, set[int]] = defaultdict(set)

        self.model: List[clingo.Symbol] = []


    def init(self, ctl: clingo.PropagateInit):
        self.get_ensure(ctl)
        self.get_assign(ctl)
        self.set_declarations(ctl)
        # ctl.check_mode = clingo.PropagatorCheckMode.Both

        print("INIT DONE")
        print("#"*50)

    def check(self, ctl: clingo.PropagateControl):
        # return
        print("CHECKING")
        # print(f"Is assignment total: {ctl.assignment.is_total}")
        # if not ctl.assignment.is_total:
        #     print("Assignment is not total, cannot check ensures")
        #     return
        # print(f"Assignment is total({ctl.assignment.is_total}), checking ensures")

        self.reasons = defaultdict(set)
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
            print(f"Evaluating... Iteration {iterations}\nCurrent evaluations: {self.evaluated | self.evaluated_sets}")
            for symbol, lit in self.assign_symbol_lit.items():
                _, var, expr = self.assign_symbol_parsed[symbol]
                # if var in self.evaluated:
                #     # this only triggers for non set variables
                #     continue
                print(f"Looking at variable {var} with expression {expr} and literal {lit} with assignment {ctl.assignment.is_true(lit)}")

                evaluated = self.evaluate_expr(ctl, symbol, lit)
                if evaluated is not None:
                    print(f"expression {expr} evaluated to {evaluated} for variable {var} (True literal {lit})")
                    changed = True
                    self.reasons[var] = { lit }
                    self.reasons[var] = self.reasons[var].union(*(self.reasons[dvar] for dvar in list(evaluator.collectVars(expr))))
                    print(f"the reason(s) for {var} taking value {evaluated} is {self.reasons[var]}")
    
    def undo(self, thread_id: int, assignment: clingo.Assignment, changes: Sequence[int]) -> None:
        """
        Resets the evaluations and reasons based on the current assignment.
        """
        print(f"UNDOING for decision level {assignment.decision_level} with changes {changes}")
        to_del = set()
        for var, level in self.evaluation_level.items():
            if level >= assignment.decision_level:
                print(f"Removing {var} from evaluated and reasons due to decision level {level} >= {assignment.decision_level}")
                if var in self.evaluated:
                    del self.evaluated[var]
                if var in self.reasons:
                    del self.reasons[var]

                to_del.add(var)

        for var in to_del:
            del self.evaluation_level[var]

        
        for var, level in self.evaluation_level_sets.items():
            if level >= assignment.decision_level:
                print(f"Removing {var} from evaluated and reasons due to decision level {level} >= {assignment.decision_level}")
                if var in self.evaluated_sets:
                    del self.evaluated_sets[var]
                if var in self.reasons:
                    del self.reasons[var]

                to_del.add(var)

        for var in to_del:
            del self.evaluation_level_sets[var]

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
            self.initial_assign_eval(ctl, atom)

    def set_declarations(self, ctl: clingo.PropagateInit):

        for atom in ctl.symbolic_atoms.by_signature(AtomNames.SET_DECLARE, 2):
            # name = myClorm.cltopy(atom.symbol.arguments[0])
            var = myClorm.cltopy(atom.symbol.arguments[1])
            self.evaluated[var] = set()

        for atom in ctl.symbolic_atoms.by_signature(AtomNames.SET_ASSIGN, 3):
            self.initial_assign_eval(ctl, atom)

    def initial_assign_eval(self, ctl, atom):
        literal = ctl.solver_literal(atom.literal)
        self.assign_symbol_lit[atom.symbol] = literal
        
        name, var, expr = self.parse_assign(atom.symbol)
        self.assign_symbol_parsed[atom.symbol] = (name, var, expr)

        # Any facts assigning to a variable are stored immediately
        # in the evaluated dict

        self.evaluate_expr(ctl, atom.symbol, literal)

    def evaluate_expr(self, ctl, symbol, literal):
        evaluated = None
        name, var, expr = self.assign_symbol_parsed[symbol]
        if ctl.assignment.is_true(literal):
            evaluated = evaluator.evaluate_expr(self.evaluated | self.evaluated_sets, expr)
            if evaluated is not None:
                if type(evaluated) == set:
                        if None in evaluated:
                            # if something in the set is undefined
                            # we do not add it to as a value
                            evaluated.remove(None)
                        evaluated = frozenset(evaluated)

                if symbol.name == AtomNames.SET_ASSIGN:
                    if var not in self.evaluated_sets:
                        self.evaluated_sets[var] = set()
                    if evaluated in self.evaluated_sets[var]:
                        # the value is already in the set, nothing to do
                        return None
                    print(f"initially adding to set {var} the value {evaluated}")
                    self.evaluated_sets[var].add(evaluated)
                    # add both so we know at which level the value was added to the set
                    # if it was not evaluated before, set it to the current level
                    self.evaluation_level_sets[(symbol, evaluated)] = min(ctl.assignment.decision_level, 
                                                                          self.evaluation_level_sets.get((symbol, evaluated), 100000000))
                elif symbol.name == AtomNames.ASSIGN:
                    if evaluated == self.evaluated.get(var, None):
                        print(f"the variable already has value {evaluated}, nothing to do")
                        return None
                    self.evaluated[var] = evaluated
                    self.evaluation_level[symbol] = ctl.assignment.decision_level
                else:
                    assert False, "Unknown atom name in initial assignment evaluation"
        else:
            # if not a fact, we watch it
            ctl.add_watch(literal)

        return evaluated

    def on_model(self,model):
        self.model = []
        for (var, val) in self.evaluated.items():
            pyAtom = Val(var,evaluator.get_baseType(val),val)
            print(f"adding atom {pyAtom}",end=" ")
            clAtom = myClorm.pytocl(pyAtom)
            print(f"= {clAtom}")
            if not model.contains(clAtom):
                model.extend([clAtom])
                self.model.append(clAtom)

