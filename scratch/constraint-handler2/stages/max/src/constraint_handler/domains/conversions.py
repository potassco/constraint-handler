"""Domain evaluation for conversions operators."""

from __future__ import annotations

import math
from collections.abc import Iterator
from itertools import product
from typing import cast

from ..diagnostics import ExpressionLocation
from ..python_input import Operator
from .evaluation import DomainHandler, EvaluationContext
from .values import (
    EMPTY_DOMAIN,
    UNKNOWN_DOMAIN,
    Domain,
    TupleValue,
    domain_from_values,
    join_domains,
)


def _eval_make_tuple(
    context: EvaluationContext,
    op: Operator,
    doms: list[Domain],
    location: ExpressionLocation,
) -> Domain:
    """Keep large tuple products factored by position instead of expanding sets."""
    if any(domain.tuples or domain.tuple_domains for domain in doms):
        context.diagnostics.error("Nested tuples are not supported", location=location)
        return UNKNOWN_DOMAIN
    if any(domain.unknown for domain in doms):
        return UNKNOWN_DOMAIN
    if any(domain.is_empty() for domain in doms):
        return EMPTY_DOMAIN
    size = 1
    for domain in doms:
        size *= domain.cardinality() or 0
    if size > context.threshold and doms:
        return Domain(tuple_domains=frozenset({tuple(doms)}))
    rows = cast(
        Iterator[TupleValue],
        product(*(domain.iter_values() for domain in doms)),
    )
    return domain_from_values(rows)


def _eval_concat(
    context: EvaluationContext,
    op: Operator,
    doms: list[Domain],
    location: ExpressionLocation,
) -> Domain:
    """Compute domain for Operation(Concat, [x, y])."""
    if len(doms) != 2:
        context.diagnostics.error(
            f"concat expects 2 arguments, got {len(doms)}", location=location
        )
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
            location=location,
        )
    if len(dx.strings) * len(dy.strings) > context.threshold:
        return UNKNOWN_DOMAIN
    return Domain(strings=frozenset(a + b for a, b in product(dx.strings, dy.strings)))


def _eval_length(
    context: EvaluationContext,
    op: Operator,
    doms: list[Domain],
    location: ExpressionLocation,
) -> Domain:
    """Compute domain for Operation(Length, [x])."""
    if len(doms) != 1:
        context.diagnostics.error(
            f"length expects 1 argument, got {len(doms)}", location=location
        )
        return UNKNOWN_DOMAIN
    dx = doms[0]
    if dx.unknown:
        return UNKNOWN_DOMAIN
    if dx.bools or dx.int_count() or dx.reals or dx.has_none:
        context.diagnostics.error(
            "length requires strings, tuples, or sets; ignoring unsupported values",
            location=location,
        )
    lengths = set(dx.possible_set_sizes())
    for s in dx.strings:
        lengths.add(len(s))
    for t in dx.tuples:
        lengths.add(len(t))
    lengths.update(len(positions) for positions in dx.tuple_domains)
    return Domain(ints=frozenset(lengths))


def eval_tuple_get(
    context: EvaluationContext,
    op: Operator,
    doms: list[Domain],
    location: ExpressionLocation,
) -> Domain:
    """Compute domain for Operation(TupleGet, [tuple_expr, index_expr])."""
    if len(doms) != 2:
        context.diagnostics.error(
            f"tuple_get expects 2 arguments, got {len(doms)}",
            location=location,
        )
        return UNKNOWN_DOMAIN
    dt, di = doms
    if dt.unknown or di.unknown:
        return UNKNOWN_DOMAIN
    if dt.is_empty() or di.is_empty():
        return EMPTY_DOMAIN
    results = [
        value
        for tup in dt.tuples
        for index, value in enumerate(tup)
        if di.contains_int(index)
    ]
    arity = min((len(tup) for tup in (*dt.tuples, *dt.tuple_domains)), default=None)
    bounds = di.integer_bounds()
    if arity is not None and bounds is not None:
        for index in sorted(set(bounds)):
            if index < 0 or index >= arity:
                context.diagnostics.warn(
                    f"tuple_get index {index} out of bounds", location=location
                )
    positions = [
        position
        for alternative in dt.tuple_domains
        for index, position in enumerate(alternative)
        if di.contains_int(index)
    ]
    return join_domains((domain_from_values(results), *positions), context.threshold)


def _eval_conversion(
    context: EvaluationContext,
    op: Operator,
    doms: list[Domain],
    location: ExpressionLocation,
) -> Domain:
    """Compute domains for numeric rounding and type conversions."""
    if len(doms) != 1:
        context.diagnostics.error(
            f"{op} expects 1 argument, got {len(doms)}", location=location
        )
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
        return Domain(
            reals=dx.reals | frozenset(float(value) for value in dx.iter_ints())
        )
    return UNKNOWN_DOMAIN


HANDLERS: dict[Operator, DomainHandler] = {
    Operator.make_tuple: _eval_make_tuple,
    Operator.concat: _eval_concat,
    Operator.length: _eval_length,
    Operator.tuple_get: eval_tuple_get,
    Operator.real_from_int: _eval_conversion,
    Operator.floor: _eval_conversion,
    Operator.ceil: _eval_conversion,
    Operator.int_from_real: _eval_conversion,
}
