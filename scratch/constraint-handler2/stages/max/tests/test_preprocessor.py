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
from constraint_handler.python_input import Expr
from constraint_handler.static_types import SetOf


@pytest.mark.parametrize(
    ("op", "value"),
    (
        (Operator.conj, True),
        (Operator.disj, False),
        (Operator.lxor, False),
        (Operator.leqv, True),
    ),
)
def test_preprocess_nullary_boolean_operators(op: Operator, value: bool) -> None:
    """Accept nullary Boolean identities through all preprocessing passes."""
    store = ConstraintStore()
    result = VariableRef("result")
    store.define(result, Operation(op, ()))
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    prepared, diagnostics = preprocessor.preprocess()
    assert not diagnostics.items
    assert prepared.static_types[result] == frozenset({ValueType.boolean})
    assert prepared.domains[result] == Domain(bools=frozenset({value}))


@pytest.mark.parametrize(
    ("left", "right", "quotient"),
    ((3.5, 2, 1), (-3.5, 2, -2), (7, -2.0, -4), (7, 2, 3)),
)
def test_preprocess_integer_division(left: float, right: float, quotient: int) -> None:
    """Keep division results integer-valued when used by integer-only operators."""
    store = ConstraintStore()
    divided, result = VariableRef("divided"), VariableRef("result")
    store.define(divided, Operation(Operator.int_div, (left, right)))
    store.define(result, Operation(Operator.linear_integer, ((2, divided), 1)))
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    prepared, diagnostics = preprocessor.preprocess()
    assert not diagnostics.items
    assert prepared.static_types[divided] == frozenset({ValueType.integer})
    assert prepared.static_types[result] == frozenset({ValueType.integer})
    assert prepared.domains[divided] == Domain(ints=frozenset({quotient}))
    assert prepared.domains[result] == Domain(ints=frozenset({2 * quotient + 1}))


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

    options = PreprocessOptions(arguments=("--opt",), threshold=100, boolean_threshold=10)
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
    assert prepared.static_types[s] == frozenset({SetOf(frozenset({ValueType.integer}), False)})

    assert prepared.domains[x] == Domain(ints=frozenset({1, 2, 3}))
    assert prepared.domains[y] == Domain(ints=frozenset({11, 12, 13}))
    assert prepared.domains[s] == Domain(implicit_set_elements=frozenset({1, 2, 3, 5, 6}))

    # Adding more to preprocessor after preprocess must not mutate prepared.store
    extra = ConstraintStore()
    extra.define(VariableRef("z"), 42)
    preprocessor.add(extra)
    assert VariableRef("z") not in prepared.store.variables


@pytest.mark.parametrize(
    ("values", "lengths", "implicit"),
    (
        (("", "abc"), frozenset({0, 3}), False),
        (((), (1, True)), frozenset({0, 2}), False),
        ((frozenset[int](), frozenset({1, 2})), frozenset({0, 2}), False),
        (("abc", (1, True), frozenset({1})), frozenset({1, 2, 3}), False),
        ((1, 2), frozenset({0, 1, 2}), True),
    ),
)
def test_preprocess_collection_length(values: tuple[Expr, ...], lengths: frozenset[int], implicit: bool) -> None:
    """Preserve length overload metadata through normalization and splitting."""
    store = ConstraintStore()
    source, length, result, offset = (VariableRef(name) for name in ("source", "length", "result", "offset"))
    if implicit:
        store.set_contain_choose_from_iterator(source, values)
    else:
        store.choose_from_iterator(source, values)
    store.choose_from_iterator(offset, range(20))
    store.define(length, Operation(Operator.length, (source,)))
    store.define(
        result,
        Operation(Operator.add, (Operation(Operator.length, (source,)), offset)),
    )
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    prepared, diagnostics = preprocessor.preprocess()
    assert not diagnostics.items
    assert prepared.domains[length] == Domain(ints=lengths)
    assert prepared.static_types[length] == frozenset({ValueType.integer})
    assert prepared.domains[result] == Domain(ints=frozenset(size + value for size in lengths for value in range(20)))
    assert set(prepared.store.expressions.values()) <= (prepared.domains.keys() & prepared.static_types.keys())


@pytest.mark.parametrize("value", (True, 1, 1.5, None))
def test_preprocess_length_rejects_scalars(value: Expr) -> None:
    """Keep non-collection length inputs invalid during preprocessing."""
    store = ConstraintStore()
    store.define(VariableRef("result"), Operation(Operator.length, (value,)))
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    _prepared, diagnostics = preprocessor.preprocess()
    assert diagnostics.has_errors
    assert any("length requires" in item.message for item in diagnostics.errors)


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
    assert len([error for error in diagnostics.errors if "dependency cycle" in error.message]) == 2


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
