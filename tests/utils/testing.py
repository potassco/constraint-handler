import os
from collections.abc import Sequence
from dataclasses import dataclass, field

import clingo
import clintest.assertion
import clintest.solver
import clintest.test
from clingo import SolveResult
from clintest.assertion import Assertion
from clintest.outcome import Outcome
from clintest.quantifier import All, Any, Exact, Finished, First, Last, Quantifier

import constraint_handler
from constraint_handler.engine import Engine, compile
from constraint_handler.propagator.PropagatorConstants import OPTIMIZATION_STAGE_ATOM
from constraint_handler.reasoning_modes.reasoning_modes_propagator import ReasoningMode


@dataclass
class TestingOptions:
    clingo_options: list[str] = field(default_factory=list)
    add_to_ctl_options: dict[str, ReasoningMode] = field(default_factory=dict)


def atoms_from_file(file_name: str) -> list[clingo.Symbol]:
    try:
        with open(file_name, "r", encoding="utf-8") as file_handle:
            return [clingo.symbol.parse_term(line) for raw_line in file_handle if (line := raw_line.strip())]
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


def build_expectations(name) -> tuple[list[tuple[clintest.test.Test, TestingOptions]], dict[str, str]]:
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

    if test_noargs or expected_stats.keys() & {"tight", "choices"}:
        tests.append((clintest.test.And(*test_noargs), TestingOptions()))

    test_brave = [clintest.test.Assert(Last(), contains(atom)) for atom in atoms_from_file(name + "brave")]
    if test_brave:
        tests.append((clintest.test.And(*test_brave), TestingOptions(clingo_options=["--enum-mode=brave"])))

    test_cautious = [clintest.test.Assert(Last(), contains(atom)) for atom in atoms_from_file(name + "cautious")]
    if test_cautious:
        tests.append((clintest.test.And(*test_cautious), TestingOptions(clingo_options=["--enum-mode=cautious"])))

    for mode in (ReasoningMode.UNION, ReasoningMode.INTERSECTION, ReasoningMode.SUPREMUM, ReasoningMode.INFIMUM):
        test_mode = [clintest.test.Assert(Last(), contains(atom)) for atom in atoms_from_file(name + mode.name.lower())]
        if test_mode:
            tests.append((clintest.test.And(*test_mode), TestingOptions(add_to_ctl_options={"reasoning_mode": mode})))

    test_optimize = []
    for atom in atoms_from_file(name + "optall"):
        test_optimize.append(AssertOptimal(All(), contains(atom)))
    for atom in atoms_from_file(name + "optany"):
        test_optimize.append(AssertOptimal(Any(), contains(atom)))
    for atom in atoms_from_file(name + "optnone"):
        test_optimize.append(AssertOptimal(All(), absent(atom)))
    if test_optimize:
        tests.append((clintest.test.And(*test_optimize), TestingOptions(clingo_options=["--opt-mode=optN"])))

    return tests, expected_stats


class TheoryContains(clintest.assertion.Assertion):
    def __init__(self, symbol: clingo.Symbol | str) -> None:
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


def assert_statistics(statistics: dict, expected: dict[str, str]) -> None:
    if "tight" in expected:
        actual = statistics["problem"]["lp"]["sccs"] == 0.0
        assert actual == (expected["tight"] == "true"), f"tight: expected {expected['tight']}, got {actual}"
    if "choices" in expected:
        actual = statistics["solving"]["solvers"]["choices"] > 0.0
        assert actual == (expected["choices"] == "true"), f"choices: expected {expected['choices']}, got {actual}"


class Solver(clintest.solver.Solver):
    def __init__(
        self,
        arguments: Sequence[str] | None = None,
        program: str | None = None,
        files: Sequence[str] | None = None,
        engine: Engine = compile,
        add_to_ctl_options: dict[str, ReasoningMode] | None = None,
    ) -> None:
        self.__arguments = [] if arguments is None else arguments
        self.__program = "" if program is None else program
        self.__files = [] if files is None else files
        self.__engine = engine
        self.__add_to_ctl_options = {} if add_to_ctl_options is None else add_to_ctl_options

    def solve(self, test: clintest.test.Test, expected_stats: dict[str, str] = {}) -> None:
        if test.outcome().is_certain() and not expected_stats:
            return

        ctl = clingo.Control([*self.__arguments, "--stats=2"])

        constraint_handler.add_to_control(ctl, engine=self.__engine, **self.__add_to_ctl_options)
        ctl.add(self.__program)

        for file_name in self.__files:
            ctl.load(file_name)
        ctl.ground()

        ctl.solve(
            on_core=test.on_core,
            on_finish=test.on_finish,
            on_model=test.on_model,
            on_unsat=test.on_unsat,
            on_statistics=test.on_statistics,
        )
        assert_statistics(ctl.statistics, expected_stats)

    def __repr__(self):
        name = self.__class__.__name__
        arguments = repr(self.__arguments)
        program = repr(self.__program)
        files = repr(self.__files)
        engine = repr(self.__engine)
        add_to_ctl_options = repr(self.__add_to_ctl_options)
        return f"{name}({arguments}, {program}, {files}, {engine}, {add_to_ctl_options})"
