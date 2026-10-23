"""Domain evaluation for conversions operators."""

from __future__ import annotations

import math
from itertools import product

from ..internal_input import ExprId
from ..python_input import Operator
from .evaluation import DomainHandler, EvaluationContext
from .values import (
    EMPTY_DOMAIN,
    UNKNOWN_DOMAIN,
    Domain,
    DomainValue,
    domain_from_values,
    join_domains,
)


def _eval_concat(context: EvaluationContext, op: Operator, doms: list[Domain], expr_id: ExprId | None) -> Domain:
    """Compute domain for Operation(Concat, [x, y])."""
    if len(doms) != 2:
        context.diagnostics.error(f"concat expects 2 arguments, got {len(doms)}", expr_id=expr_id)
        return UNKNOWN_DOMAIN
    dx, dy = doms
    if dx.unknown or dy.unknown:
        return UNKNOWN_DOMAIN
    if any(
        d.bools
        or d.int_count()
        or d.reals
        or d.tuples
        or d.explicit_sets
        or d.implicit_set_elements is not None
        or d.has_none
        for d in doms
    ):
        context.diagnostics.error(
            "concat requires string arguments; ignoring unsupported values",
            expr_id=expr_id,
        )
    if len(dx.strings) * len(dy.strings) > context.threshold:
        return UNKNOWN_DOMAIN
    return Domain(strings=frozenset(a + b for a, b in product(dx.strings, dy.strings)))


def _eval_length(context: EvaluationContext, op: Operator, doms: list[Domain], expr_id: ExprId | None) -> Domain:
    """Compute domain for Operation(Length, [x])."""
    if len(doms) != 1:
        context.diagnostics.error(f"length expects 1 argument, got {len(doms)}", expr_id=expr_id)
        return UNKNOWN_DOMAIN
    dx = doms[0]
    if dx.unknown:
        return UNKNOWN_DOMAIN
    if dx.bools or dx.int_count() or dx.reals or dx.has_none:
        context.diagnostics.error(
            "length requires strings, tuples, or sets; ignoring unsupported values",
            expr_id=expr_id,
        )
    lengths = set(dx.possible_set_sizes())
    for s in dx.strings:
        lengths.add(len(s))
    for t in dx.tuples:
        lengths.add(len(t))
    return Domain(ints=frozenset(lengths))


def _eval_tuple_get(context: EvaluationContext, op: Operator, doms: list[Domain], expr_id: ExprId | None) -> Domain:
    """Compute domain for Operation(TupleGet, [tuple_expr, index_expr])."""
    if len(doms) != 2:
        context.diagnostics.error(
            f"tuple_get expects 2 arguments, got {len(doms)}",
            expr_id=expr_id,
        )
        return UNKNOWN_DOMAIN
    dt, di = doms
    if dt.unknown or di.unknown:
        return UNKNOWN_DOMAIN
    if dt.is_empty() or di.is_empty():
        return EMPTY_DOMAIN
    if len(dt.tuples) * di.int_count() > context.threshold:
        return UNKNOWN_DOMAIN
    results: list[DomainValue] = []
    for tup, idx in product(dt.tuples, di.iter_ints()):
        if 0 <= idx < len(tup):
            results.append(tup[idx])
        else:
            context.diagnostics.warn(f"tuple_get index {idx} out of bounds", expr_id=expr_id)
    return domain_from_values(results)


def _eval_conversion(context: EvaluationContext, op: Operator, doms: list[Domain], expr_id: ExprId | None) -> Domain:
    """Compute domains for numeric rounding and type conversions."""
    if len(doms) != 1:
        context.diagnostics.error(f"{op} expects 1 argument, got {len(doms)}", expr_id=expr_id)
        return UNKNOWN_DOMAIN
    dx = doms[0]
    if dx.unknown:
        return UNKNOWN_DOMAIN
    if dx.is_empty():
        return EMPTY_DOMAIN

    if op in (Operator.floor, Operator.ceil, Operator.int_from_real):
        mapping = {
            Operator.floor: math.floor,
            Operator.ceil: math.ceil,
            Operator.int_from_real: int,
        }[op]
        return join_domains(
            (
                Domain(ints=dx.ints | frozenset(mapping(value) for value in dx.reals)),
                Domain(int_range=dx.int_range),
            ),
            context.threshold,
        )

    if op == Operator.real_from_int:
        if dx.int_count() + len(dx.reals) > context.threshold:
            return UNKNOWN_DOMAIN
        return Domain(reals=dx.reals | frozenset(float(value) for value in dx.iter_ints()))
    return UNKNOWN_DOMAIN


HANDLERS: dict[Operator, DomainHandler] = {
    Operator.concat: _eval_concat,
    Operator.length: _eval_length,
    Operator.tuple_get: _eval_tuple_get,
    Operator.real_from_int: _eval_conversion,
    Operator.floor: _eval_conversion,
    Operator.ceil: _eval_conversion,
    Operator.int_from_real: _eval_conversion,
}
