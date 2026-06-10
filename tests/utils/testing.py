import os
from typing import Optional, Sequence, Union

import clingo
import clintest.assertion
import clintest.solver
import clintest.test
from clingo import SolveResult
from clintest.assertion import Assertion
from clintest.outcome import Outcome
from clintest.quantifier import All, Any, Exact, Finished, First, Last, Quantifier

import constraint_handler
import constraint_handler.evaluator as evaluator
import constraint_handler.myClorm as myClorm
from constraint_handler.PropagatorConstants import OPTIMIZATION_STAGE_ATOM


def atoms_from_file(file_name):
    try:
        with open(file_name, "r", encoding="utf-8") as file_handle:
            contents = file_handle.read().split()
            return [clingo.symbol.parse_term(atom) for atom in contents]
    except FileNotFoundError:
        return []


def stats_from_file(file_name: str) -> dict[str, str]:
    try:
        with open(file_name, "r", encoding="utf-8") as file_handle:
            return {
                key: value
                for raw_line in file_handle
                if (line := raw_line.strip())
                for key, value in [line.split("=", 1)]
            }
    except FileNotFoundError:
        return {}


def contains(atom):
    return clintest.assertion.Or(clintest.assertion.Contains(atom), TheoryContains(atom))


def absent(atom):
    return clintest.assertion.Not(clintest.assertion.Or(clintest.assertion.Contains(atom), TheoryContains(atom)))


def build_expectations(name) -> list[tuple[clintest.test.Test, list[str]]]:
    name = name + ".expected."
    tests = []

    test_noargs = []
    for atom in atoms_from_file(name + "all"):
        test_noargs.append(clintest.test.Assert(All(), contains(atom)))
    for atom in atoms_from_file(name + "any"):
        test_noargs.append(clintest.test.Assert(Any(), contains(atom)))
    for atom in atoms_from_file(name + "none"):
        test_noargs.append(clintest.test.Assert(All(), absent(atom)))
    for atom in atoms_from_file(name + "first"):
        test_noargs.append(clintest.test.Assert(First(), contains(atom)))
    for atom in atoms_from_file(name + "last"):
        test_noargs.append(clintest.test.Assert(Last(), contains(atom)))
    expected_stats = stats_from_file(name + "stats")
    if "models" in expected_stats:
        expected_models = int(expected_stats["models"])
        test_noargs.append(clintest.test.Assert(Exact(expected_models), clintest.assertion.True_()))
    else:
        satisfiability_implicit = any(
            (os.path.isfile(name + extension) for extension in ("all", "none", "first", "last", "optall", "optnone"))
        )
        satisfiability_asserted = any(
            (os.path.isfile(name + extension) for extension in ("any", "brave", "cautious", "optany"))
        )
        satisfiable = clintest.test.Assert(Any(), clintest.assertion.True_())
        if satisfiability_implicit and not satisfiability_asserted:
            test_noargs.append(satisfiable)

    if test_noargs:
        tests.append((clintest.test.And(*test_noargs), []))

    test_brave = (clintest.test.Assert(Last(), contains(atom)) for atom in atoms_from_file(name + "brave"))
    if test_brave:
        tests.append((clintest.test.And(*test_brave), ["--enum-mode=brave"]))

    test_cautious = (clintest.test.Assert(Last(), contains(atom)) for atom in atoms_from_file(name + "cautious"))
    if test_cautious:
        tests.append((clintest.test.And(*test_cautious), ["--enum-mode=cautious"]))

    test_optimize = []
    for atom in atoms_from_file(name + "optall"):
        test_optimize.append(AssertOptimal(All(), contains(atom)))
    for atom in atoms_from_file(name + "optany"):
        test_optimize.append(AssertOptimal(Any(), contains(atom)))
    for atom in atoms_from_file(name + "optnone"):
        test_optimize.append(AssertOptimal(All(), absent(atom)))
    if test_optimize:
        tests.append((clintest.test.And(*test_optimize), ["--opt-mode=optN"]))

    return tests


class TheoryContains(clintest.assertion.Assertion):
    def __init__(self, symbol: Union[clingo.Symbol, str]) -> None:
        self.__symbol = symbol

    def __repr__(self):
        name = self.__class__.__name__
        return f'{name}("{self.__symbol}")'

    def holds_for(self, model: clingo.solving.Model) -> bool:
        return self.__symbol in model.symbols(theory=True)


class AssertOptimal(clintest.test.Test):
    def __init__(self, quantifier: Quantifier, assertion: Assertion) -> None:
        self.__quantifier = quantifier
        self.__assertion = assertion

    def __repr__(self):
        name = self.__class__.__name__
        quantifier = repr(self.__quantifier)
        assertion = repr(self.__assertion)
        return f"{name}({quantifier}, {assertion})"

    def __str__(self):
        return os.linesep.join(
            [
                f"[{self.outcome()}] {self.__class__.__name__}",
                f"    quantifier: {self.__quantifier}",
                f"    assertion:  {self.__assertion}",
            ]
        )

    def on_model(self, _model: clingo.solving.Model) -> bool:
        propagator_optimality_atom = clingo.Function(OPTIMIZATION_STAGE_ATOM, [clingo.Number(2)])

        if not self.__quantifier.outcome().is_certain() and (
            _model.optimality_proven or propagator_optimality_atom in _model.symbols(atoms=True)
        ):
            self.__quantifier.consume(self.__assertion.holds_for(_model))

        return not self.__quantifier.outcome().is_certain()

    def on_finish(self, result: SolveResult) -> None:
        self.__quantifier = Finished(self.__quantifier)

    def outcome(self) -> Outcome:
        return self.__quantifier.outcome()


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
