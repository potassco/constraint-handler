"""Specification-driven tests of normalized domains and operator computation."""

# pyright: reportPrivateUsage=false

import math
from collections.abc import Callable
from itertools import product
from unittest.mock import patch

import pytest

from constraint_handler import (
    ConstraintStore,
    DomainCache,
    Lambda,
    Operation,
    Operator,
    VariableRef,
)
from constraint_handler.domains import EMPTY_DOMAIN, UNKNOWN_DOMAIN, Domain
from constraint_handler.domains._domain import (
    DomainValue,
    _Range,
    domain_from_values,
    join_domains,
    representation_key,
)
from constraint_handler.internal_input import convert_expression
from constraint_handler.python_input import Expr


def test_integer_range_normalization() -> None:
    """Normalize intervals while preserving genuine gaps and immutable identity."""
    supplied = [(10, 11), (2, 3), (7, 7), (1, 1), (2, 2)]
    actual = _Range(supplied)
    assert actual.intervals == ((1, 3), (7, 7), (10, 11))
    assert actual == _Range(reversed(supplied))
    assert hash(actual) == hash(_Range(reversed(supplied)))
    supplied.append((4, 6))
    assert actual.cardinality() == 6
    assert actual.bounds() == (1, 11)
    assert 7 in actual
    assert 4 not in actual
    assert True not in actual
    assert 1.0 not in actual


def test_integer_range_empty_singleton_and_large_operations() -> None:
    """Operate directly on huge intervals without integer enumeration."""
    empty = _Range()
    assert empty.bounds() is None
    assert empty.cardinality() == 0
    assert 0 not in empty
    singleton = _Range([(7, 7)])
    assert singleton.cardinality() == 1
    assert empty.union(singleton) == singleton
    assert empty.intersection(singleton) == empty
    limit = 10**30
    left = _Range([(-limit, -1), (3, limit)])
    right = _Range([(-2, 3), (limit + 2, limit + 2)])
    assert left.cardinality() == 2 * limit - 2
    assert left.intersection(right) == _Range([(-2, -1), (3, 3)])
    assert left.union(right) == _Range([(-limit, limit), (limit + 2, limit + 2)])


@pytest.mark.parametrize("interval", [(3, 2), (True, 2), (1, 2.0)])
def test_integer_range_rejects_invalid_endpoints(interval: tuple[int, int]) -> None:
    """Reject reversed bounds and noninteger endpoints, including Booleans."""
    with pytest.raises(ValueError if interval == (3, 2) else TypeError):
        _Range([interval])


@pytest.mark.parametrize(
    "value",
    [None, True, False, -7, 1.0, -0.0, "hello", (1, frozenset({2})), frozenset({1, 2})],
)
def test_literal_domains(value: DomainValue) -> None:
    """Abstract supported scalar, tuple, and set literals consistently."""
    cache = DomainCache(ConstraintStore())
    assert cache.get_domain(convert_expression(value)) == domain_from_values([value])


def test_domain_normalized_identity_and_join() -> None:
    """Identify equivalent intervals and set bases without widening scalar joins."""
    assert Domain(ints=[1, 2, 3]) == Domain(int_range=(1, 3))
    assert hash(Domain(ints=[1, 2, 3])) == hash(Domain(int_range=(1, 3)))
    joined = join_domains([Domain(int_range=(1, 3)), Domain(int_range=(7, 9))])
    assert joined.integers.intervals == ((1, 3), (7, 9))
    assert joined.int_count() == 6
    assert join_domains([Domain(reals=[1.0]), Domain(reals=[2.5])]) == Domain(
        reals=[1.0, 2.5]
    )
    assert domain_from_values(
        [frozenset({1, 2}), frozenset({2, 3})]
    ) == domain_from_values([frozenset({1, 2, 3})])
    assert Domain(set_base=EMPTY_DOMAIN).cardinality() == 1
    assert not Domain(set_base=EMPTY_DOMAIN).is_empty()
    assert Domain(set_base=UNKNOWN_DOMAIN).cardinality() is None
    assert Domain(bools=[True]) != Domain(ints=[1])
    assert Domain(reals=[-0.0]) != Domain(reals=[0.0])
    assert join_domains([UNKNOWN_DOMAIN, Domain(ints=[1])]) == UNKNOWN_DOMAIN


def test_integer_projection_operations_do_not_expand() -> None:
    """Clip intervals and obtain bounds and minimum nonzero magnitudes symbolically."""
    domain = Domain(integers=_Range([(-(10**30), -7), (0, 0), (3, 10**30)]))
    assert domain.integer_bounds() == (-(10**30), 10**30)
    assert domain.min_nonzero_abs_int() == 3
    assert Domain(int_range=(-4, 5)).min_nonzero_abs_int() == 1
    assert EMPTY_DOMAIN.min_nonzero_abs_int() is None


_OPERATOR_CASES: list[tuple[Operator, tuple[Expr, ...], DomainValue]] = [
    (Operator.abs, (-3,), 3),
    (Operator.minus, (3,), -3),
    (Operator.add, (2, 3), 5),
    (Operator.sub, (2, 3), -1),
    (Operator.mult, (2, 3), 6),
    (Operator.int_div, (-7, 2), -4),
    (Operator.mod, (-7, 2), 1),
    (Operator.real_div, (7, 2), 3.5),
    (Operator.pow, (2, -2), 0.25),
    (Operator.min, (3, 1, 2), 1),
    (Operator.max, (3, 1, 2), 3),
    (Operator.sqrt, (9,), 3.0),
    (Operator.sin, (0,), 0.0),
    (Operator.cos, (0,), 1.0),
    (Operator.tan, (0,), 0.0),
    (Operator.asin, (0,), 0.0),
    (Operator.acos, (1,), 0.0),
    (Operator.atan, (0,), 0.0),
    (Operator.floor, (3.5,), 3),
    (Operator.ceil, (-3.5,), -3),
    (Operator.int_from_real, (-3.5,), -3),
    (Operator.real_from_int, (3,), 3.0),
    (Operator.eq, (True, 1), False),
    (Operator.eq, (1, 1.0), True),
    (Operator.neq, (True, 1), True),
    (Operator.lt, (1, 2), True),
    (Operator.leq, (2, 2), True),
    (Operator.gt, (2, 1), True),
    (Operator.geq, (2, 2), True),
    (Operator.lnot, (True,), False),
    (Operator.snot, (None,), False),
    (Operator.wnot, (True,), True),
    (Operator.wnot, (False,), False),
    (Operator.wnot, (None,), True),
    (Operator.limp, (True, False), False),
    (Operator.conj, (), True),
    (Operator.disj, (), False),
    (Operator.lxor, (), False),
    (Operator.leqv, (), True),
    (Operator.lxor, (True, False, True), False),
    (Operator.leqv, (False, True, False), True),
    (Operator.concat, ("a", "b"), "ab"),
    (Operator.length, ("hello",), 5),
    (Operator.length, ((1, 2),), 2),
    (Operator.has_value, (None,), False),
    (Operator.get_or_else, (None, 7), 7),
    (Operator.if_, (False, 7), None),
    (Operator.ite, (False, 1, 2), 2),
    (Operator.tuple_get, ((1, "two"), 1), "two"),
    (Operator.make_tuple, (1, "two"), (1, "two")),
    (Operator.set_make, (1, 2), frozenset({1, 2})),
    (Operator.union, (), frozenset()),
    (Operator.linear_integer, (), 0),
    (Operator.linear_integer, ((2, 3), 1), 7),
    (Operator.linear_comparison, ("lt", (2, 3), -7), True),
]


@pytest.mark.parametrize(("op", "arguments", "expected"), _OPERATOR_CASES)
def test_operator_results(
    op: Operator, arguments: tuple[Expr, ...], expected: DomainValue
) -> None:
    """Follow operator semantics for admissible scalar and structural inputs."""
    expr = convert_expression(Operation(op, arguments))
    assert DomainCache(ConstraintStore()).get_domain(expr) == domain_from_values(
        [expected]
    )


@pytest.mark.parametrize(
    "op",
    [
        Operator.add,
        Operator.sub,
        Operator.mult,
        Operator.int_div,
        Operator.mod,
        Operator.pow,
    ],
)
def test_integer_operator_bounds_cover_finite_results(op: Operator) -> None:
    """Check symbolic bounds against all successful values of small integer products."""
    store = ConstraintStore()
    left, right = VariableRef("left"), VariableRef("right")
    store.choose_from_iterator(left, range(-3, 4))
    store.choose_from_iterator(right, range(-2, 3))
    expr = convert_expression(Operation(op, (left, right)))
    cache = DomainCache(store, threshold=1)
    result = cache.get_domain(expr)
    functions: dict[Operator, Callable[[int, int], int | float]] = {
        Operator.add: lambda first, second: first + second,
        Operator.sub: lambda first, second: first - second,
        Operator.mult: lambda first, second: first * second,
        Operator.int_div: lambda first, second: first // second,
        Operator.mod: lambda first, second: first % second,
        Operator.pow: lambda first, second: first**second,
    }
    if result.unknown:
        return
    for first, second in product(range(-3, 4), range(-2, 3)):
        try:
            value = functions[op](first, second)
        except ValueError, ZeroDivisionError:
            continue
        assert (
            result.contains_int(value) if type(value) is int else value in result.reals
        )


def test_large_symbolic_domains_and_structural_projection() -> None:
    """Avoid expanding huge integer axes or set-valued tuple positions."""
    store = ConstraintStore()
    source = VariableRef("source")
    cache = DomainCache(store)
    cache.set_domain(source, Domain(int_range=(1, 10**30)))
    absolute = convert_expression(Operation(Operator.abs, (source,)))
    addition = convert_expression(Operation(Operator.add, (source, 1)))
    compound = convert_expression(
        Operation(Operator.make_tuple, (source, frozenset({1, 2})))
    )
    projection = convert_expression(
        Operation(
            Operator.tuple_get,
            (Operation(Operator.make_tuple, (source, frozenset({1, 2}))), 1),
        )
    )
    with patch.object(Domain, "iter_ints", side_effect=AssertionError("expanded")):
        assert cache.get_domain(absolute) == Domain(int_range=(1, 10**30))
        assert cache.get_domain(addition) == Domain(int_range=(2, 10**30 + 1))
        assert cache.get_domain(compound).tuple_domains
        assert cache.get_domain(projection) == Domain(set_base=Domain(ints=[1, 2]))


def test_lambda_lexical_shadowing_and_unknown_parameters() -> None:
    """Explicit unknown parameters never fall back to same-named globals."""
    store = ConstraintStore()
    parameter, missing = VariableRef("parameter"), VariableRef("missing")
    store.define(parameter, 7)
    expr = convert_expression(
        Operation(Operator.lambda_, (Lambda((parameter,), parameter), missing))
    )
    assert DomainCache(store).get_domain(expr) == UNKNOWN_DOMAIN


def test_domain_unsupported_values_and_nonfinite_detection() -> None:
    """Retain finite type-sensitive identity and detect nonfinite compound payloads."""
    assert Domain(reals=[math.inf]).has_nonfinite_values()
    assert domain_from_values([(math.inf,)]).has_nonfinite_values()
    assert not Domain(int_range=(0, 10**100)).has_nonfinite_values()
    assert representation_key((True,)) != representation_key((1,))
    assert EMPTY_DOMAIN.is_empty()
    assert not UNKNOWN_DOMAIN.is_empty()
    assert not Domain(has_none=True).is_empty()
