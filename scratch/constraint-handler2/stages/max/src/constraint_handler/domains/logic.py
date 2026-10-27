"""Domain evaluation for logic operators."""

from __future__ import annotations

from dataclasses import replace
from itertools import product

from ..diagnostics import ExpressionLocation
from ..python_input import Operator
from .evaluation import DomainHandler, EvaluationContext
from .values import (
    EMPTY_DOMAIN,
    TRUE_FALSE_DOMAIN,
    UNKNOWN_DOMAIN,
    Domain,
    join_domains,
)


def _eval_conj(context: EvaluationContext, op: Operator, doms: list[Domain], location: ExpressionLocation) -> Domain:
    """Compute domain for Operation(Conj, [x1, ..., xn])."""
    if any(d.unknown for d in doms):
        return TRUE_FALSE_DOMAIN
    res: set[bool] = set()
    if any(False in d.bools for d in doms):
        res.add(False)
    if all(True in d.bools for d in doms):
        res.add(True)
    return Domain(bools=frozenset(res))


def _eval_disj(context: EvaluationContext, op: Operator, doms: list[Domain], location: ExpressionLocation) -> Domain:
    """Compute domain for Operation(Disj, [x1, ..., xn])."""
    if any(d.unknown for d in doms):
        return TRUE_FALSE_DOMAIN
    res: set[bool] = set()
    if any(True in d.bools for d in doms):
        res.add(True)
    if all(False in d.bools for d in doms):
        res.add(False)
    return Domain(bools=frozenset(res))


def _eval_get_or_else(
    context: EvaluationContext, op: Operator, doms: list[Domain], location: ExpressionLocation
) -> Domain:
    """Compute domain for Operation(GetOrElse, [x, y])."""
    if len(doms) != 2:
        context.diagnostics.error(
            f"get_or_else expects 2 arguments, got {len(doms)}",
            location=location,
        )
        return UNKNOWN_DOMAIN
    dx, dy = doms
    if dx.unknown or dy.unknown:
        return UNKNOWN_DOMAIN
    if not dx.has_none:
        return dx
    dx_without_none = replace(dx, has_none=False)
    return join_domains((dx_without_none, dy), context.threshold)


def _eval_if(context: EvaluationContext, op: Operator, doms: list[Domain], location: ExpressionLocation) -> Domain:
    """Compute domain for Operation(If, [c, x])."""
    if len(doms) != 2:
        context.diagnostics.error(f"if_ expects 2 arguments, got {len(doms)}", location=location)
        return UNKNOWN_DOMAIN
    dc, dx = doms
    if dc.unknown or dx.unknown:
        return UNKNOWN_DOMAIN
    if dc.is_empty():
        return EMPTY_DOMAIN
    if False in dc.bools or dc.has_none:
        return join_domains((dx, Domain(has_none=True)), context.threshold)
    return dx


def _eval_ite(context: EvaluationContext, op: Operator, doms: list[Domain], location: ExpressionLocation) -> Domain:
    """Compute domain for Operation(Ite, [c, x, y])."""
    if len(doms) != 3:
        context.diagnostics.error(f"ite expects 3 arguments, got {len(doms)}", location=location)
        return UNKNOWN_DOMAIN
    dc, dx, dy = doms
    if dc.unknown or dx.unknown or dy.unknown:
        return UNKNOWN_DOMAIN
    if dc == Domain(bools=frozenset({True})):
        return dx
    if dc == Domain(bools=frozenset({False})):
        return dy
    return join_domains((dx, dy), context.threshold)


def _eval_logic_ops(
    context: EvaluationContext, op: Operator, doms: list[Domain], location: ExpressionLocation
) -> Domain:
    """Compute domain for boolean and three-valued logic operators."""
    if any(d.unknown for d in doms):
        return TRUE_FALSE_DOMAIN
    if any(d.is_empty() for d in doms):
        return EMPTY_DOMAIN

    match op:
        case Operator.lnot:
            if len(doms) != 1:
                context.diagnostics.error(
                    f"lnot expects 1 argument, got {len(doms)}",
                    location=location,
                )
                return UNKNOWN_DOMAIN
            d = doms[0]
            return Domain(
                bools=frozenset(not b for b in d.bools),
            )
        case Operator.snot:
            if len(doms) != 1:
                context.diagnostics.error(
                    f"snot expects 1 argument, got {len(doms)}",
                    location=location,
                )
                return UNKNOWN_DOMAIN
            d = doms[0]
            bools = {not b for b in d.bools}
            if d.has_none:
                bools.add(False)
            return Domain(bools=frozenset(bools))
        case Operator.wnot:
            if len(doms) != 1:
                context.diagnostics.error(
                    f"wnot expects 1 argument, got {len(doms)}",
                    location=location,
                )
                return UNKNOWN_DOMAIN
            d = doms[0]
            bools = {not b for b in d.bools}
            if d.has_none:
                bools.add(True)
            return Domain(bools=frozenset(bools))
        case Operator.limp:
            if len(doms) != 2:
                context.diagnostics.error(
                    f"limp expects 2 arguments, got {len(doms)}",
                    location=location,
                )
                return UNKNOWN_DOMAIN
            dx, dy = doms
            return Domain(bools=frozenset((not a) or b for a, b in product(dx.bools, dy.bools)))
        case Operator.lxor | Operator.leqv:
            if any(
                d.int_count()
                or d.reals
                or d.strings
                or d.tuples
                or d.explicit_sets
                or d.implicit_set_elements is not None
                or d.has_none
                for d in doms
            ):
                context.diagnostics.error(
                    f"{op} requires boolean arguments; ignoring unsupported values",
                    location=location,
                )
            if any(not domain.bools for domain in doms):
                return EMPTY_DOMAIN
            if any(len(domain.bools) == 2 for domain in doms):
                return TRUE_FALSE_DOMAIN
            if op == Operator.lxor:
                value = sum(True in domain.bools for domain in doms) % 2 == 1
            else:
                value = sum(False in domain.bools for domain in doms) % 2 == 0
            return Domain(bools=frozenset({value}))
        case _:  # pragma: no cover
            return TRUE_FALSE_DOMAIN


def _eval_has_value(
    context: EvaluationContext, op: Operator, doms: list[Domain], location: ExpressionLocation
) -> Domain:
    """Compute whether a value can be present or absent."""
    if len(doms) != 1:
        context.diagnostics.error(
            f"has_value expects 1 argument, got {len(doms)}",
            location=location,
        )
        return UNKNOWN_DOMAIN
    d = doms[0]
    if d.unknown:
        return TRUE_FALSE_DOMAIN
    if d.is_empty():
        return EMPTY_DOMAIN
    bools: set[bool] = set()
    if d.has_none:
        bools.add(False)
    card = d.cardinality()
    if card is None or card > (1 if d.has_none else 0):
        bools.add(True)
    return Domain(bools=frozenset(bools))


HANDLERS: dict[Operator, DomainHandler] = {
    Operator.conj: _eval_conj,
    Operator.disj: _eval_disj,
    Operator.has_value: _eval_has_value,
    Operator.if_: _eval_if,
    Operator.ite: _eval_ite,
    Operator.get_or_else: _eval_get_or_else,
    Operator.lnot: _eval_logic_ops,
    Operator.snot: _eval_logic_ops,
    Operator.wnot: _eval_logic_ops,
    Operator.limp: _eval_logic_ops,
    Operator.lxor: _eval_logic_ops,
    Operator.leqv: _eval_logic_ops,
}
