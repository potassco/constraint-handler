"""Domain evaluation for comparisons operators."""

from __future__ import annotations

import operator
from itertools import product

from ..diagnostics import ExpressionLocation
from ..python_input import Operator
from .evaluation import DomainHandler, EvaluationContext
from .values import (
    EMPTY_DOMAIN,
    TRUE_FALSE_DOMAIN,
    UNKNOWN_DOMAIN,
    Domain,
    value_key,
)


def _ordered_bounds(dom: Domain) -> tuple[float | int, float | int] | None:
    """Return (min, max) over numeric/boolean values if domain is purely ordered."""
    if (
        dom.unknown
        or dom.has_none
        or dom.strings
        or dom.tuples
        or dom.explicit_sets
        or dom.implicit_set_elements is not None
    ):
        return None
    mins: list[float | int] = []
    maxs: list[float | int] = []
    if dom.bools:
        mins.append(int(min(dom.bools)))
        maxs.append(int(max(dom.bools)))
    bounds = dom.integer_bounds()
    if bounds is not None:
        mins.append(bounds[0])
        maxs.append(bounds[1])
    if dom.reals:
        mins.append(min(dom.reals))
        maxs.append(max(dom.reals))
    if not mins:
        return None
    return (min(mins), max(maxs))


def _eval_equality(
    context: EvaluationContext, op: Operator, doms: list[Domain], location: ExpressionLocation
) -> Domain:
    """Compute domain for eq and neq."""
    if len(doms) != 2:
        context.diagnostics.error(f"{op} expects 2 arguments, got {len(doms)}", location=location)
        return UNKNOWN_DOMAIN
    dx, dy = doms
    if dx.unknown or dy.unknown:
        return TRUE_FALSE_DOMAIN
    if dx.is_empty() or dy.is_empty():
        return EMPTY_DOMAIN
    cx, cy = dx.cardinality(), dy.cardinality()
    if cx == cy == 1:
        equal = value_key(next(dx.iter_values())) == value_key(next(dy.iter_values()))
        return Domain(bools=frozenset({equal if op == Operator.eq else not equal}))
    if cx is None or cy is None or cx * cy > context.boolean_threshold:
        return TRUE_FALSE_DOMAIN
    bools: set[bool] = set()
    for a, b in product(dx.iter_values(), dy.iter_values()):
        eq_val = value_key(a) == value_key(b)
        bools.add(eq_val if op == Operator.eq else not eq_val)
    return Domain(bools=frozenset(bools))


def _eval_comparison(
    context: EvaluationContext, op: Operator, doms: list[Domain], location: ExpressionLocation
) -> Domain:
    """Compute domain for leq, lt, geq, gt."""
    if len(doms) != 2:
        context.diagnostics.error(f"{op} expects 2 arguments, got {len(doms)}", location=location)
        return UNKNOWN_DOMAIN
    dx, dy = doms
    if dx.unknown or dy.unknown:
        return TRUE_FALSE_DOMAIN
    if dx.is_empty() or dy.is_empty():
        return EMPTY_DOMAIN
    bx = _ordered_bounds(dx)
    by = _ordered_bounds(dy)
    if bx is None or by is None:
        context.diagnostics.error(
            f"{op} requires ordered numeric or boolean domains",
            location=location,
        )
        return TRUE_FALSE_DOMAIN
    min_x, max_x = bx
    min_y, max_y = by
    match op:
        case Operator.leq:
            if max_x <= min_y:
                return Domain(bools=frozenset({True}))
            if min_x > max_y:
                return Domain(bools=frozenset({False}))
            cmp_fn = operator.le
        case Operator.lt:
            if max_x < min_y:
                return Domain(bools=frozenset({True}))
            if min_x >= max_y:
                return Domain(bools=frozenset({False}))
            cmp_fn = operator.lt
        case Operator.geq:
            if min_x >= max_y:
                return Domain(bools=frozenset({True}))
            if max_x < min_y:
                return Domain(bools=frozenset({False}))
            cmp_fn = operator.ge
        case Operator.gt:
            if min_x > max_y:
                return Domain(bools=frozenset({True}))
            if max_x <= min_y:
                return Domain(bools=frozenset({False}))
            cmp_fn = operator.gt
        case _:  # pragma: no cover
            return TRUE_FALSE_DOMAIN

    cx, cy = dx.cardinality(), dy.cardinality()
    if cx is not None and cy is not None and cx * cy <= context.boolean_threshold:
        bools: set[bool] = set()
        for a, b in product(dx.iter_values(), dy.iter_values()):
            if isinstance(a, (bool, int, float)) and isinstance(b, (bool, int, float)):
                bools.add(cmp_fn(a, b))
        return Domain(bools=frozenset(bools))
    return TRUE_FALSE_DOMAIN


HANDLERS: dict[Operator, DomainHandler] = {
    Operator.eq: _eval_equality,
    Operator.neq: _eval_equality,
    Operator.leq: _eval_comparison,
    Operator.lt: _eval_comparison,
    Operator.geq: _eval_comparison,
    Operator.gt: _eval_comparison,
}
