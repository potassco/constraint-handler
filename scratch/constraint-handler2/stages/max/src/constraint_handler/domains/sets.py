"""Domain evaluation for sets operators."""

from __future__ import annotations

from collections.abc import Iterable
from itertools import product

from ..diagnostics import ExpressionLocation
from ..python_input import Operator
from .evaluation import (
    DomainHandler,
    EnumerationDecision,
    EvaluationContext,
    bounded_product_decision,
)
from .values import (
    EMPTY_DOMAIN,
    TRUE_FALSE_DOMAIN,
    UNKNOWN_DOMAIN,
    Domain,
    SetValue,
    domain_from_values,
    has_value_collisions,
    join_domains,
    value_key,
)


def _member_keys(members: Iterable[SetValue]) -> frozenset[object]:
    """Index set members using recursive language equality."""
    return frozenset(value_key(member) for member in members)


def _select_members(
    members: Iterable[SetValue], keys: frozenset[object], *, exclude: bool = False
) -> frozenset[SetValue]:
    """Select intersection or difference members against a precomputed index."""
    return frozenset(member for member in members if (value_key(member) in keys) != exclude)


def _checked_members(members: Iterable[SetValue]) -> frozenset[SetValue] | None:
    """Build a member set unless Python equality would collapse distinct values."""
    values = tuple(members)
    if has_value_collisions(values):
        return None
    return frozenset(values)


def _eval_set_domains(
    context: EvaluationContext, op: Operator, doms: list[Domain], location: ExpressionLocation
) -> Domain:
    """Construct sets from evaluated arguments without dropping invalid values."""
    if any(
        d.tuples
        or d.tuple_domains
        or d.explicit_sets
        or d.implicit_set_elements is not None
        for d in doms
    ):
        context.diagnostics.error(
            "Set elements must be scalar values", location=location
        )
        return UNKNOWN_DOMAIN
    if not doms:
        return Domain(explicit_sets=frozenset({frozenset()}))
    decision = bounded_product_decision(doms, context.threshold)
    if decision == EnumerationDecision.UNKNOWN:
        return UNKNOWN_DOMAIN
    if decision == EnumerationDecision.EMPTY:
        return EMPTY_DOMAIN
    if decision == EnumerationDecision.ENUMERABLE:
        value_lists: list[list[SetValue]] = []
        for d in doms:
            vals: list[SetValue] = []
            for v in d.iter_values():
                if isinstance(v, frozenset):
                    context.diagnostics.error("Nested sets are not supported", location=location)
                    return UNKNOWN_DOMAIN
                vals.append(v)
            value_lists.append(vals)
        results: list[frozenset[SetValue]] = []
        for combo in product(*value_lists):
            members = _checked_members(combo)
            if members is None:
                context.diagnostics.warn(
                    "set_make contains values that Python sets cannot distinguish",
                    location=location,
                )
                return UNKNOWN_DOMAIN
            results.append(members)
        return domain_from_values(results)
    merged = join_domains(doms, context.threshold)
    if merged.unknown or merged.int_range is not None:
        return UNKNOWN_DOMAIN
    all_scalars: list[SetValue] = []
    for v in merged.iter_values():
        if isinstance(v, frozenset):
            return UNKNOWN_DOMAIN
        all_scalars.append(v)
    members = _checked_members(all_scalars)
    if members is None:
        context.diagnostics.warn(
            "set_make contains values that Python sets cannot distinguish",
            location=location,
        )
        return UNKNOWN_DOMAIN
    return Domain(implicit_set_elements=members)


def _eval_set_ops(context: EvaluationContext, op: Operator, doms: list[Domain], location: ExpressionLocation) -> Domain:
    """Compute domain for set operations."""
    if any(d.unknown for d in doms):
        if op in (Operator.set_isin, Operator.set_notin, Operator.subset):
            return TRUE_FALSE_DOMAIN
        return UNKNOWN_DOMAIN
    if any(d.is_empty() for d in doms):
        return EMPTY_DOMAIN

    match op:
        case Operator.cardinality:
            if len(doms) != 1:
                context.diagnostics.error(
                    f"cardinality expects 1 argument, got {len(doms)}",
                    location=location,
                )
                return UNKNOWN_DOMAIN
            ds = doms[0]
            return Domain(ints=ds.possible_set_sizes())

        case Operator.set_isin | Operator.set_notin:
            if len(doms) != 2:
                context.diagnostics.error(
                    f"{op} expects 2 arguments, got {len(doms)}",
                    location=location,
                )
                return UNKNOWN_DOMAIN
            dx, ds = doms
            if bounded_product_decision(doms, context.boolean_threshold) == EnumerationDecision.ENUMERABLE:
                bools: set[bool] = set()
                sets = [_member_keys(s) for s in ds.iter_values() if isinstance(s, frozenset)]
                scalars = [v for v in dx.iter_values() if not isinstance(v, frozenset)]
                scalar_keys = [value_key(value) for value in scalars]
                for key, keys in product(scalar_keys, sets):
                    inside = key in keys
                    bools.add(inside if op == Operator.set_isin else not inside)
                return Domain(bools=frozenset(bools))
            return TRUE_FALSE_DOMAIN

        case Operator.union | Operator.inter | Operator.diff:
            if len(doms) != 2:
                context.diagnostics.error(
                    f"{op} expects 2 arguments, got {len(doms)}",
                    location=location,
                )
                return UNKNOWN_DOMAIN
            da, db = doms
            if bounded_product_decision(doms, context.threshold) == EnumerationDecision.ENUMERABLE:
                sets_a = [s for s in da.iter_values() if isinstance(s, frozenset)]
                sets_b = [s for s in db.iter_values() if isinstance(s, frozenset)]
                res_sets: list[frozenset[SetValue]] = []
                if op == Operator.union:
                    for sa, sb in product(sets_a, sets_b):
                        members = _checked_members((*sa, *sb))
                        if members is None:
                            context.diagnostics.warn(
                                "union contains values that Python sets cannot distinguish",
                                location=location,
                            )
                            return UNKNOWN_DOMAIN
                        res_sets.append(members)
                else:
                    right_keys = [_member_keys(members) for members in sets_b]
                    res_sets = [
                        _select_members(sa, keys, exclude=op == Operator.diff)
                        for sa, keys in product(sets_a, right_keys)
                    ]
                return domain_from_values(res_sets)
            for domain in (da, db) if op != Operator.diff else (da,):
                if (
                    _checked_members(
                        value
                        for members in (
                            *domain.explicit_sets,
                            domain.implicit_set_elements or frozenset(),
                        )
                        for value in members
                    )
                    is None
                ):
                    context.diagnostics.warn(
                        f"{op} member universe contains values that Python sets cannot distinguish",
                        location=location,
                    )
                    return UNKNOWN_DOMAIN
            pa = da.potential_set_members()
            pb = db.potential_set_members()
            if op == Operator.union:
                members = _checked_members((*pa, *pb))
                if members is None:
                    context.diagnostics.warn(
                        "union contains values that Python sets cannot distinguish",
                        location=location,
                    )
                    return UNKNOWN_DOMAIN
                return Domain(implicit_set_elements=members)
            if op == Operator.inter:
                return Domain(implicit_set_elements=_select_members(pa, _member_keys(pb)))
            return Domain(implicit_set_elements=pa)

        case Operator.subset:
            if len(doms) != 2:
                context.diagnostics.error(
                    f"subset expects 2 arguments, got {len(doms)}",
                    location=location,
                )
                return UNKNOWN_DOMAIN
            da, db = doms
            if bounded_product_decision(doms, context.boolean_threshold) == EnumerationDecision.ENUMERABLE:
                sets_a = [_member_keys(s) for s in da.iter_values() if isinstance(s, frozenset)]
                sets_b = [_member_keys(s) for s in db.iter_values() if isinstance(s, frozenset)]
                return Domain(bools=frozenset(sa <= sb for sa, sb in product(sets_a, sets_b)))
            return TRUE_FALSE_DOMAIN

        case _:  # pragma: no cover
            return UNKNOWN_DOMAIN


HANDLERS: dict[Operator, DomainHandler] = {
    Operator.set_make: _eval_set_domains,
    Operator.cardinality: _eval_set_ops,
    Operator.set_isin: _eval_set_ops,
    Operator.set_notin: _eval_set_ops,
    Operator.union: _eval_set_ops,
    Operator.inter: _eval_set_ops,
    Operator.diff: _eval_set_ops,
    Operator.subset: _eval_set_ops,
}
