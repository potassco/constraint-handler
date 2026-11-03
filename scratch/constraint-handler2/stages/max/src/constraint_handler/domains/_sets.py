"""Compute set domains from possible members, without enumerating subsets."""

from __future__ import annotations

from ..python_input import Operator
from ._domain import (
    EMPTY_DOMAIN,
    TRUE_FALSE_DOMAIN,
    UNKNOWN_DOMAIN,
    Domain,
    _Range,
    join_domains,
)


def intersect_scalar_domains(left: Domain, right: Domain) -> Domain:
    """Keep possible members common to both domains, using numeric equality."""
    if left.unknown:
        return right
    if right.unknown:
        return left
    intervals = left.integers.intersection(right.integers)
    real_integers = [
        int(value)
        for value in right.reals
        if value.is_integer() and left.contains_int(int(value))
    ]
    intervals = intervals.union(_Range((value, value) for value in real_integers))
    return Domain(
        bools=left.bools & right.bools,
        integers=intervals,
        reals=(
            value
            for value in left.reals
            if value in right.reals
            or value.is_integer()
            and right.contains_int(int(value))
        ),
        has_none=left.has_none and right.has_none,
        strings=left.strings & right.strings,
    )


def set_operation(op: Operator, doms: list[Domain]) -> Domain:
    """Compute approximate set domains using their possible members, not exact sets."""
    if any(domain.is_empty() for domain in doms):
        return EMPTY_DOMAIN
    if op == Operator.set_make:
        return Domain(set_base=join_domains(doms))
    if op in {Operator.set_isin, Operator.set_notin}:
        element, collection = doms
        if collection.set_base is not None and not element.unknown:
            common = intersect_scalar_domains(element, collection.set_base)
            if common.is_empty():
                return Domain(bools=(op == Operator.set_notin,))
        return TRUE_FALSE_DOMAIN
    if op == Operator.subset:
        if doms[0].set_base is not None and doms[0].set_base.is_empty():
            return Domain(bools=(True,))
        return TRUE_FALSE_DOMAIN
    if op == Operator.cardinality:
        if doms[0].unknown:
            return UNKNOWN_DOMAIN
        base = doms[0].set_base
        size = None if base is None else base.cardinality()
        return UNKNOWN_DOMAIN if size is None else Domain(int_range=(0, size))
    bases = [UNKNOWN_DOMAIN if domain.unknown else domain.set_base for domain in doms]
    if any(base is None for base in bases):
        return EMPTY_DOMAIN
    known = [base for base in bases if base is not None]
    if op == Operator.union:
        return Domain(set_base=join_domains(known))
    if not known:
        return UNKNOWN_DOMAIN
    if op == Operator.diff:
        return Domain(set_base=known[0])
    if op == Operator.inter:
        base = known[0]
        for other in known[1:]:
            base = intersect_scalar_domains(base, other)
        return Domain(set_base=base)
    return UNKNOWN_DOMAIN
