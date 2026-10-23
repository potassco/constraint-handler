"""Tests for the Preprocessor, PreparedProblem, and Solver workflow interface."""

from pathlib import Path

import pytest

from constraint_handler import (
    ConstraintStore,
    Operation,
    Operator,
    PreparedProblem,
    PreprocessOptions,
    Preprocessor,
    SolveOptions,
    VariableRef,
)
from constraint_handler.domains import Domain
from constraint_handler.internal_input import ValueType
from constraint_handler.static_types import SetOf


def test_preprocessor_workflow() -> None:
    """Verify Preprocessor.add, snapshot isolation, and prepared metadata."""
    x = VariableRef("x")
    y = VariableRef("y")
    s = VariableRef("s")

    store1 = ConstraintStore()
    store1.choose_from_iterator(x, (1, 2))
    store1.default_to(x, 3)

    store2 = ConstraintStore()
    store2.define(y, Operation(Operator.add, (x, 10)))
    store2.set_contain_choose(s, x)
    store2.set_contain(s, 5)
    store2.set_contain_default_to(s, 6)
    store2.ensure(Operation(Operator.lt, (x, y)))

    options = PreprocessOptions(
        arguments=("--opt",), threshold=100, boolean_threshold=10
    )
    preprocessor = Preprocessor(options)
    assert preprocessor.options == options

    preprocessor.add(store1)
    preprocessor.add(store2)

    # Mutating original stores after add must not affect preprocessor
    store1.choose(x, 999)

    prepared, diagnostics = preprocessor.preprocess()
    assert not diagnostics.has_errors
    assert not diagnostics.warnings

    assert prepared.static_types[x] == frozenset({ValueType.integer})
    assert prepared.static_types[y] == frozenset({ValueType.integer})
    assert prepared.static_types[s] == frozenset(
        {SetOf(frozenset({ValueType.integer}), False)}
    )

    assert prepared.domains[x] == Domain(ints=frozenset({1, 2, 3}))
    assert prepared.domains[y] == Domain(ints=frozenset({11, 12, 13}))
    assert prepared.domains[s] == Domain(
        implicit_set_elements=frozenset({1, 2, 3, 5, 6})
    )

    # Adding more to preprocessor after preprocess must not mutate prepared.store
    extra = ConstraintStore()
    extra.define(VariableRef("z"), 42)
    preprocessor.add(extra)
    assert VariableRef("z") not in prepared.store.variables


def test_preprocess_collects_diagnostics_once_for_shared_order() -> None:
    """Verify undefined variables and cycles are reported once via shared EvaluationOrder."""
    store = ConstraintStore()
    undef = VariableRef("undef")
    a = VariableRef("a")
    b = VariableRef("b")
    store.define(a, b)
    store.define(b, a)
    store.ensure(Operation(Operator.add, (undef, 1)))

    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    _, diagnostics = preprocessor.preprocess()

    assert diagnostics.has_errors
    undef_errors = [d for d in diagnostics.errors if d.variable == undef]
    assert len(undef_errors) == 1
    assert (
        len(
            [
                error
                for error in diagnostics.errors
                if "dependency cycle" in error.message
            ]
        )
        == 2
    )


def test_prepared_problem_and_solver_skeleton_methods() -> None:
    """Verify PreparedProblem and Solver session creation and unimplemented stubs."""
    preprocessor = Preprocessor(PreprocessOptions())
    prepared, _ = preprocessor.preprocess()

    solve_opts = SolveOptions(arguments=("0",))
    solver = prepared.create_solver(solve_opts)
    assert solver.problem is prepared
    assert solver.options == solve_opts

    with pytest.raises(NotImplementedError):
        preprocessor.add_context("ctx", object())
    with pytest.raises(NotImplementedError):
        prepared.dump(Path("problem.ch-prepared"))
    with pytest.raises(NotImplementedError):
        PreparedProblem.load(Path("problem.ch-prepared"))
    with pytest.raises(NotImplementedError):
        solver.add_context("ctx", object())
    with pytest.raises(NotImplementedError):
        solver.preset({VariableRef("x"): 1})
    with pytest.raises(NotImplementedError):
        solver.enforce_query(True)
    with pytest.raises(NotImplementedError):
        solver.solve()
