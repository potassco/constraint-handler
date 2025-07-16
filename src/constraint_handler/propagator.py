import clingo
import constraint_handler.myClorm as myClorm
import constraint_handler.evaluator as evaluator

from collections import defaultdict

from typing import Any, Dict
import queue

class ConstraintHandlerPropagator:

    def __init__(self):
        self.ensure_symbol_lit: Dict[clingo.symbol,int] = {}
        self.assign_symbol_lit: Dict[clingo.symbol,int] = {}

        self.evaluated: Dict[clingo.symbol, Any] = {}

        self.assign_dependencies: Dict[clingo.symbol, set[clingo.symbol]] = defaultdict(set)

    def init(self, ctl: clingo.PropagateInit):
        self.get_ensure(ctl)
        self.get_assign(ctl)

        print(self.ensure_symbol_lit)
        print(self.assign_symbol_lit)

        # readable = { key : val for key,val in self.ensure_symbol_lit.items() }
        # readable.update({ key : val for key,val in self.assign_symbol_lit.items() })
        # print(readable)

        print("Variable dependencies for assignments:")
        for var, deps in self.assign_dependencies.items():
            print(f"{var}: {deps}")
        print("#"*50)

        print("INIT DONE")
        print("#"*50)

    def check(self, ctl: clingo.PropagateControl):
        # return
        print("CHECKING")

        evaluations: Dict[clingo.Symbol, Any] = self.evaluated_solver_assignment(ctl)
        self.check_ensure(evaluations)

    def check_ensure(self, evaluations: Dict[clingo.Symbol, Any]) -> None:
        """
        This method checks the ensure constraints in the propagator.
        It evaluates the expressions and checks if they hold true.
        If any ensure constraint is violated, it adds a nogood and propagates
        """
        for symbol, lit in self.ensure_symbol_lit.items():
            name, expr = self.parse_ensure(symbol)
            print(f"Checking ensure: {name} := {str(expr)} with literal {lit}")
            evaluated = evaluator.evaluate_expr(evaluations, expr)
            # if evaluated is None or not evaluated:
            print(f"Ensure constraint {name}: {expr} evaluated to {evaluated}")
            deps = set()
            for var in evaluator.collectVars(expr):
                deps.update(self.get_base_dependencies(var))
            print(f"Base dependencies: {deps}")
    
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
        
        # In the future, we can do a order on which expressions to evaluate first
        # So that we do only one pass, for now this is easier to implement
        # Also, we can split the expressions into the ones evaluated at initialization
        # and the other ones so that we only look at the relevant ones in this pass
        while changed and iterations < max_iterations:
            iterations += 1
            changed = False
            print(f"Evaluating... Iteration {iterations}")
            print(f"Current evaluations: {evaluations}")
            for symbol, lit in self.assign_symbol_lit.items():
                name, var, expr = self.parse_assign(symbol)
                print(f"Looking at variable {var} with expression {expr} and literal {lit} with assignment {ctl.assignment.is_true(lit)}")
                if var in evaluations:
                    print(f"Variable {var} already evaluated as {evaluations[var]}")
                    continue

                if ctl.assignment.is_true(lit):
                    print(f"Literal {lit} is true, evaluating expression {expr}")
                    print(f"Evaluated dict: {evaluations}")
                    evaluated = evaluator.evaluate_expr(evaluations, expr)
                    if evaluated is not None:
                        changed = True
                        evaluations[var] = evaluated
                        print(f"temp Evaluated stored: {var} = {evaluated}")

        return evaluations

    def parse_assign(self, symbol: clingo.Symbol):
        name = myClorm.cltopy(symbol.arguments[0])
        var = myClorm.cltopy(symbol.arguments[1])
        expr = myClorm.cltopy(symbol.arguments[2],evaluator.Expr)
        return name, var, expr

    def parse_ensure(self, symbol: clingo.Symbol):
        name = myClorm.cltopy(symbol.arguments[0])
        expr = myClorm.cltopy(symbol.arguments[1],evaluator.Expr)
        return name, expr

    def get_ensure(self, ctl: clingo.PropagateInit):
        for atom in ctl.symbolic_atoms.by_signature("propagator_ensure",2):

            self.ensure_symbol_lit[atom.symbol] = ctl.solver_literal(atom.literal)
            
            name, expr = self.parse_ensure(atom.symbol)
            print(f"ensure: {name} := {str(expr)} has literal {atom.literal} and solver literal {self.ensure_symbol_lit[atom.symbol]}")
            print(f"variables in {str(expr)} are {evaluator.collectVars(expr)}")
            print(f"Evaluated: {evaluator.evaluate_expr({},expr)}")

    def get_assign(self, ctl: clingo.PropagateInit):
        for atom in ctl.symbolic_atoms.by_signature("propagator_assign",3):
            self.assign_symbol_lit[atom.symbol] = ctl.solver_literal(atom.literal)
            
            name, var, expr = self.parse_assign(atom.symbol)
            print(f"assign: {name} and var {var} := {str(expr)} has literal {atom.literal} and solver literal {self.assign_symbol_lit[atom.symbol]}")
            print(f"variables in {str(expr)} are {evaluator.collectVars(expr)}")

            self.assign_dependencies[var] = evaluator.collectVars(expr)

            # Any facts assigning to a variable are stored immediately
            # in the evaluated dict
            print(f"Evaluated dict: {self.evaluated}")
            print(f"Evaluated: {evaluator.evaluate_expr(self.evaluated, expr)}")
            if ctl.assignment.is_true(ctl.solver_literal(atom.literal)):
                evaluated = evaluator.evaluate_expr(self.evaluated, expr)
                if evaluated is not None:
                    self.evaluated[var] = evaluated
                    print(f"Evaluated stored: {var} = {evaluated}")

    def get_base_dependencies(self, symbol: clingo.Symbol) -> set[clingo.Symbol]:
        """
        Returns the base dependencies of a symbol.
        This is used to determine which variables are needed in the nogood when an ensure is violated.
        """
        # For now, this justs gets the variables that have a value assigned to them directly
        # Later, we have to also check the solver literal to see if it is a fact or not.
        # Probably, we only want to consider the variables that are NOT facts
        # Since adding facts to the nogood does not bring any value
        
        deps = queue.Queue()
        for dep in self.assign_dependencies[symbol]:
            deps.put(dep)

        base_deps = set()
        while not deps.empty():
            dep = deps.get()
            if len(self.assign_dependencies[dep]) > 0:
                for sub_dep in self.assign_dependencies[dep]:
                    deps.put(sub_dep)

            else:
                base_deps.add(dep)

        return base_deps