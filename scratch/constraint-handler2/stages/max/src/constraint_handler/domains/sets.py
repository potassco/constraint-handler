"""Domain evaluation for sets operators."""

from __future__ import annotations

import math
from itertools import product

from ..internal_input import ExprId
from ..python_input import Operator
from .evaluation import DomainHandler, EvaluationContext
from .values import (
    EMPTY_DOMAIN,
    TRUE_FALSE_DOMAIN,
    UNKNOWN_DOMAIN,
    Domain,
    SetValue,
    domain_from_values,
    has_value_collisions,
    union_domains,
    value_key,
)


def _eval_set_domains(
    context: EvaluationContext, op: Operator, doms: list[Domain], expr_id: ExprId | None
) -> Domain:
    """Construct sets from evaluated arguments without dropping invalid values."""
    if not doms:
        return Domain(explicit_sets=frozenset({frozenset()}))
    if any(d.unknown for d in doms):
        return UNKNOWN_DOMAIN
    if any(d.is_empty() for d in doms):
        return EMPTY_DOMAIN
    counts = [d.cardinality() for d in doms]
    if any(c is None for c in counts):  # pragma: no cover
        return UNKNOWN_DOMAIN
    int_counts = [c for c in counts if c is not None]
    if math.prod(int_counts) <= context.threshold:
        value_lists: list[list[SetValue]] = []
        for d in doms:
            vals: list[SetValue] = []
            for v in d.iter_values():
                if isinstance(v, frozenset):
                    context.diagnostics.error(
                        "Nested sets are not supported", expr_id=expr_id
                    )
                    return UNKNOWN_DOMAIN
                vals.append(v)
            value_lists.append(vals)
        results: list[frozenset[SetValue]] = []
        for combo in product(*value_lists):
            if has_value_collisions(combo):
                context.diagnostics.warn(
                    "set_make contains values that Python sets cannot distinguish",
                    expr_id=expr_id,
                )
                return UNKNOWN_DOMAIN
            results.append(frozenset(combo))
        return domain_from_values(results)
    merged = union_domains(doms, context.threshold)
    if merged.unknown or merged.int_range is not None:
        return UNKNOWN_DOMAIN
    all_scalars: list[SetValue] = []
    for v in merged.iter_values():
        if isinstance(v, frozenset):
            return UNKNOWN_DOMAIN
        all_scalars.append(v)
    if has_value_collisions(all_scalars):
        context.diagnostics.warn(
            "set_make contains values that Python sets cannot distinguish",
            expr_id=expr_id,
        )
        return UNKNOWN_DOMAIN
    return Domain(implicit_set_elements=frozenset(all_scalars))


def _eval_set_ops(
    context: EvaluationContext, op: Operator, doms: list[Domain], expr_id: ExprId | None
) -> Domain:
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
                    expr_id=expr_id,
                )
                return UNKNOWN_DOMAIN
            ds = doms[0]
            sizes = {len(s) for s in ds.explicit_sets}
            if ds.implicit_set_elements is not None:
                sizes.update(range(len(ds.implicit_set_elements) + 1))
            return Domain(ints=frozenset(sizes))

        case Operator.set_isin | Operator.set_notin:
            if len(doms) != 2:
                context.diagnostics.error(
                    f"{op} expects 2 arguments, got {len(doms)}",
                    expr_id=expr_id,
                )
                return UNKNOWN_DOMAIN
            dx, ds = doms
            cx, cs = dx.cardinality(), ds.cardinality()
            if (
                cx is not None
                and cs is not None
                and cx * cs <= context.boolean_threshold
            ):
                bools: set[bool] = set()
                sets = [s for s in ds.iter_values() if isinstance(s, frozenset)]
                scalars = [v for v in dx.iter_values() if not isinstance(v, frozenset)]
                for val, s in product(scalars, sets):
                    inside = any(value_key(val) == value_key(item) for item in s)
                    bools.add(inside if op == Operator.set_isin else not inside)
                return Domain(bools=frozenset(bools))
            return TRUE_FALSE_DOMAIN

        case Operator.union | Operator.inter | Operator.diff:
            if len(doms) != 2:
                context.diagnostics.error(
                    f"{op} expects 2 arguments, got {len(doms)}",
                    expr_id=expr_id,
                )
                return UNKNOWN_DOMAIN
            da, db = doms
            ca, cb = da.cardinality(), db.cardinality()
            if ca is not None and cb is not None and ca * cb <= context.threshold:
                sets_a = [s for s in da.iter_values() if isinstance(s, frozenset)]
                sets_b = [s for s in db.iter_values() if isinstance(s, frozenset)]
                if op == Operator.union:
                    if any(
                        has_value_collisions((*sa, *sb))
                        for sa, sb in product(sets_a, sets_b)
                    ):
                        context.diagnostics.warn(
                            "union contains values that Python sets cannot distinguish",
                            expr_id=expr_id,
                        )
                        return UNKNOWN_DOMAIN
                    res_sets = [sa | sb for sa, sb in product(sets_a, sets_b)]
                elif op == Operator.inter:
                    res_sets = [
                        frozenset(
                            v for v in sa if value_key(v) in {value_key(w) for w in sb}
                        )
                        for sa, sb in product(sets_a, sets_b)
                    ]
                else:
                    res_sets = [
                        frozenset(
                            v
                            for v in sa
                            if value_key(v) not in {value_key(w) for w in sb}
                        )
                        for sa, sb in product(sets_a, sets_b)
                    ]
                return domain_from_values(res_sets)
            for domain in (da, db) if op != Operator.diff else (da,):
                if has_value_collisions(
                    value
                    for members in (
                        *domain.explicit_sets,
                        domain.implicit_set_elements or frozenset(),
                    )
                    for value in members
                ):
                    context.diagnostics.warn(
                        f"{op} member universe contains values that Python sets cannot distinguish",
                        expr_id=expr_id,
                    )
                    return UNKNOWN_DOMAIN
            pa = da.potential_set_members()
            pb = db.potential_set_members()
            if op == Operator.union:
                if has_value_collisions((*pa, *pb)):
                    context.diagnostics.warn(
                        "union contains values that Python sets cannot distinguish",
                        expr_id=expr_id,
                    )
                    return UNKNOWN_DOMAIN
                return Domain(implicit_set_elements=pa | pb)
            if op == Operator.inter:
                return Domain(
                    implicit_set_elements=frozenset(
                        v for v in pa if value_key(v) in {value_key(w) for w in pb}
                    )
                )
            return Domain(implicit_set_elements=pa)

        case Operator.subset:
            if len(doms) != 2:
                context.diagnostics.error(
                    f"subset expects 2 arguments, got {len(doms)}",
                    expr_id=expr_id,
                )
                return UNKNOWN_DOMAIN
            da, db = doms
            ca, cb = da.cardinality(), db.cardinality()
            if (
                ca is not None
                and cb is not None
                and ca * cb <= context.boolean_threshold
            ):
                sets_a = [s for s in da.iter_values() if isinstance(s, frozenset)]
                sets_b = [s for s in db.iter_values() if isinstance(s, frozenset)]
                return Domain(
                    bools=frozenset(
                        {value_key(v) for v in sa} <= {value_key(v) for v in sb}
                        for sa, sb in product(sets_a, sets_b)
                    )
                )
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
