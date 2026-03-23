from typing import Optional, Sequence, Union

import clingo
import clintest.assertion
import clintest.solver
import clintest.test
from clintest.quantifier import All, Any, First, Last

import constraint_handler
import constraint_handler.evaluator as evaluator
import constraint_handler.myClorm as myClorm


def atoms_from_file(file_name):
    try:
        with open(file_name, "r", encoding="utf-8") as file_handle:
            contents = file_handle.read().split()
            return [clingo.symbol.parse_term(atom) for atom in contents]
    except FileNotFoundError:
        return []


def contains(atom):
    return clintest.assertion.Or(*(clintest.assertion.Contains(atom), TheoryContains(atom)))


def build_expectations(name):
    opt_contains = contains
    absent = lambda atom: clintest.assertion.Not(
        clintest.assertion.Or(*(clintest.assertion.Contains(atom), TheoryContains(atom)))
    )
    expected_all = atoms_from_file(name + ".expected.all")
    test_all = clintest.test.And(*(clintest.test.Assert(All(), opt_contains(atom)) for atom in expected_all))
    expected_any = atoms_from_file(name + ".expected.any")
    test_any = clintest.test.And(*(clintest.test.Assert(Any(), opt_contains(atom)) for atom in expected_any))
    expected_none = atoms_from_file(name + ".expected.none")
    test_none = clintest.test.And(*(clintest.test.Assert(All(), absent(atom)) for atom in expected_none))
    expected_first = atoms_from_file(name + ".expected.first")
    test_first = clintest.test.And(*(clintest.test.Assert(First(), contains(atom)) for atom in expected_first))
    test_exists = (
        clintest.test.Assert(Any(), clintest.assertion.True_())
        if (expected_all or expected_first) and not expected_any
        else clintest.test.True_()
    )
    return clintest.test.And(test_exists, test_all, test_any, test_none, test_first)


def build_reasoning_mode_expectations(name) -> list[tuple[clintest.test.Test, list[str]]]:
    expected_brave = atoms_from_file(name + ".expected.brave")
    test_brave = clintest.test.And(*(clintest.test.Assert(Last(), contains(atom)) for atom in expected_brave))

    expected_cautious = atoms_from_file(name + ".expected.cautious")
    test_cautious = clintest.test.And(*(clintest.test.Assert(Last(), contains(atom)) for atom in expected_cautious))

    return [(test_brave, ["--enum-mode=brave"]), (test_cautious, ["--enum-mode=cautious"])]


class TheoryContains(clintest.assertion.Assertion):
    def __init__(self, symbol: Union[clingo.Symbol, str]) -> None:
        self.__symbol = symbol

    def __repr__(self):
        name = self.__class__.__name__
        return f'{name}("{self.__symbol}")'

    def holds_for(self, model: clingo.solving.Model) -> bool:
        return self.__symbol in model.symbols(theory=True)


class Solver(clintest.solver.Solver):
    def __init__(
        self,
        arguments: Optional[Sequence[str]] = None,
        program: Optional[str] = None,
        files: Optional[Sequence[str]] = None,
        propagator_check_only: bool = False,
    ) -> None:
        self.__arguments = [] if arguments is None else arguments
        self.__program = "" if program is None else program
        self.__files = [] if files is None else files
        self.__propagator_check_only = propagator_check_only

    def solve(self, test: clintest.test.Test) -> None:
        if test.outcome().is_certain():
            return

        ctl = clingo.Control(self.__arguments)

        constraint_handler.add_to_control(ctl, propagator_check_only=self.__propagator_check_only)
        ctl.add(self.__program)

        for file_name in self.__files:
            ctl.load(file_name)
        ctl.ground()

        if not test.outcome().is_certain():
            ctl.solve(
                on_core=test.on_core,
                on_finish=test.on_finish,
                on_model=test.on_model,
                on_unsat=test.on_unsat,
                on_statistics=test.on_statistics,
            )

    def __repr__(self):
        name = self.__class__.__name__
        arguments = repr(self.__arguments)
        program = repr(self.__program)
        files = repr(self.__files)
        prop = repr(self.__propagator_check_only)
        return f"{name}({arguments}, {program}, {files}, {prop})"


class PropPrint(clingo.propagator.Propagator):
    def __init__(self):
        print("creation")

    def init(self, init):
        print("init")

    def propagate(self, ctl, changes):
        for atom in changes:
            print(atom, end=" ")
        print()

    def check(self, ctl):
        print("check", len(ctl.assignment.trail))

    def on_model(self, model):
        value_map = {"b": True, "i": 42, "y": 85, "s": "foo", "x": "foo", "f": 47.1}
        for var, val in value_map.items():
            symbol = clingo.Function(var)
            base_type = myClorm.pytocl(evaluator.get_baseType(val))
            value = myClorm.pytocl(val)
            fact = clingo.Function("value", [symbol, base_type, value])
            print(f"extending with {fact}")
            model.extend([fact])