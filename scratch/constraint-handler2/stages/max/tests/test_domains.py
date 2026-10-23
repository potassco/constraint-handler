"""Tests for domain representation and domain computation."""

import math
from collections.abc import Iterator
from itertools import product
from typing import Literal
from unittest.mock import patch

import pytest

from constraint_handler import (
    ConstraintStore,
    Diagnostics,
    Lambda,
    Operation,
    Operator,
    Python,
    VariableRef,
)
from constraint_handler.domains import (
    DEFAULT_BOOLEAN_THRESHOLD,
    DEFAULT_THRESHOLD,
    EMPTY_DOMAIN,
    TRUE_FALSE_DOMAIN,
    UNKNOWN_DOMAIN,
    Domain,
    DomainStore,
    arithmetic,
    comparisons,
    compute_domains,
    conversions,
    domain_from_values,
    logic,
    sets,
    union_domains,
)
from constraint_handler.domains.arithmetic import MAX_POWER_BITS, numeric_combinations
from constraint_handler.domains.operations import (
    DOMAIN_HANDLERS,
    DomainOperationEvaluator,
)
from constraint_handler.internal_input import ValueType
from constraint_handler.python_input import Expr
from constraint_handler.static_types import SetOf, compute_static_types
from constraint_handler.util import compute_evaluation_order


def _domains_for(
    store: ConstraintStore,
    *,
    threshold: int = DEFAULT_THRESHOLD,
    boolean_threshold: int = DEFAULT_BOOLEAN_THRESHOLD,
    diagnostics: Diagnostics | None = None,
) -> DomainStore:
    """Compute evaluation order and domains for a store."""
    diag = diagnostics if diagnostics is not None else Diagnostics()
    order = compute_evaluation_order(store, diag)
    return compute_domains(
        store,
        order,
        diag,
        threshold=threshold,
        boolean_threshold=boolean_threshold,
    )


@pytest.mark.parametrize("op", (Operator.lxor, Operator.leqv))
@pytest.mark.parametrize(
    "operands", ((), (True, True, True), (False,), (False, False), (True, False))
)
@pytest.mark.parametrize("boolean_threshold", (0, 1, DEFAULT_BOOLEAN_THRESHOLD))
def test_logic_parity_is_threshold_independent(
    op: Operator, operands: tuple[bool, ...], boolean_threshold: int
) -> None:
    """Compute fixed Boolean parity exactly without products or thresholds."""
    store = ConstraintStore()
    result = VariableRef("result")
    store.define(result, Operation(op, operands))

    with patch(
        "constraint_handler.domains.logic.product",
        create=True,
        side_effect=AssertionError("unexpected enumeration"),
    ):
        domains = _domains_for(store, boolean_threshold=boolean_threshold)
    assert domains[result] == Domain(
        bools=frozenset(
            {
                sum(operands) % 2 == 1
                if op == Operator.lxor
                else operands.count(False) % 2 == 0
            }
        )
    )


@pytest.mark.parametrize("op", (Operator.lxor, Operator.leqv))
def test_logic_large_product_is_not_enumerated(op: Operator) -> None:
    """Infer both parities directly from an operand with both Boolean values."""
    store = ConstraintStore()
    argument = VariableRef("argument")
    result = VariableRef("result")
    store.choose_from_iterator(argument, (True, False))
    store.define(result, Operation(op, (argument,) * 32))
    with patch(
        "constraint_handler.domains.logic.product",
        create=True,
        side_effect=AssertionError("unexpected enumeration"),
    ):
        assert _domains_for(store)[result] == TRUE_FALSE_DOMAIN


@pytest.mark.parametrize(
    ("left", "right", "equal"),
    (
        ("a", 42, False),
        (1, 1.0, True),
        (True, 1, False),
        (False, 0.0, False),
        ((True,), (1,), False),
        ((1,), (1.0,), True),
        (frozenset({True}), frozenset({1}), False),
        (((False,),), ((0,),), False),
    ),
)
def test_cross_type_equality(left: Expr, right: Expr, equal: bool) -> None:
    """Accept cross-type equality, preserving only numeric integer/real coercion."""
    store = ConstraintStore()
    eq_result = VariableRef("eq_result")
    neq_result = VariableRef("neq_result")
    store.define(eq_result, Operation(Operator.eq, (left, right)))
    store.define(neq_result, Operation(Operator.neq, (left, right)))
    diagnostics = Diagnostics()
    order = compute_evaluation_order(store, diagnostics)
    compute_static_types(store, order, diagnostics)
    assert not diagnostics.has_errors
    domains = _domains_for(store, diagnostics=diagnostics)
    assert domains[eq_result] == Domain(bools=frozenset({equal}))
    assert domains[neq_result] == Domain(bools=frozenset({not equal}))


@pytest.mark.parametrize("bound", (2**60 + 1, 10**400))
def test_integer_division_large_interval(bound: int) -> None:
    """Keep interval division bounds exact without floating-point conversion."""
    store = ConstraintStore()
    source = VariableRef("source")
    result = VariableRef("result")
    store.choose_from_iterator(source, (0, bound))
    store.define(result, Operation(Operator.int_div, (source, 1)))
    assert _domains_for(store, threshold=1)[result] == Domain(int_range=(-bound, bound))


@pytest.mark.parametrize("threshold", (1, DEFAULT_THRESHOLD))
def test_set_boolean_numeric_collisions(threshold: int) -> None:
    """Never infer a smaller set after Python collapses Boolean/numeric members."""
    store = ConstraintStore()
    source = VariableRef("source")
    result = VariableRef("result")
    store.choose_from_iterator(source, (True, 1))
    store.define(result, Operation(Operator.set_make, (source, 1)))
    diagnostics = Diagnostics()
    assert _domains_for(store, threshold=threshold, diagnostics=diagnostics)[
        result
    ].unknown
    assert any("cannot distinguish" in item.message for item in diagnostics.items)


@pytest.mark.parametrize(
    "op", (Operator.set_isin, Operator.subset, Operator.inter, Operator.diff)
)
def test_set_operations_distinguish_booleans(op: Operator) -> None:
    """Use language equality rather than Python equality for set operations."""
    store = ConstraintStore()
    result = VariableRef("result")
    left: Expr = True if op == Operator.set_isin else frozenset({True})
    store.define(result, Operation(op, (left, frozenset({1}))))
    expected = (
        Domain(bools=frozenset({False}))
        if op in (Operator.set_isin, Operator.subset)
        else Domain(
            explicit_sets=frozenset(
                {frozenset() if op == Operator.inter else frozenset({True})}
            )
        )
    )
    assert _domains_for(store)[result] == expected


def test_compound_domain_collisions() -> None:
    """Preserve soundness when alternative tuples collide in Python collections."""
    assert domain_from_values(((True,), (1,))).unknown
    assert union_domains(
        (domain_from_values(((True,),)), domain_from_values(((1,),)))
    ).unknown


@pytest.mark.parametrize(
    ("op", "value"),
    (
        (Operator.floor, math.inf),
        (Operator.ceil, -math.inf),
        (Operator.int_from_real, math.nan),
        (Operator.sqrt, 10**400),
        (Operator.cos, 10**400),
        (Operator.sin, 10**400),
        (Operator.tan, 10**400),
        (Operator.real_from_int, 10**400),
    ),
)
def test_numeric_failures_are_diagnosed(op: Operator, value: float) -> None:
    """Fall back soundly on unrepresentable or non-finite numerical evaluations."""
    store = ConstraintStore()
    result = VariableRef("result")
    store.define(result, Operation(op, (value,)))
    diagnostics = Diagnostics()
    assert _domains_for(store, diagnostics=diagnostics)[result].unknown
    assert diagnostics.warnings
    assert all(item.expr_id is not None for item in diagnostics.warnings)


@pytest.mark.parametrize(
    ("op", "arguments"),
    (
        (Operator.min, ("a", "b")),
        (Operator.max, ("a", "b")),
        (Operator.length, (1,)),
        (Operator.concat, (1, "a")),
        (Operator.concat, (None, "a")),
        (Operator.lxor, (1, True)),
        (Operator.leqv, ("a", False)),
    ),
)
def test_unsupported_domain_inputs_are_diagnosed(
    op: Operator, arguments: tuple[Expr, ...]
) -> None:
    """Reject string extrema and explain operators with no supported input values."""
    store = ConstraintStore()
    result = VariableRef("result")
    store.define(result, Operation(op, arguments))
    diagnostics = Diagnostics()
    assert _domains_for(store, diagnostics=diagnostics)[result].is_empty()
    assert diagnostics.has_errors
    assert all(item.expr_id is not None for item in diagnostics.errors)


def test_logical_not_none_is_empty() -> None:
    """Logical negation contributes values only for Boolean alternatives."""
    store = ConstraintStore()
    result = VariableRef("result")
    store.define(result, Operation(Operator.lnot, (None,)))
    assert _domains_for(store)[result] == EMPTY_DOMAIN


@pytest.mark.parametrize("set_variable", (False, True))
def test_collection_variable_collisions_are_diagnosed(set_variable: bool) -> None:
    """Locate unsupported variable-domain collection collisions at their variable."""
    store = ConstraintStore()
    source = VariableRef("source")
    if set_variable:
        store.set_contain_choose_from_iterator(source, (True, 1))
    else:
        store.choose_from_iterator(source, ((True,), (1,)))
    diagnostics = Diagnostics()
    assert _domains_for(store, diagnostics=diagnostics)[source].unknown
    assert any(item.variable == source for item in diagnostics.warnings)


def test_tuple_alternatives_collisions_are_diagnosed() -> None:
    """Do not discard tuple alternatives generated from scalar choices."""
    store = ConstraintStore()
    source = VariableRef("source")
    result = VariableRef("result")
    store.choose_from_iterator(source, (True, 1))
    store.define(result, (source,))
    diagnostics = Diagnostics()
    assert _domains_for(store, diagnostics=diagnostics)[result].unknown
    assert diagnostics.warnings


def test_implicit_and_explicit_sets_use_typed_equality() -> None:
    """Retain an explicit Boolean set outside a numeric implicit universe."""
    domain = Domain(
        implicit_set_elements=frozenset({1}),
        explicit_sets=frozenset({frozenset({True})}),
    )
    assert domain.cardinality() == 3
    assert len(list(domain.iter_values())) == 3
    assert union_domains((domain,)) == domain


def test_linear_set_term_reports_integer_error_only() -> None:
    """Validate structural linear pairs without treating them as value tuples."""
    store = ConstraintStore()
    result = VariableRef("result")
    store.define(result, Operation(Operator.linear_integer, ((1, frozenset({2})), 0)))
    diagnostics = Diagnostics()
    assert _domains_for(store, diagnostics=diagnostics)[result].unknown
    assert len(diagnostics.errors) == 1
    assert diagnostics.errors[0].message == "linear_integer terms must be integers"
    assert diagnostics.errors[0].expr_id is not None


def test_undefined_variable_is_diagnosed() -> None:
    """Distinguish undefined references from deliberately empty choice domains."""
    store = ConstraintStore()
    missing = VariableRef("missing")
    store.define(VariableRef("result"), missing)
    diagnostics = Diagnostics()
    _domains_for(store, diagnostics=diagnostics)
    assert any(item.variable == missing for item in diagnostics.errors)


@pytest.mark.parametrize("op", (Operator.min, Operator.max))
@pytest.mark.parametrize("threshold", (0, DEFAULT_THRESHOLD))
def test_string_extrema_are_empty_at_any_threshold(
    op: Operator, threshold: int
) -> None:
    """Unsupported string extrema stay empty even when enumeration is disabled."""
    store = ConstraintStore()
    result = VariableRef("result")
    store.define(result, Operation(op, ("a", "b")))
    diagnostics = Diagnostics()
    assert _domains_for(store, threshold=threshold, diagnostics=diagnostics)[
        result
    ].is_empty()
    assert diagnostics.has_errors


@pytest.mark.parametrize("threshold", (0, DEFAULT_THRESHOLD))
def test_union_collision_is_diagnosed_once(threshold: int) -> None:
    """Explain an unrepresentable typed union once in either evaluation mode."""
    store = ConstraintStore()
    result = VariableRef("result")
    store.define(result, Operation(Operator.union, (frozenset({True}), frozenset({1}))))
    diagnostics = Diagnostics()
    assert _domains_for(store, threshold=threshold, diagnostics=diagnostics)[
        result
    ].unknown
    assert len(diagnostics.warnings) == 1


def test_numeric_conversion_domains() -> None:
    """Retain both numeric kinds and bound conversion of large integer ranges."""
    store = ConstraintStore()
    source = VariableRef("source")
    store.choose_from_iterator(source, (-2, 3, -1.5, 2.5))
    store.define(VariableRef("to_int"), Operation(Operator.int_from_real, (source,)))
    store.define(VariableRef("to_real"), Operation(Operator.real_from_int, (source,)))
    domains = _domains_for(store)
    assert domains[VariableRef("to_int")] == Domain(ints=frozenset({-2, -1, 2, 3}))
    assert domains[VariableRef("to_real")] == Domain(
        reals=frozenset({-2.0, 3.0, -1.5, 2.5})
    )
    domains = _domains_for(store, threshold=2)
    assert domains[VariableRef("to_int")] == Domain(int_range=(-2, 3))
    assert domains[VariableRef("to_real")] == UNKNOWN_DOMAIN


@pytest.mark.parametrize("set_variable", (False, True))
def test_shared_definition_completion(set_variable: bool) -> None:
    """Finalize repeated definition IDs once before either pass visits dependents."""
    store = ConstraintStore()
    source = VariableRef("source")
    dependent = VariableRef("dependent")
    if set_variable:
        store.set_contain_choose(source, 7)
        bases = store.set_variables[source].bases
        bases.append(bases[0])
        store.define(dependent, Operation(Operator.cardinality, (source,)))
        expected_domain = Domain(implicit_set_elements=frozenset({7}))
        expected_type = frozenset({SetOf(frozenset({ValueType.integer}), True)})
    else:
        store.choose(source, 7)
        choices = store.variables[source].choices
        choices.append(choices[0])
        store.define(dependent, Operation(Operator.add, (source, 1)))
        expected_domain = Domain(ints=frozenset({7}))
        expected_type = frozenset({ValueType.integer})
    diagnostics = Diagnostics()
    order = compute_evaluation_order(store, diagnostics)
    definitions = order.defining_exprs[source]
    assert len(definitions) == 2
    assert len(set(definitions)) == 1
    steps = list(order.evaluation_steps())
    assert sum(source in variables for _, variables in steps) == 1
    assert list(order.evaluation_steps()) == steps
    domains = compute_domains(store, order, diagnostics)
    types = compute_static_types(store, order, diagnostics)
    assert domains[source] == expected_domain
    assert types[source] == expected_type
    assert domains[dependent] == Domain(ints=frozenset({0, 1} if set_variable else {8}))
    assert types[dependent] == frozenset({ValueType.integer})
    assert not diagnostics.has_errors


@pytest.mark.parametrize("argument", (Lambda((), 1), Python("lambda: 1")))
def test_set_make_rejects_callable_members(argument: Lambda | Python) -> None:
    """Report callable set members and keep their result unknown rather than partial."""
    store = ConstraintStore()
    result = VariableRef("result")
    store.define(result, Operation(Operator.set_make, (1, argument)))
    diagnostics = Diagnostics()
    assert _domains_for(store, diagnostics=diagnostics)[result] == UNKNOWN_DOMAIN
    assert len(diagnostics.errors) == 1


@pytest.mark.parametrize(
    ("source", "expected"),
    (
        ("lambda value: value * 2", Domain(ints=frozenset({2, 4}))),
        ("lambda value: (value, 'x')", Domain(tuples=frozenset({(1, "x"), (2, "x")}))),
        (
            "lambda value: frozenset({value})",
            Domain(explicit_sets=frozenset({frozenset({1}), frozenset({2})})),
        ),
        ("lambda value: None", Domain(has_none=True)),
        (
            "lambda value: math.sqrt(value)",
            Domain(reals=frozenset({1.0, math.sqrt(2)})),
        ),
    ),
)
def test_python_eval_domains(source: str, expected: Domain) -> None:
    """Evaluate supported Python results exactly up to the combination threshold."""
    store = ConstraintStore()
    argument = VariableRef("argument")
    result = VariableRef("result")
    store.choose_from_iterator(argument, (1, 2))
    store.define(result, Operation(Operator.python_eval, (Python(source), argument)))
    assert _domains_for(store, threshold=2)[result] == expected
    assert _domains_for(store, threshold=1)[result] == UNKNOWN_DOMAIN


@pytest.mark.parametrize(
    "source", ("lambda value: 1 / 0", "lambda value: [value]", "1", "invalid syntax!")
)
def test_python_eval_failures(source: str) -> None:
    """Keep failed, non-callable, and unsupported Python evaluations sound."""
    store = ConstraintStore()
    result = VariableRef("result")
    store.define(result, Operation(Operator.python_eval, (Python(source), 1)))
    diagnostics = Diagnostics()
    assert _domains_for(store, diagnostics=diagnostics)[result] == UNKNOWN_DOMAIN
    assert len(diagnostics.warnings) == 1
    diagnostics = Diagnostics()
    assert (
        _domains_for(store, threshold=0, diagnostics=diagnostics)[result]
        == UNKNOWN_DOMAIN
    )
    assert not diagnostics.warnings


def test_python_eval_empty_and_nullary() -> None:
    """Skip Python for empty arguments and evaluate a nullary callable once."""
    store = ConstraintStore()
    argument = VariableRef("argument")
    store.choose_from_iterator(argument, ())
    store.define(
        VariableRef("empty"),
        Operation(Operator.python_eval, (Python("lambda value: 1 / 0"), argument)),
    )
    store.define(
        VariableRef("nullary"), Operation(Operator.python_eval, (Python("lambda: 42"),))
    )
    diagnostics = Diagnostics()
    domains = _domains_for(store, diagnostics=diagnostics)
    assert domains[VariableRef("empty")] == EMPTY_DOMAIN
    assert domains[VariableRef("nullary")] == Domain(ints=frozenset({42}))
    assert not diagnostics.warnings
    assert _domains_for(store, threshold=0)[VariableRef("nullary")] == UNKNOWN_DOMAIN


@pytest.mark.parametrize("error_type", (MemoryError, RecursionError))
def test_python_eval_resource_failures(error_type: type[Exception]) -> None:
    """Do not hide interpreter resource failures as ordinary callback failures."""
    store = ConstraintStore()
    source = f"lambda: (_ for _ in ()).throw({error_type.__name__}())"
    store.define(
        VariableRef("result"), Operation(Operator.python_eval, (Python(source),))
    )
    with pytest.raises(error_type):
        _domains_for(store)


@pytest.mark.parametrize(
    ("operator", "members"),
    (
        (Operator.union, frozenset({1, 2, 3})),
        (Operator.inter, frozenset({2})),
        (Operator.diff, frozenset({1, 2})),
    ),
)
def test_set_operation_fallback_universes(
    operator: Operator, members: frozenset[int]
) -> None:
    """Approximate large set products using the tight potential-member universe."""
    store = ConstraintStore()
    left = VariableRef("left")
    right = VariableRef("right")
    result = VariableRef("result")
    store.choose_from_iterator(left, (frozenset({1, 2}), frozenset({2})))
    store.choose_from_iterator(right, (frozenset({2, 3}), frozenset({3})))
    store.define(result, Operation(operator, (left, right)))
    assert _domains_for(store, threshold=2)[result] == Domain(
        implicit_set_elements=members
    )


def test_set_fold_uses_specified_repr_order() -> None:
    """Keep order-sensitive folds deterministic without introducing numeric order."""
    store = ConstraintStore()
    accumulator = VariableRef("accumulator")
    element = VariableRef("element")
    callback = Lambda(
        (accumulator, element),
        Operation(
            Operator.add,
            (Operation(Operator.mult, (accumulator, 100)), element),
        ),
    )
    result = VariableRef("result")
    store.define(
        result, Operation(Operator.set_fold, (callback, frozenset({2, 10}), 0))
    )
    assert _domains_for(store)[result] == Domain(ints=frozenset({1002}))


def test_set_fold_domains_and_fallbacks() -> None:
    """Bound fold input products and preserve empty-set and empty-domain behavior."""
    store = ConstraintStore()
    accumulator = VariableRef("accumulator")
    element = VariableRef("element")
    callback = Lambda(
        (accumulator, element), Operation(Operator.add, (accumulator, element))
    )
    sets = VariableRef("sets")
    initial = VariableRef("initial")
    empty_domain = VariableRef("empty_domain")
    store.choose_from_iterator(sets, (frozenset({1, 2}), frozenset({3})))
    store.choose_from_iterator(initial, (10, 20))
    store.choose_from_iterator(empty_domain, ())
    store.define(
        VariableRef("folded"), Operation(Operator.set_fold, (callback, sets, initial))
    )
    store.define(
        VariableRef("empty_set"),
        Operation(Operator.set_fold, (callback, frozenset(), initial)),
    )
    store.define(
        VariableRef("empty_domain_result"),
        Operation(Operator.set_fold, (callback, empty_domain, initial)),
    )
    store.define(
        VariableRef("python_fold"),
        Operation(
            Operator.set_fold, (Python("lambda acc, elem: acc + elem"), sets, initial)
        ),
    )
    domains = _domains_for(store, threshold=4)
    assert domains[VariableRef("folded")] == Domain(ints=frozenset({13, 23}))
    assert domains[VariableRef("empty_set")] == domains[initial]
    assert domains[VariableRef("empty_domain_result")] == EMPTY_DOMAIN
    assert domains[VariableRef("python_fold")] == UNKNOWN_DOMAIN
    assert _domains_for(store, threshold=3)[VariableRef("folded")] == UNKNOWN_DOMAIN


def test_set_fold_without_set_members_is_diagnosed() -> None:
    """Report a non-set fold argument instead of silently returning no values."""
    store = ConstraintStore()
    accumulator = VariableRef("accumulator")
    element = VariableRef("element")
    callback = Lambda(
        (accumulator, element), Operation(Operator.add, (accumulator, element))
    )
    result = VariableRef("result")
    store.define(result, Operation(Operator.set_fold, (callback, 1, 0)))
    diagnostics = Diagnostics()
    assert _domains_for(store, diagnostics=diagnostics)[result] == UNKNOWN_DOMAIN
    assert len(diagnostics.errors) == 1
    assert diagnostics.errors[0].expr_id is not None


def test_domain_methods_and_unions() -> None:
    """Verify Domain helper methods, cardinality, iteration, and union_domains."""
    assert EMPTY_DOMAIN.is_empty()
    assert not UNKNOWN_DOMAIN.is_empty()
    assert UNKNOWN_DOMAIN.cardinality() is None
    assert EMPTY_DOMAIN.cardinality() == 0
    assert EMPTY_DOMAIN.min_int() is None
    assert EMPTY_DOMAIN.max_int() is None

    r_dom = Domain(ints=frozenset({-5, 2, 10}), int_range=(0, 5))
    assert r_dom.int_count() == 8
    assert set(r_dom.iter_ints()) == {-5, 0, 1, 2, 3, 4, 5, 10}
    assert r_dom.min_int() == -5
    assert r_dom.max_int() == 10

    s_dom = Domain(
        explicit_sets=frozenset({frozenset({1, 2}), frozenset({3})}),
        implicit_set_elements=frozenset({1, 2}),
    )
    assert s_dom.cardinality() == 5
    assert len(list(s_dom.iter_values())) == 5
    assert s_dom.potential_set_members() == frozenset({1, 2, 3})

    u1 = union_domains((Domain(ints=frozenset({1, 2, 3, 4})),), threshold=2)
    assert u1.int_range == (1, 4)
    assert not u1.ints

    u2 = union_domains(
        (Domain(int_range=(1, 3)), Domain(ints=frozenset({10}))), threshold=100
    )
    assert u2.int_range == (1, 10)

    u_real = union_domains((Domain(reals=frozenset({1.0, 2.0, 3.0})),), threshold=2)
    assert u_real.unknown

    u_set = union_domains(
        (
            Domain(implicit_set_elements=frozenset({1})),
            Domain(
                implicit_set_elements=frozenset({2}),
                explicit_sets=frozenset({frozenset({1, 2}), frozenset({3})}),
            ),
        )
    )
    assert u_set.implicit_set_elements == frozenset({1, 2})
    assert u_set.explicit_sets == frozenset({frozenset({3})})


def test_basic_expressions_and_variables() -> None:
    """Verify literals, variable choices/definitions/defaults, sets, and tuples."""
    store = ConstraintStore()
    x = VariableRef("x")
    y = VariableRef("y")
    s = VariableRef("s")
    empty_v = VariableRef("empty_v")
    empty_s = VariableRef("empty_s")

    store.choose_from_iterator(x, (1, 2))
    store.default_to(x, 3)
    store.define(y, (x, "a"))
    store.set_contain_choose_from_iterator(s, (10, 20))
    store.set_contain(s, 30)
    store.set_contain_default_to(s, 40)
    store.choose_from_iterator(empty_v, ())
    store.set_contain_choose_from_iterator(empty_s, ())
    store.ensure(frozenset({x, 5}))
    store.ensure(())

    doms = _domains_for(store)
    assert doms[x] == Domain(ints=frozenset({1, 2, 3}))
    assert doms[y] == Domain(tuples=frozenset({(1, "a"), (2, "a"), (3, "a")}))
    assert doms[s] == Domain(implicit_set_elements=frozenset({10, 20, 30, 40}))
    assert doms[empty_v] == EMPTY_DOMAIN
    assert doms[empty_s] == Domain(explicit_sets=frozenset({frozenset()}))
    assert doms[store.expressions[store.constraints[0].expr]] == Domain(
        explicit_sets=frozenset(
            {frozenset({1, 5}), frozenset({2, 5}), frozenset({3, 5})}
        )
    )
    assert doms[store.expressions[store.constraints[1].expr]] == Domain(
        tuples=frozenset({()})
    )


def test_operator_registry_covers_value_operators() -> None:
    """Register each value operator once while leaving scoped calls to the coordinator."""
    registries = (
        arithmetic.HANDLERS,
        comparisons.HANDLERS,
        conversions.HANDLERS,
        logic.HANDLERS,
        sets.HANDLERS,
    )
    scoped = {
        Operator.python_eval,
        Operator.lambda_,
        Operator.set_fold,
        Operator.linear_integer,
    }
    assert set(DOMAIN_HANDLERS) == set(Operator) - scoped
    assert sum(len(registry) for registry in registries) == len(DOMAIN_HANDLERS)


@pytest.mark.parametrize("kind", ("integers", "reals", "all"))
@pytest.mark.parametrize(
    "domains",
    (
        [],
        [EMPTY_DOMAIN],
        [Domain(int_range=(1, 2), reals=frozenset({0.5}))],
        [
            Domain(int_range=(1, 2), reals=frozenset({0.5})),
            Domain(ints=frozenset({3}), reals=frozenset({1.5})),
            Domain(ints=frozenset({4}), reals=frozenset({2.5})),
        ],
        [Domain(reals=frozenset({0.5})), Domain(ints=frozenset({1}))],
        [Domain(reals=frozenset({0.5})), EMPTY_DOMAIN],
    ),
)
def test_numeric_combinations(
    domains: list[Domain], kind: Literal["integers", "reals", "all"]
) -> None:
    """Partition small numeric products exactly, including empty and real-only axes."""
    expected = [
        values
        for values in product(
            *([*domain.iter_ints(), *domain.reals] for domain in domains)
        )
        if kind == "all"
        or (kind == "integers" and all(isinstance(value, int) for value in values))
        or (kind == "reals" and any(isinstance(value, float) for value in values))
    ]
    actual = list(numeric_combinations(domains, kind))
    assert len(actual) == len(expected)
    assert set(actual) == set(expected)


@pytest.mark.parametrize("op", (Operator.add, Operator.sub, Operator.mult))
@pytest.mark.parametrize("reverse", (False, True))
def test_arithmetic_skips_large_integer_only_products(
    op: Operator, reverse: bool
) -> None:
    """Keep exact real results without visiting a million integer-only tuples."""
    large = Domain(int_range=(0, 10**6), reals=frozenset({0.5}))
    small = Domain(ints=frozenset({1}))
    operands = [small, large] if reverse else [large, small]
    original_iter_ints = Domain.iter_ints

    def bounded_iter_ints(domain: Domain) -> Iterator[int]:
        """Reject enumeration of large integer intervals deterministically."""
        assert domain.int_count() <= 10
        return original_iter_ints(domain)

    with patch.object(Domain, "iter_ints", bounded_iter_ints):
        evaluator = DomainOperationEvaluator(Diagnostics(), 10, 10)
        result = evaluator.evaluate(op, operands, None)
    if op == Operator.add:
        expected = Domain(int_range=(1, 10**6 + 1), reals=frozenset({1.5}))
    elif op == Operator.mult:
        expected = Domain(int_range=(0, 10**6), reals=frozenset({0.5}))
    elif reverse:
        expected = Domain(int_range=(1 - 10**6, 1), reals=frozenset({0.5}))
    else:
        expected = Domain(int_range=(-1, 10**6 - 1), reals=frozenset({-0.5}))
    assert result == expected


@pytest.mark.parametrize(
    "expression",
    [
        Operation(Operator.linear_integer, ((0.5, VariableRef("x")), 0)),
        Operation(Operator.linear_integer, ((1, VariableRef("x")), 0.5)),
        Operation(Operator.linear_integer, ((1, VariableRef("real")), 0)),
        Operation(Operator.linear_integer, ((VariableRef("x"), VariableRef("x")), 0)),
        Operation(Operator.linear_integer, ((1, VariableRef("x")), VariableRef("x"))),
    ],
)
def test_linear_rejects_noninteger_and_nonconstant_inputs(
    expression: Operation,
) -> None:
    """Reject invalid linear inputs even when computing domains without static checks."""
    store = ConstraintStore()
    store.define(VariableRef("x"), 2)
    store.define(VariableRef("real"), 0.5)
    result = VariableRef("result")
    store.define(result, expression)
    diagnostics = Diagnostics()
    domains = _domains_for(store, diagnostics=diagnostics)
    assert domains[result].unknown
    assert diagnostics.has_errors


def test_arithmetic_and_thresholds() -> None:
    """Verify exact vs interval arithmetic and real threshold fallbacks."""
    store = ConstraintStore()
    a = VariableRef("a")
    b = VariableRef("b")
    f = VariableRef("f")
    store.choose_from_iterator(a, range(10))
    store.choose_from_iterator(b, range(10))
    store.choose_from_iterator(f, (0.5, 1.5))

    store.define(VariableRef("sum_ab"), Operation(Operator.add, (a, b)))
    store.define(VariableRef("sub_ab"), Operation(Operator.sub, (a, b)))
    store.define(VariableRef("mul_ab"), Operation(Operator.mult, (a, b)))
    store.define(
        VariableRef("lin_ab"),
        Operation(Operator.linear_integer, ((2, a), (-1, b), 3)),
    )
    store.define(
        VariableRef("lin_real"),
        Operation(Operator.linear_integer, ((1.5, a), 0.5)),
    )
    store.define(VariableRef("add_real"), Operation(Operator.add, (a, f)))
    store.define(VariableRef("sub_real"), Operation(Operator.sub, (a, f)))
    store.define(VariableRef("mul_real"), Operation(Operator.mult, (a, f)))

    # Exact under default threshold (10 * 10 = 100 <= 1000)
    doms_exact = _domains_for(store, threshold=200)
    assert doms_exact[VariableRef("sum_ab")] == Domain(ints=frozenset(range(19)))
    assert doms_exact[VariableRef("sub_ab")] == Domain(ints=frozenset(range(-9, 10)))
    assert doms_exact[VariableRef("lin_ab")] == Domain(
        ints=frozenset(2 * x - y + 3 for x in range(10) for y in range(10))
    )
    assert doms_exact[VariableRef("lin_real")].unknown

    # Interval fallback when N_int > threshold (100 > 50), while N_real (20) <= 50
    doms_range = _domains_for(store, threshold=50)
    assert doms_range[VariableRef("sum_ab")] == Domain(int_range=(0, 18))
    assert doms_range[VariableRef("sub_ab")] == Domain(int_range=(-9, 9))
    assert doms_range[VariableRef("mul_ab")] == Domain(int_range=(0, 81))
    assert doms_range[VariableRef("lin_ab")] == Domain(int_range=(-6, 21))
    assert doms_range[VariableRef("add_real")].int_range is None
    assert len(doms_range[VariableRef("add_real")].reals) == 11

    # Real combinations exceed threshold (20 > 5) -> unknown
    doms_unk = _domains_for(store, threshold=5)
    assert doms_unk[VariableRef("add_real")].unknown
    assert doms_unk[VariableRef("sub_real")].unknown
    assert doms_unk[VariableRef("mul_real")].unknown
    assert doms_unk[VariableRef("lin_real")].unknown


@pytest.mark.parametrize("threshold", (0, DEFAULT_THRESHOLD))
@pytest.mark.parametrize("base", (-2, 2))
@pytest.mark.parametrize("exponent", (MAX_POWER_BITS, 10**8))
def test_power_size_limit(base: int, exponent: int, threshold: int) -> None:
    """Bound integer power construction in both exact and interval branches."""
    evaluator = DomainOperationEvaluator(Diagnostics(), threshold, 10)
    assert (
        evaluator.evaluate(
            Operator.pow,
            [Domain(ints=frozenset({base})), Domain(ints=frozenset({exponent}))],
            None,
        )
        == UNKNOWN_DOMAIN
    )


@pytest.mark.parametrize("threshold", (0, DEFAULT_THRESHOLD))
def test_power_at_size_limit(threshold: int) -> None:
    """Retain powers whose estimated result still fits the integer bit budget."""
    evaluator = DomainOperationEvaluator(Diagnostics(), threshold, 10)
    bound = 1 << (MAX_POWER_BITS - 1)
    result = evaluator.evaluate(
        Operator.pow,
        [
            Domain(ints=frozenset({2})),
            Domain(ints=frozenset({MAX_POWER_BITS - 1})),
        ],
        None,
    )
    assert result == (
        Domain(int_range=(-bound, bound))
        if threshold == 0
        else Domain(ints=frozenset({bound}))
    )


@pytest.mark.parametrize("base", (-1, 0, 1))
def test_power_large_exponent_small_result(base: int) -> None:
    """Preserve constant-sized powers even when their exponents are large."""
    evaluator = DomainOperationEvaluator(Diagnostics(), DEFAULT_THRESHOLD, 10)
    assert evaluator.evaluate(
        Operator.pow,
        [Domain(ints=frozenset({base})), Domain(ints=frozenset({10**8}))],
        None,
    ) == Domain(ints=frozenset({0 if base == 0 else 1}))


def test_divisions_mod_and_pow() -> None:
    """Verify int_div, mod, real_div, pow, and division/power warnings."""
    store = ConstraintStore()
    x = VariableRef("x")
    y = VariableRef("y")
    z0 = VariableRef("z0")
    z1 = VariableRef("z1")
    f = VariableRef("f")
    store.choose_from_iterator(x, (-4, 0, 4))
    store.choose_from_iterator(y, (-2, 0, 2))
    store.define(z0, 0)
    store.define(z1, 1)
    store.define(f, 0.5)

    store.define(VariableRef("idiv"), Operation(Operator.int_div, (x, y)))
    store.define(VariableRef("imod"), Operation(Operator.mod, (x, y)))
    store.define(VariableRef("fdiv"), Operation(Operator.real_div, (x, y)))
    store.define(VariableRef("pow0"), Operation(Operator.pow, (x, z0)))
    store.define(VariableRef("pow1"), Operation(Operator.pow, (x, z1)))
    store.define(VariableRef("pow_xy"), Operation(Operator.pow, (x, y)))
    store.define(VariableRef("pow_xf"), Operation(Operator.pow, (x, f)))
    store.define(VariableRef("idiv_f"), Operation(Operator.int_div, (x, f)))

    diag = Diagnostics()
    doms = _domains_for(store, threshold=100, diagnostics=diag)
    assert len(diag.warnings) >= 4
    assert doms[VariableRef("idiv")] == Domain(ints=frozenset({-2, 0, 2}))
    assert doms[VariableRef("imod")] == Domain(ints=frozenset({0}))
    assert doms[VariableRef("fdiv")] == Domain(reals=frozenset({-2.0, 0.0, 2.0}))
    assert doms[VariableRef("pow0")] == Domain(ints=frozenset({1}))
    assert doms[VariableRef("pow1")] == doms[x]
    assert 16 in doms[VariableRef("pow_xy")].ints
    assert 0.0625 in doms[VariableRef("pow_xy")].reals
    assert doms[VariableRef("pow_xf")] == Domain(reals=frozenset({0.0, 2.0}))
    assert doms[VariableRef("idiv_f")] == Domain(reals=frozenset({-8.0, 0.0, 8.0}))

    # Range fallback for int_div, mod, and pow when threshold is small
    diag2 = Diagnostics()
    doms_small = _domains_for(store, threshold=3, diagnostics=diag2)
    assert doms_small[VariableRef("idiv")] == Domain(int_range=(-2, 2))
    assert doms_small[VariableRef("imod")] == Domain(int_range=(-1, 1))
    assert doms_small[VariableRef("fdiv")].unknown

    # Pow range fallback with non-negative integer exponents and real base/exp
    store2 = ConstraintStore()
    bx = VariableRef("bx")
    by = VariableRef("by")
    store2.choose_from_iterator(bx, (-3, 2))
    store2.choose_from_iterator(by, (0, 1, 2))
    store2.define(VariableRef("p_range"), Operation(Operator.pow, (bx, by)))
    doms2 = _domains_for(store2, threshold=2)
    assert doms2[VariableRef("p_range")] == Domain(int_range=(-9, 9))


def test_unary_math_and_trig() -> None:
    """Verify abs, minus, floor, ceil, trig functions, and domain warnings."""
    store = ConstraintStore()
    x = VariableRef("x")
    f = VariableRef("f")
    store.choose_from_iterator(x, (-2, 0, 1))
    store.choose_from_iterator(f, (-1.5, 0.5, math.pi / 2))

    store.define(VariableRef("abs_x"), Operation(Operator.abs, (x,)))
    store.define(VariableRef("neg_x"), Operation(Operator.minus, (x,)))
    store.define(VariableRef("flr_f"), Operation(Operator.floor, (f,)))
    store.define(VariableRef("cil_f"), Operation(Operator.ceil, (f,)))
    store.define(VariableRef("i2f"), Operation(Operator.real_from_int, (x,)))
    store.define(VariableRef("f2i"), Operation(Operator.int_from_real, (f,)))
    store.define(VariableRef("sq"), Operation(Operator.sqrt, (x,)))
    store.define(VariableRef("cs"), Operation(Operator.cos, (0,)))
    store.define(VariableRef("sn"), Operation(Operator.sin, (0,)))
    store.define(VariableRef("tn"), Operation(Operator.tan, (f,)))
    store.define(VariableRef("ac"), Operation(Operator.acos, (x,)))
    store.define(VariableRef("as_"), Operation(Operator.asin, (x,)))
    store.define(VariableRef("at"), Operation(Operator.atan, (0,)))

    diag = Diagnostics()
    doms = _domains_for(store, diagnostics=diag)
    assert len(diag.warnings) >= 4
    assert doms[VariableRef("abs_x")] == Domain(ints=frozenset({0, 1, 2}))
    assert doms[VariableRef("neg_x")] == Domain(ints=frozenset({-1, 0, 2}))
    assert doms[VariableRef("flr_f")] == Domain(ints=frozenset({-2, 0, 1}))
    assert doms[VariableRef("cil_f")] == Domain(ints=frozenset({-1, 1, 2}))
    assert doms[VariableRef("i2f")] == Domain(reals=frozenset({-2.0, 0.0, 1.0}))
    assert doms[VariableRef("f2i")] == Domain(ints=frozenset({-1, 0, 1}))
    assert doms[VariableRef("sq")] == Domain(reals=frozenset({0.0, 1.0}))
    assert doms[VariableRef("cs")] == Domain(reals=frozenset({1.0}))
    assert doms[VariableRef("sn")] == Domain(reals=frozenset({0.0}))
    assert doms[VariableRef("at")] == Domain(reals=frozenset({0.0}))
    assert len(doms[VariableRef("tn")].reals) == 2
    assert len(doms[VariableRef("ac")].reals) == 2
    assert len(doms[VariableRef("as_")].reals) == 2


def test_if_with_empty_condition_is_empty() -> None:
    """An if_ whose condition has no values has no values, even when x is empty."""
    store = ConstraintStore()
    cond = VariableRef("cond")
    store.choose_from_iterator(cond, ())
    store.define(VariableRef("result"), Operation(Operator.if_, (cond, 1)))
    store.define(
        VariableRef("result_empty_x"),
        Operation(Operator.if_, (cond, VariableRef("empty_x"))),
    )
    store.choose_from_iterator(VariableRef("empty_x"), ())

    doms = _domains_for(store)
    assert doms[VariableRef("result")] == EMPTY_DOMAIN
    assert doms[VariableRef("result_empty_x")] == EMPTY_DOMAIN


def test_comparisons_equalities_and_conditionals() -> None:
    """Verify eq, neq, ordered comparisons, if_, ite, get_or_else, has_value."""
    store = ConstraintStore()
    a = VariableRef("a")
    b = VariableRef("b")
    c = VariableRef("c")
    opt = VariableRef("opt")
    store.choose_from_iterator(a, (1, 2))
    store.choose_from_iterator(b, (3, 4))
    store.choose_from_iterator(c, (2, 3))
    store.choose_from_iterator(opt, (1, None))

    store.define(VariableRef("lt_true"), Operation(Operator.lt, (a, b)))
    store.define(VariableRef("lt_false"), Operation(Operator.lt, (b, a)))
    store.define(VariableRef("leq_true"), Operation(Operator.leq, (a, c)))
    store.define(VariableRef("leq_false"), Operation(Operator.leq, (b, a)))
    store.define(VariableRef("geq_true"), Operation(Operator.geq, (c, a)))
    store.define(VariableRef("geq_false"), Operation(Operator.geq, (a, b)))
    store.define(VariableRef("gt_true"), Operation(Operator.gt, (b, a)))
    store.define(VariableRef("gt_false"), Operation(Operator.gt, (a, b)))
    store.define(VariableRef("lt_mix"), Operation(Operator.lt, (a, c)))
    store.define(VariableRef("eq_ab"), Operation(Operator.eq, (a, b)))
    store.define(VariableRef("neq_ab"), Operation(Operator.neq, (a, b)))
    store.define(VariableRef("goe_none"), Operation(Operator.get_or_else, (opt, 99)))
    store.define(VariableRef("goe_nonnull"), Operation(Operator.get_or_else, (a, 99)))
    store.define(VariableRef("hv_opt"), Operation(Operator.has_value, (opt,)))
    store.define(VariableRef("hv_a"), Operation(Operator.has_value, (a,)))
    store.define(VariableRef("if_true"), Operation(Operator.if_, (True, a)))
    store.define(VariableRef("if_false"), Operation(Operator.if_, (False, a)))
    store.define(VariableRef("ite_t"), Operation(Operator.ite, (True, a, b)))
    store.define(VariableRef("ite_f"), Operation(Operator.ite, (False, a, b)))
    store.define(
        VariableRef("ite_both"),
        Operation(Operator.ite, (Operation(Operator.lt, (a, c)), a, b)),
    )
    store.define(VariableRef("min_ab"), Operation(Operator.min, (a, b)))
    store.define(VariableRef("max_ab"), Operation(Operator.max, (a, b)))
    store.define(VariableRef("cat"), Operation(Operator.concat, ("x", "y")))
    store.define(VariableRef("len_s"), Operation(Operator.length, ("hello",)))

    doms = _domains_for(store)
    assert doms[VariableRef("lt_true")] == Domain(bools=frozenset({True}))
    assert doms[VariableRef("lt_false")] == Domain(bools=frozenset({False}))
    assert doms[VariableRef("leq_true")] == Domain(bools=frozenset({True}))
    assert doms[VariableRef("leq_false")] == Domain(bools=frozenset({False}))
    assert doms[VariableRef("geq_true")] == Domain(bools=frozenset({True}))
    assert doms[VariableRef("geq_false")] == Domain(bools=frozenset({False}))
    assert doms[VariableRef("gt_true")] == Domain(bools=frozenset({True}))
    assert doms[VariableRef("gt_false")] == Domain(bools=frozenset({False}))
    assert doms[VariableRef("lt_mix")] == TRUE_FALSE_DOMAIN
    assert doms[VariableRef("eq_ab")] == Domain(bools=frozenset({False}))
    assert doms[VariableRef("neq_ab")] == Domain(bools=frozenset({True}))
    assert doms[VariableRef("goe_none")] == Domain(ints=frozenset({1, 99}))
    assert doms[VariableRef("goe_nonnull")] == Domain(ints=frozenset({1, 2}))
    assert doms[VariableRef("hv_opt")] == TRUE_FALSE_DOMAIN
    assert doms[VariableRef("hv_a")] == Domain(bools=frozenset({True}))
    assert doms[VariableRef("if_true")] == Domain(ints=frozenset({1, 2}))
    assert doms[VariableRef("if_false")] == Domain(
        ints=frozenset({1, 2}), has_none=True
    )
    assert doms[VariableRef("ite_t")] == Domain(ints=frozenset({1, 2}))
    assert doms[VariableRef("ite_f")] == Domain(ints=frozenset({3, 4}))
    assert doms[VariableRef("ite_both")] == Domain(ints=frozenset({1, 2, 3, 4}))
    assert doms[VariableRef("min_ab")] == Domain(ints=frozenset({1, 2}))
    assert doms[VariableRef("max_ab")] == Domain(ints=frozenset({3, 4}))
    assert doms[VariableRef("cat")] == Domain(strings=frozenset({"xy"}))
    assert doms[VariableRef("len_s")] == Domain(ints=frozenset({5}))


def test_logic_sets_lambdas_and_folds() -> None:
    """Verify boolean logic, set operations, lambda evaluation, and set_fold."""
    store = ConstraintStore()
    b1 = VariableRef("b1")
    b2 = VariableRef("b2")
    bn = VariableRef("bn")
    store.choose_from_iterator(b1, (True, False))
    store.define(b2, False)
    store.choose_from_iterator(bn, (True, None))

    store.define(VariableRef("c_false"), Operation(Operator.conj, (b1, b2)))
    store.define(VariableRef("d_both"), Operation(Operator.disj, (b1, b2)))
    store.define(VariableRef("lnot_bn"), Operation(Operator.lnot, (bn,)))
    store.define(VariableRef("snot_bn"), Operation(Operator.snot, (bn,)))
    store.define(VariableRef("wnot_bn"), Operation(Operator.wnot, (bn,)))
    store.define(VariableRef("limp_b"), Operation(Operator.limp, (b2, b1)))
    store.define(VariableRef("lxor_b"), Operation(Operator.lxor, (b1, b2)))
    store.define(VariableRef("leqv_b"), Operation(Operator.leqv, (b1, b2)))

    s1 = VariableRef("s1")
    s2 = VariableRef("s2")
    store.define(s1, Operation(Operator.set_make, (1, 2)))
    store.define(s2, Operation(Operator.set_make, (2, 3)))
    store.define(VariableRef("u_s"), Operation(Operator.union, (s1, s2)))
    store.define(VariableRef("i_s"), Operation(Operator.inter, (s1, s2)))
    store.define(VariableRef("d_s"), Operation(Operator.diff, (s1, s2)))
    store.define(VariableRef("sub_s"), Operation(Operator.subset, (s1, s2)))
    store.define(VariableRef("in_s"), Operation(Operator.set_isin, (1, s1)))
    store.define(VariableRef("nin_s"), Operation(Operator.set_notin, (1, s1)))
    store.define(VariableRef("card_s"), Operation(Operator.cardinality, (s1,)))
    store.define(VariableRef("len_set"), Operation(Operator.length, (s1,)))

    p = VariableRef("p")
    lam = Lambda((p,), Operation(Operator.mult, (p, 2)))
    x = VariableRef("x")
    store.choose_from_iterator(x, (3, 4))
    store.define(VariableRef("lam_x"), Operation(Operator.lambda_, (lam, x)))

    acc = VariableRef("acc")
    el = VariableRef("el")
    fold_lam = Lambda((acc, el), Operation(Operator.add, (acc, el)))
    store.define(
        VariableRef("folded"),
        Operation(Operator.set_fold, (fold_lam, s1, 10)),
    )
    store.define(
        VariableRef("tget"),
        Operation(Operator.tuple_get, ((10, 20), 1)),
    )

    doms = _domains_for(store)
    assert doms[VariableRef("c_false")] == Domain(bools=frozenset({False}))
    assert doms[VariableRef("d_both")] == TRUE_FALSE_DOMAIN
    assert doms[VariableRef("lnot_bn")] == Domain(bools=frozenset({False}))
    assert doms[VariableRef("snot_bn")] == Domain(bools=frozenset({False}))
    assert doms[VariableRef("wnot_bn")] == TRUE_FALSE_DOMAIN
    assert doms[VariableRef("limp_b")] == Domain(bools=frozenset({True}))
    assert doms[VariableRef("lxor_b")] == TRUE_FALSE_DOMAIN
    assert doms[VariableRef("leqv_b")] == TRUE_FALSE_DOMAIN

    assert doms[VariableRef("u_s")] == Domain(
        explicit_sets=frozenset({frozenset({1, 2, 3})})
    )
    assert doms[VariableRef("i_s")] == Domain(explicit_sets=frozenset({frozenset({2})}))
    assert doms[VariableRef("d_s")] == Domain(explicit_sets=frozenset({frozenset({1})}))
    assert doms[VariableRef("sub_s")] == Domain(bools=frozenset({False}))
    assert doms[VariableRef("in_s")] == Domain(bools=frozenset({True}))
    assert doms[VariableRef("nin_s")] == Domain(bools=frozenset({False}))
    assert doms[VariableRef("card_s")] == Domain(ints=frozenset({2}))
    assert doms[VariableRef("len_set")] == Domain(ints=frozenset({2}))
    assert doms[VariableRef("lam_x")] == Domain(ints=frozenset({6, 8}))
    assert doms[VariableRef("folded")] == Domain(ints=frozenset({13}))
    assert doms[VariableRef("tget")] == Domain(ints=frozenset({20}))


def test_cycles_unknowns_and_error_diagnostics() -> None:
    """Verify cycle handling, unknown propagation, and invalid operator arities."""
    store = ConstraintStore()
    c1 = VariableRef("c1")
    c2 = VariableRef("c2")
    store.define(c1, c2)
    store.define(c2, c1)

    unk = VariableRef("unk")
    store.define(unk, Operation(Operator.python_eval, (Python("1"),)))

    # Propagate unknown across operations
    store.define(VariableRef("u_eq"), Operation(Operator.eq, (unk, 1)))
    store.define(VariableRef("u_lt"), Operation(Operator.lt, (unk, 1)))
    store.define(VariableRef("u_conj"), Operation(Operator.conj, (unk, False)))
    store.define(VariableRef("u_disj"), Operation(Operator.disj, (unk, True)))
    store.define(VariableRef("u_hv"), Operation(Operator.has_value, (unk,)))
    store.define(VariableRef("u_goe"), Operation(Operator.get_or_else, (unk, 1)))
    store.define(VariableRef("u_if"), Operation(Operator.if_, (unk, 1)))
    store.define(VariableRef("u_ite"), Operation(Operator.ite, (unk, 1, 2)))
    store.define(VariableRef("u_cat"), Operation(Operator.concat, (unk, "a")))
    store.define(VariableRef("u_len"), Operation(Operator.length, (unk,)))
    store.define(VariableRef("u_min"), Operation(Operator.min, (unk, 1)))
    store.define(VariableRef("u_abs"), Operation(Operator.abs, (unk,)))
    store.define(VariableRef("u_add"), Operation(Operator.add, (unk, 1)))
    store.define(VariableRef("u_sub"), Operation(Operator.sub, (unk, 1)))
    store.define(VariableRef("u_mul"), Operation(Operator.mult, (unk, 1)))
    store.define(VariableRef("u_idiv"), Operation(Operator.int_div, (unk, 1)))
    store.define(VariableRef("u_fdiv"), Operation(Operator.real_div, (unk, 1)))
    store.define(VariableRef("u_pow"), Operation(Operator.pow, (unk, 2)))
    store.define(VariableRef("u_lnot"), Operation(Operator.lnot, (unk,)))
    store.define(VariableRef("u_isin"), Operation(Operator.set_isin, (1, unk)))
    store.define(VariableRef("u_union"), Operation(Operator.union, (unk, unk)))
    store.define(VariableRef("u_tget"), Operation(Operator.tuple_get, (unk, 0)))
    store.define(
        VariableRef("u_lin"), Operation(Operator.linear_integer, ((2, unk), 1))
    )

    diag = Diagnostics()
    doms = _domains_for(store, diagnostics=diag)
    assert diag.has_errors
    assert doms[c1].unknown
    assert doms[c2].unknown
    assert doms[VariableRef("u_eq")] == TRUE_FALSE_DOMAIN
    assert doms[VariableRef("u_lt")] == TRUE_FALSE_DOMAIN
    assert doms[VariableRef("u_conj")] == TRUE_FALSE_DOMAIN
    assert doms[VariableRef("u_disj")] == TRUE_FALSE_DOMAIN
    assert doms[VariableRef("u_hv")] == TRUE_FALSE_DOMAIN
    assert doms[VariableRef("u_isin")] == TRUE_FALSE_DOMAIN
    assert doms[VariableRef("u_lnot")] == TRUE_FALSE_DOMAIN
    assert doms[VariableRef("u_goe")].unknown
    assert doms[VariableRef("u_union")].unknown
    assert doms[VariableRef("u_lin")].unknown


@pytest.mark.parametrize(
    "values",
    [
        (True, 1, 2.5, None, "s", (1, 2), frozenset({1})),
    ],
)
def test_domain_from_values_all_kinds(values: tuple[object, ...]) -> None:
    """Verify domain_from_values partitions every supported runtime value kind."""
    d = domain_from_values(values)  # type: ignore[arg-type]
    assert d.bools == frozenset({True})
    assert d.ints == frozenset({1})
    assert d.reals == frozenset({2.5})
    assert d.has_none
    assert d.strings == frozenset({"s"})
    assert d.tuples == frozenset({(1, 2)})
    assert d.explicit_sets == frozenset({frozenset({1})})
