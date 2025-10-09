from typing import Optional, Sequence, Union

import clingo
import clingo.symbol
import clintest.assertion
import clintest.solver
import clintest.test
from clintest.quantifier import All, Any, First
from clintest.test import And, Assert

import constraint_handler.evaluator as evaluator
import constraint_handler.myClorm as myClorm


def atoms_from_file(file_name):
    try:
        with open(file_name, "r") as f:
            contents = f.read().split()
            return [clingo.symbol.parse_term(atom) for atom in contents]
    except FileNotFoundError:
        # print("missing file",file_name)
        return []


def build_expectations(name):
    contains = lambda a: clintest.assertion.Or(*(clintest.assertion.Contains(a), TheoryContains(a)))
    expected_all = atoms_from_file(name + ".expected.all")
    test_all = And(*(Assert(All(), contains(a)) for a in expected_all))
    expected_any = atoms_from_file(name + ".expected.any")
    test_any = And(*(Assert(Any(), contains(a)) for a in expected_any))
    expected_any = atoms_from_file(name + ".expected.first")
    test_any = And(*(Assert(First(), contains(a)) for a in expected_any))
    return And(test_all, test_any)


class TheoryContains(clintest.assertion.Assertion):
    def __init__(self, symbol: Union[clingo.Symbol, str]) -> None:
        # self.__symbol = _into_symbol(symbol)
        self.__symbol = symbol

    def __repr__(self):
        name = self.__class__.__name__
        return f'{name}("{self.__symbol}")'

    def holds_for(self, model: clingo.solving.Model) -> bool:
        return self.__symbol in model.symbols(theory=True)


class SolverWithPropagators(clintest.solver.Solver):

    def __init__(
        self,
        arguments: Optional[Sequence[str]] = None,
        program: Optional[str] = None,
        files: Optional[Sequence[str]] = None,
        propagators: list[clingo.propagator.Propagator] = [],
    ) -> None:
        self.__arguments = [] if arguments is None else arguments
        self.__program = "" if program is None else program
        self.__files = [] if files is None else files
        self.__propgators = [] if not len(propagators) else propagators

    def wrap(self, test, props, method):
        def fn(*args, **kwargs):
            for prop in props:
                if hasattr(prop, method) and callable(getattr(prop, method)):
                    getattr(prop, method)(*args, **kwargs)
            getattr(test, method)(*args, **kwargs)

        return fn

    def solve(self, test: clintest.test.Test) -> None:
        ctl = clingo.Control(self.__arguments)

        ctl.add("base", [], self.__program)

        for file in self.__files:
            ctl.load(file)

        ctl.ground([("base", [])])
        props = [prop(ctl) for prop in self.__propgators]
        for prop in props:
            ctl.register_propagator(prop)

        if not test.outcome().is_certain():
            ctl.solve(
                on_core=self.wrap(test, props, "on_core"),
                on_finish=self.wrap(test, props, "on_finish"),
                on_model=self.wrap(test, props, "on_model"),
                on_unsat=self.wrap(test, props, "on_unsat"),
                on_statistics=self.wrap(test, props, "on_statistics"),
            )

    def __repr__(self):
        name = self.__class__.__name__
        arguments = repr(self.__arguments)
        program = repr(self.__program)
        files = repr(self.__files)
        props = repr(self.__propagators)
        return f"{name}({arguments}, {program}, {files}, {props})"


class PropPrint(clingo.propagator.Propagator):
    def __init__(self, ctl):
        print("creation")

    def init(self, init):
        print("init")

    def propagate(self, ctl, changes):
        for a in changes:
            print(a, end=" ")
        print()

    def check(self, ctl):
        print("check", len(ctl.assignment.trail))

    def on_model(self, _model):
        value_map = {"b": True, "i": 42, "y": 85, "s": "foo", "x": "foo", "f": 47.1}
        for var, val in value_map.items():
            x = clingo.Function(var)
            t = myClorm.pytocl(evaluator.get_baseType(val))
            v = myClorm.pytocl(val)
            fact = clingo.Function("value", [x, t, v])
            print(f"extending with {fact}")
            _model.extend([fact])
