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
        Operator.linear_comparison,
        (
            ValueDef(ValueType.string, relation.value),
            (ValueDef(ValueType.integer, 2), x),
            ValueDef(ValueType.integer, -3),
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
def test_real_arithmetic_is_not_normalized(
    relation: bool, choices: tuple[int | float, ...]
) -> None:
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
        Operator.linear_comparison,
        (
            ValueDef(ValueType.string, "eq"),
            (ValueDef(ValueType.integer, 1), x),
            ValueDef(ValueType.integer, -1),
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


@pytest.mark.parametrize(
    "expression",
    [
        Operation(Operator.mult, (2, Operation(Operator.mult, (3, VariableRef("x"))))),
        Operation(Operator.mult, (Operation(Operator.mult, (2, 3)), VariableRef("x"))),
    ],
)
def test_nested_scalar_products_combine_coefficients(expression: Operation) -> None:
    """Flatten nested scalar factors without distributing over sums."""
    store = ConstraintStore()
    x = VariableRef("x")
    store.define(VariableRef("result"), expression)
    expr_id = store.variables[VariableRef("result")].definitions[0].value
    normalize(store, StaticTypeStore(expressions={x: frozenset({ValueType.integer})}))
    assert store.expressions[expr_id] == InternalOperation(
        Operator.linear_integer,
        ((ValueDef(ValueType.integer, 6), x), ValueDef(ValueType.integer, 0)),
    )


@pytest.mark.parametrize(
    "arguments",
    [
        (0, Operation(Operator.mult, (VariableRef("x"), VariableRef("y")))),
        (0, VariableRef("x"), VariableRef("y")),
        (0, Operation(Operator.add, (VariableRef("x"), 1))),
    ],
)
def test_zero_product_prunes_compound_terms(
    arguments: tuple[int | VariableRef | Operation, ...],
) -> None:
    """Drop integer compound factors whenever their scalar coefficient is zero."""
    store = ConstraintStore()
    store.define(VariableRef("result"), Operation(Operator.mult, arguments))
    expr_id = store.variables[VariableRef("result")].definitions[0].value
    normalize(
        store,
        StaticTypeStore(
            expressions={
                VariableRef(name): frozenset({ValueType.integer}) for name in ("x", "y")
            }
        ),
    )
    assert store.expressions[expr_id] == InternalOperation(
        Operator.linear_integer, (ValueDef(ValueType.integer, 0),)
    )


@pytest.mark.parametrize("operator", [Operator.abs, Operator.int_div, Operator.floor])
@pytest.mark.parametrize(
    "relation",
    [Operator.eq, Operator.neq, Operator.lt, Operator.leq, Operator.gt, Operator.geq],
)
def test_relations_use_known_integer_expression_types(
    operator: Operator, relation: Operator
) -> None:
    """Retain integer type proofs when normalization changes an operator's child."""
    store = ConstraintStore()
    x = VariableRef("x")
    y = VariableRef("y")
    store.choose_from_iterator(x, (1, 2))
    store.choose_from_iterator(y, (1, 2))
    argument = Operation(Operator.add, (x, 1))
    operands = (argument, 2) if operator == Operator.int_div else (argument,)
    store.ensure(Operation(relation, (Operation(operator, operands), y)))
    diagnostics = Diagnostics()
    types = compute_static_types(
        store, compute_evaluation_order(store, diagnostics), diagnostics
    )
    normalize(store, types)
    result = store.expressions[store.constraints[0].expr]
    assert isinstance(result, InternalOperation)
    assert result.op == Operator.linear_comparison
    assert result.args[0] == ValueDef(ValueType.string, relation.value)
    assert result.args[-1] == ValueDef(ValueType.integer, 0)
    assert result.args[2] == (ValueDef(ValueType.integer, -1), y)
    first = dict(store.expressions)
    normalize(store, types)
    assert store.expressions == first
    assert not diagnostics.has_errors


def test_shared_lambda_is_normalized_per_call() -> None:
    """Keep integer and real calls independent even when they share a callback."""
    store = ConstraintStore()
    parameter = VariableRef("parameter")
    store.choose(parameter, 1.5)
    callback = Lambda((parameter,), Operation(Operator.add, (parameter, parameter)))
    store.define(
        VariableRef("result"),
        (
            Operation(Operator.lambda_, (callback, 2)),
            Operation(Operator.lambda_, (callback, 2.0)),
        ),
    )
    diagnostics = Diagnostics()
    types = compute_static_types(
        store, compute_evaluation_order(store, diagnostics), diagnostics
    )
    expr_id = store.variables[VariableRef("result")].definitions[0].value
    before = store.expressions[expr_id]
    assert isinstance(before, tuple)
    normalize(store, types)
    result = store.expressions[expr_id]
    assert isinstance(result, tuple)
    call = result[0]
    assert isinstance(call, InternalOperation)
    normalized = call.args[0]
    assert isinstance(normalized, InternalLambda)
    assert normalized.expr == InternalOperation(
        Operator.linear_integer,
        ((ValueDef(ValueType.integer, 2), parameter), ValueDef(ValueType.integer, 0)),
    )
    assert result[1] == before[1]
    assert not diagnostics.has_errors


@pytest.mark.parametrize("operator", [Operator.abs, Operator.int_div, Operator.floor])
def test_lambda_relations_keep_scoped_integer_expression_proofs(
    operator: Operator,
) -> None:
    """Transfer scoped integer proofs when an operation's child is normalized."""
    store = ConstraintStore()
    parameter = VariableRef("parameter")
    argument = Operation(Operator.add, (parameter, 1))
    operands = (argument, 2) if operator == Operator.int_div else (argument,)
    store.ensure(
        Operation(
            Operator.lambda_,
            (
                Lambda(
                    (parameter,),
                    Operation(Operator.eq, (Operation(operator, operands), parameter)),
                ),
                2,
            ),
        )
    )
    diagnostics = Diagnostics()
    types = compute_static_types(
        store, compute_evaluation_order(store, diagnostics), diagnostics
    )
    normalize(store, types)
    call = store.expressions[store.constraints[0].expr]
    assert isinstance(call, InternalOperation)
    callback = call.args[0]
    assert isinstance(callback, InternalLambda)
    relation = callback.expr
    assert isinstance(relation, InternalOperation)
    assert relation.op == Operator.linear_comparison
    assert relation.args[0] == ValueDef(ValueType.string, "eq")
    assert relation.args[-1] == ValueDef(ValueType.integer, 0)
    first = dict(store.expressions)
    normalize(store, types)
    assert store.expressions == first
    assert not diagnostics.has_errors


def test_nested_lambda_bindings_preserve_free_and_shadowed_types() -> None:
    """Normalize captured integers without using their types for shadowed reals."""
    store = ConstraintStore()
    outer = VariableRef("outer")
    inner = VariableRef("inner")
    store.define(
        VariableRef("result"),
        Operation(
            Operator.lambda_,
            (
                Lambda(
                    (outer,),
                    (
                        Operation(
                            Operator.lambda_,
                            (
                                Lambda(
                                    (inner,),
                                    Operation(Operator.add, (outer, outer, inner)),
                                ),
                                Operation(Operator.abs, (outer,)),
                            ),
                        ),
                        Operation(
                            Operator.lambda_,
                            (
                                Lambda((outer,), Operation(Operator.add, (outer, 1))),
                                1.5,
                            ),
                        ),
                    ),
                ),
                2,
            ),
        ),
    )
    diagnostics = Diagnostics()
    types = compute_static_types(
        store, compute_evaluation_order(store, diagnostics), diagnostics
    )
    expr_id = store.variables[VariableRef("result")].definitions[0].value
    normalize(store, types)
    call = store.expressions[expr_id]
    assert isinstance(call, InternalOperation)
    callback = call.args[0]
    assert isinstance(callback, InternalLambda)
    assert isinstance(callback.expr, tuple)
    integer_call, real_call = callback.expr
    assert isinstance(integer_call, InternalOperation)
    integer_callback = integer_call.args[0]
    assert isinstance(integer_callback, InternalLambda)
    assert integer_callback.expr == InternalOperation(
        Operator.linear_integer,
        (
            (ValueDef(ValueType.integer, 2), outer),
            (ValueDef(ValueType.integer, 1), inner),
            ValueDef(ValueType.integer, 0),
        ),
    )
    assert isinstance(real_call, InternalOperation)
    real_callback = real_call.args[0]
    assert isinstance(real_callback, InternalLambda)
    assert real_callback.expr == InternalOperation(
        Operator.add, (outer, ValueDef(ValueType.integer, 1))
    )
    assert not diagnostics.has_errors


def test_lambda_unknown_binding_does_not_use_global_parameter_type() -> None:
    """Leave parameter arithmetic unchanged when its call-site type is unknown."""
    store = ConstraintStore()
    parameter = VariableRef("parameter")
    store.ensure(
        Operation(
            Operator.lambda_,
            (
                Lambda((parameter,), Operation(Operator.add, (parameter, parameter))),
                VariableRef("unknown"),
            ),
        )
    )
    before = dict(store.expressions)
    normalize(
        store,
        StaticTypeStore(expressions={parameter: frozenset({ValueType.integer})}),
    )
    assert store.expressions == before


def test_scalar_product_does_not_distribute_over_addition() -> None:
    """Keep a scalar product around a sum rather than scaling its terms."""
    store = ConstraintStore()
    x = VariableRef("x")
    store.define(
        VariableRef("result"),
        Operation(Operator.mult, (2, Operation(Operator.add, (x, 1)))),
    )
    expr_id = store.variables[VariableRef("result")].definitions[0].value
    normalize(store, StaticTypeStore(expressions={x: frozenset({ValueType.integer})}))
    assert store.expressions[expr_id] == InternalOperation(
        Operator.mult,
        (
            ValueDef(ValueType.integer, 2),
            InternalOperation(
                Operator.linear_integer,
                ((ValueDef(ValueType.integer, 1), x), ValueDef(ValueType.integer, 1)),
            ),
        ),
    )


def test_integer_expression_proofs_do_not_leak_into_lambda_scope() -> None:
    """Do not reuse a global integer result when its variable is shadowed by a real."""
    store = ConstraintStore()
    x = VariableRef("x")
    store.choose_from_iterator(x, (1, 2))
    relation = Operation(Operator.eq, (Operation(Operator.abs, (x,)), x))
    store.define(
        VariableRef("result"),
        (relation, Operation(Operator.lambda_, (Lambda((x,), relation), 1.5))),
    )
    expr_id = store.variables[VariableRef("result")].definitions[0].value
    before = store.expressions[expr_id]
    assert isinstance(before, tuple)
    diagnostics = Diagnostics()
    types = compute_static_types(
        store, compute_evaluation_order(store, diagnostics), diagnostics
    )
    normalize(store, types)
    result = store.expressions[expr_id]
    assert isinstance(result, tuple)
    assert result[0] != before[0]
    assert result[1] == before[1]
    assert not diagnostics.has_errors


@pytest.mark.parametrize("choices", [(2,), (2.0,), (2, 2.0)])
def test_lambda_normalization_uses_bound_argument_types(
    choices: tuple[int | float, ...],
) -> None:
    """Normalize parameter arithmetic only when every binding is integer-valued."""
    store = ConstraintStore()
    source = VariableRef("source")
    parameter = VariableRef("parameter")
    store.choose_from_iterator(source, choices)
    store.ensure(
        Operation(
            Operator.lambda_,
            (
                Lambda(
                    (parameter,),
                    Operation(
                        Operator.eq,
                        (Operation(Operator.add, (parameter, parameter)), 4),
                    ),
                ),
                source,
            ),
        )
    )
    diagnostics = Diagnostics()
    types = compute_static_types(
        store, compute_evaluation_order(store, diagnostics), diagnostics
    )
    expr_id = store.constraints[0].expr
    before = store.expressions[expr_id]
    normalize(store, types)
    result = store.expressions[expr_id]
    assert isinstance(result, InternalOperation)
    callback = result.args[0]
    assert isinstance(callback, InternalLambda)
    if all(type(value) is int for value in choices):
        assert callback.expr == InternalOperation(
            Operator.linear_comparison,
            (
                ValueDef(ValueType.string, "eq"),
                (ValueDef(ValueType.integer, 2), parameter),
                ValueDef(ValueType.integer, -4),
            ),
        )
    else:
        assert result == before
    first = dict(store.expressions)
    normalize(store, types)
    assert store.expressions == first
    assert not diagnostics.has_errors
