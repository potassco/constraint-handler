import clingo
import constraint_handler.myClorm as myClorm
import constraint_handler.evaluator as evaluator

from collections import defaultdict

from typing import Any, Dict, NamedTuple, List, Tuple
import queue

class Val(NamedTuple):
    name: clingo.Symbol
    type_: evaluator.BaseType | None
    value: bool | int | float | str | clingo.Symbol


class ConstraintHandlerPropagator:

    def __init__(self):
        self.ensure_symbol_lit: Dict[clingo.symbol,int] = {}
        self.ensure_symbol_parsed: Dict[clingo.symbol, Tuple[str, evaluator.Expr]] = {}
        self.assign_symbol_lit: Dict[clingo.symbol,int] = {}
        self.assign_symbol_parsed: Dict[clingo.symbol, Tuple[str, clingo.Symbol, evaluator.Expr]] = {}

        # holds evaluations of assignments in the root level
        self.evaluated: Dict[clingo.symbol, Any] = {}

        # holds the evuluations after checking on a complete assignment
        # Used to add symbols to the model
        self.final_eval: Dict[clingo.symbol, Any] = {}

        self.reasons: Dict[clingo.symbol, set[int]] = defaultdict(set)

        self.model: List[clingo.Symbol] = []


    def init(self, ctl: clingo.PropagateInit):
        self.get_ensure(ctl)
        self.get_assign(ctl)

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
        evaluations: Dict[clingo.Symbol, Any] = self.evaluated_solver_assignment(ctl)
        print(f"after evaluation, the reasons are {self.reasons}")
        
        backtrack = self.check_ensure(ctl, evaluations)
        print(f"CHECK DONE, backtracking {backtrack}")
        if backtrack:
            return
        
        if ctl.assignment.is_total:
            self.final_eval = evaluations

    # def propagate(self, ctl: clingo.PropagateControl):
    #     self.reasons = defaultdict(set)
    #     evaluations: Dict[clingo.Symbol, Any] = self.evaluated_solver_assignment(ctl)
    #     print(f"after evaluation, the reasons are {self.reasons}")
    
    #     backtrack = self.check_ensure(ctl, evaluations)
    #     print(f"PROPAGATION DONE, backtracking {backtrack}")

    def check_ensure(self, ctl: clingo.PropagateControl, evaluations: Dict[clingo.Symbol, Any]) -> bool:
        """
        This method checks the ensure constraints in the propagator.
        It evaluates the expressions and checks if they hold true.
        If any ensure constraint is violated, it adds a nogood and propagates
        """
        for symbol, lit in self.ensure_symbol_lit.items():
            name, expr = self.ensure_symbol_parsed[symbol]
            print(f"Checking ensure: {name} := {str(expr)} with literal {lit}")
            evaluated = evaluator.evaluate_expr(evaluations, expr)

            print(f"Ensure constraint {name}: {expr} evaluated to {evaluated}")
            if evaluated is None:
                continue

            if not evaluated:
                nogood = {lit}.union(*(self.reasons[dvar] for dvar in evaluator.collectVars(expr)))
                print(f"the reason for {expr} being {evaluated} is {nogood} based on vars in {evaluator.collectVars(expr)}")
                if ctl.add_nogood(list(nogood)):
                    assert False, "Added violated constraint but solver did not detect it"
                return False
        
        print("Ensures checked")
        return True
    
    def evaluated_solver_assignment(self, ctl: clingo.PropagateControl) -> Dict[clingo.symbol, Any]:
        """
        This method evaluates the expressions assigned to variables in the propagator.
        It uses the current solver assignment to determine which expressions to evaluate.
        It returns a dictionary with the evaluated variables and their values.
        """
        evaluations: Dict[clingo.Symbol, Any] = self.evaluated.copy()
        changed: bool = True
        max_iterations: int = 10 # these 2 are just for safety in the testing phase
        iterations: int = 0
        
        # Each loop evaluates the assignments
        # and updates the evaluations dictionary
        while changed and iterations < max_iterations:
            iterations += 1
            changed = False
            print(f"Evaluating... Iteration {iterations}\nCurrent evaluations: {evaluations}")
            for symbol, lit in self.assign_symbol_lit.items():
                name, var, expr = self.parse_assign(symbol)
                print(f"Looking at variable {var} with expression {expr} and literal {lit} with assignment {ctl.assignment.is_true(lit)}")
                if var in evaluations:
                    continue

                if ctl.assignment.is_true(lit):
                    evaluated = evaluator.evaluate_expr(evaluations, expr)
                    if evaluated is not None:
                        print(f"expression {expr} evaluated to {evaluated} for variable {var} (True literal {lit})")
                        changed = True
                        evaluations[var] = evaluated
                        self.reasons[var] = { lit }

                        self.reasons[var] = self.reasons[var].union(*(self.reasons[dvar] for dvar in list(evaluator.collectVars(expr))))
                        print(f"the reason(s) for {var} taking value {evaluated} is {self.reasons[var]}")

        return evaluations
    
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
        for atom in ctl.symbolic_atoms.by_signature("propagator_ensure",2):
            self.ensure_symbol_lit[atom.symbol] = ctl.solver_literal(atom.literal)
            self.ensure_symbol_parsed[atom.symbol] = self.parse_ensure(atom.symbol)
        
    def get_assign(self, ctl: clingo.PropagateInit):
        for atom in ctl.symbolic_atoms.by_signature("propagator_assign",3):
            self.assign_symbol_lit[atom.symbol] = ctl.solver_literal(atom.literal)
            
            name, var, expr = self.parse_assign(atom.symbol)
            self.assign_symbol_parsed[atom.symbol] = (name, var, expr)

            # Any facts assigning to a variable are stored immediately
            # in the evaluated dict
            if ctl.assignment.is_true(ctl.solver_literal(atom.literal)):
                evaluated = evaluator.evaluate_expr(self.evaluated, expr)
                if evaluated is not None:
                    self.evaluated[var] = evaluated

    def on_model(self,model):
        self.model = []
        for (var, val) in self.final_eval.items():
            pyAtom = Val(var,evaluator.get_baseType(val),val)
            print(f"adding atom {pyAtom}",end=" ")
            clAtom = myClorm.pytocl(pyAtom)
            print(f"= {clAtom}")
            if not model.contains(clAtom):
                model.extend([clAtom])
                self.model.append(clAtom)

