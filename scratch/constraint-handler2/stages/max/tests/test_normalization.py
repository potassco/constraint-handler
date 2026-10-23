"""Tests for expression-store normalization."""

import pytest

from constraint_handler import ConstraintStore, Lambda, Operation, Operator, VariableRef
from constraint_handler.diagnostics import Diagnostics
from constraint_handler.internal_input import Lambda as InternalLambda
from constraint_handler.internal_input import Operation as InternalOperation
from constraint_handler.internal_input import ValueDef, ValueType
from constraint_handler.normalization import normalize
from constraint_handler.static_types import StaticTypeStore, compute_static_types
from constraint_handler.util import compute_evaluation_order


def test_normalize_linear_expression_preserves_store_ids() -> None:
    """Combine coefficients and offsets without changing declaration metadata."""
    store = ConstraintStore()
    x = VariableRef("x")
    y = VariableRef("y")
    store.define(
        y,
        Operation(Operator.sub, (Operation(Operator.add, (x, x, 3)), x)),
        label="definition",
    )
    definition = store.variables[y].definitions[0]
    normalize(store, StaticTypeStore(expressions={x: frozenset({ValueType.integer})}))
    assert store.variables[y].definitions[0] == definition
    assert store.expressions[definition.value] == InternalOperation(
        Operator.linear_integer,
        ((ValueDef(ValueType.integer, 1), x), ValueDef(ValueType.integer, 3)),
    )


@pytest.mark.parametrize(
    "relation",
    [Operator.eq, Operator.neq, Operator.lt, Operator.leq, Operator.gt, Operator.geq],
)
def test_normalize_relations_and_repeatability(relation: Operator) -> None:
    """Move numeric relations to zero without reversing ordered comparisons."""
    store = ConstraintStore()
    x = VariableRef("x")
    store.choose_from_iterator(x, (1, 2))
    store.ensure(Operation(relation, (Operation(Operator.mult, (2, x)), 3)), "check")
    diagnostics = Diagnostics()
    order = compute_evaluation_order(store, diagnostics)
    types = compute_static_types(store, order, diagnostics)
    normalize(store, types)
    expr_id = store.constraints[0].expr
    assert store.expressions[expr_id] == InternalOperation(
        relation,
        (
            InternalOperation(
                Operator.linear_integer,
                (
                    (ValueDef(ValueType.integer, 2), x),
                    ValueDef(ValueType.integer, -3),
                ),
            ),
            ValueDef(ValueType.integer, 0),
        ),
    )
    first = dict(store.expressions)
    normalize(store, types)
    assert store.expressions == first
    assert store.constraints[0].label == "check"
    assert not diagnostics.has_errors


@pytest.mark.parametrize("value", ["text", True, None])
def test_nonnumeric_equality_is_unchanged(value: str | bool | None) -> None:
    """Keep equality for nonnumeric values out of arithmetic normalization."""
    store = ConstraintStore()
    store.ensure(Operation(Operator.eq, (value, value)))
    before = dict(store.expressions)
    normalize(store, StaticTypeStore())
    assert store.expressions == before


def test_products_and_lambda_shadowing_are_not_distributed() -> None:
    """Retain nonlinear products and avoid borrowing outer lambda parameter types."""
    store = ConstraintStore()
    x = VariableRef("x")
    y = VariableRef("y")
    product = Operation(Operator.mult, (x, Operation(Operator.add, (y, 1))))
    store.ensure(
        (
            product,
            Operation(
                Operator.lambda_,
                (
                    Lambda((x,), Operation(Operator.eq, (x, "text"))),
                    "text",
                ),
            ),
        )
    )
    types = StaticTypeStore(
        expressions={
            x: frozenset({ValueType.integer}),
            y: frozenset({ValueType.integer}),
        }
    )
    normalize(store, types)
    result = store.expressions[store.constraints[0].expr]
    assert isinstance(result, tuple)
    assert isinstance(result[0], InternalOperation)
    assert result[0].op == Operator.mult
    assert isinstance(result[0].args[1], InternalOperation)
    assert result[0].args[1].op == Operator.linear_integer
    call = result[1]
    assert isinstance(call, InternalOperation)
    callback = call.args[0]
    assert isinstance(callback, InternalLambda)
    assert callback.expr == InternalOperation(
        Operator.eq,
        (x, ValueDef(ValueType.string, "text")),
    )


def test_real_coefficients_are_not_normalized() -> None:
    """Leave noninteger linear coefficients and offsets for type diagnostics."""
    store = ConstraintStore()
    x = VariableRef("x")
    store.ensure(
        Operation(
            Operator.add,
            (
                Operation(Operator.linear_integer, ((0.5, x), 1.5)),
                x,
                2,
            ),
        )
    )
    before = dict(store.expressions)
    normalize(store, StaticTypeStore(expressions={x: frozenset({ValueType.integer})}))
    assert store.expressions == before


@pytest.mark.parametrize("relation", [False, True])
@pytest.mark.parametrize("choices", [(1e-17,), (1,), (1, 1e-17)])
def test_real_arithmetic_is_not_normalized(relation: bool, choices: tuple[int | float, ...]) -> None:
    """Preserve real addition in arithmetic and relations without reassociation."""
    store = ConstraintStore()
    x = VariableRef("x")
    store.choose_from_iterator(x, choices)
    store.ensure(
        Operation(
            Operator.eq if relation else Operator.sub,
            (Operation(Operator.add, (x, 1.0)), 1.0),
        )
    )
    diagnostics = Diagnostics()
    order = compute_evaluation_order(store, diagnostics)
    types = compute_static_types(store, order, diagnostics)
    before = dict(store.expressions)
    normalize(store, types)
    assert store.expressions == before
    assert not diagnostics.has_errors


def test_zero_product_prunes_its_term() -> None:
    """Normalize a zero integer coefficient to a constant-only linear form."""
    store = ConstraintStore()
    x = VariableRef("x")
    store.ensure(Operation(Operator.mult, (0, x)))
    normalize(store, StaticTypeStore(expressions={x: frozenset({ValueType.integer})}))
    assert store.expressions[store.constraints[0].expr] == InternalOperation(
        Operator.linear_integer, (ValueDef(ValueType.integer, 0),)
    )


def test_lambda_relation_uses_free_integer_variable() -> None:
    """Normalize free integer variables without treating parameters as integers."""
    store = ConstraintStore()
    x = VariableRef("x")
    parameter = VariableRef("parameter")
    store.ensure(
        Operation(
            Operator.lambda_,
            (Lambda((parameter,), Operation(Operator.eq, (x, 1))), "text"),
        )
    )
    normalize(store, StaticTypeStore(expressions={x: frozenset({ValueType.integer})}))
    result = store.expressions[store.constraints[0].expr]
    assert isinstance(result, InternalOperation)
    callback = result.args[0]
    assert isinstance(callback, InternalLambda)
    assert callback.expr == InternalOperation(
        Operator.eq,
        (
            InternalOperation(
                Operator.linear_integer,
                ((ValueDef(ValueType.integer, 1), x), ValueDef(ValueType.integer, -1)),
            ),
            ValueDef(ValueType.integer, 0),
        ),
    )


def test_nonconstant_linear_coefficient_is_not_rewritten() -> None:
    """Leave invalid linear coefficients available for type-checking diagnostics."""
    store = ConstraintStore()
    x = VariableRef("x")
    store.ensure(Operation(Operator.linear_integer, ((x, x), 0)))
    before = dict(store.expressions)
    normalize(store, StaticTypeStore(expressions={x: frozenset({ValueType.integer})}))
    assert store.expressions == before
