"""Compute approximate domains directly from operand domains, without enumeration."""

from dataclasses import replace

from ..python_input import Operator
from ._domain import (
    EMPTY_DOMAIN,
    TRUE_FALSE_DOMAIN,
    UNKNOWN_DOMAIN,
    Domain,
    join_domains,
)
from ._integer import integer_operation
from ._sets import set_operation


def symbolic_operation(
    op: Operator, domains: list[Domain], threshold: int
) -> Domain | None:
    """Compute a domain without enumeration, or return None to request table evaluation."""
    if op in {
        Operator.set_make,
        Operator.union,
        Operator.inter,
        Operator.diff,
        Operator.subset,
        Operator.set_isin,
        Operator.set_notin,
        Operator.cardinality,
    }:
        return set_operation(op, domains)
    if op == Operator.make_tuple:
        return (
            EMPTY_DOMAIN
            if any(domain.is_empty() for domain in domains)
            else Domain(tuple_domains=(tuple(domains),))
        )
    if op in {Operator.conj, Operator.disj}:
        if any(domain.unknown for domain in domains):
            return TRUE_FALSE_DOMAIN
        decisive = op == Operator.disj
        alternatives: list[bool] = []
        if any(decisive in domain.bools for domain in domains):
            alternatives.append(decisive)
        if all((not decisive) in domain.bools for domain in domains):
            alternatives.append(not decisive)
        return Domain(bools=alternatives)
    if op in {
        Operator.lnot,
        Operator.snot,
        Operator.wnot,
        Operator.limp,
        Operator.lxor,
        Operator.leqv,
        Operator.has_value,
    }:
        return _logic(op, domains)
    if op == Operator.get_or_else:
        first, fallback = domains
        if first.unknown or fallback.unknown:
            return UNKNOWN_DOMAIN
        return (
            join_domains((replace(first, has_none=False), fallback))
            if first.has_none
            else first
        )
    if any(domain.unknown for domain in domains):
        return (
            TRUE_FALSE_DOMAIN
            if op
            in {
                Operator.eq,
                Operator.neq,
                Operator.lt,
                Operator.leq,
                Operator.gt,
                Operator.geq,
            }
            else UNKNOWN_DOMAIN
        )
    if any(domain.is_empty() for domain in domains):
        return EMPTY_DOMAIN
    if op == Operator.length:
        domain = domains[0]
        lengths = Domain(
            ints=(
                *map(len, domain.strings),
                *(len(slots) for slots in domain.tuple_domains),
            )
        )
        if domain.set_base is None:
            return lengths
        size = domain.set_base.cardinality()
        return (
            UNKNOWN_DOMAIN
            if size is None
            else join_domains((lengths, Domain(int_range=(0, size))))
        )
    if op == Operator.tuple_get:
        tuples, indices = domains
        return join_domains(
            slot
            for slots in tuples.tuple_domains
            for index, slot in enumerate(slots)
            if indices.contains_int(index)
        )
    if op in {Operator.lt, Operator.leq, Operator.gt, Operator.geq}:
        first, second = (domain.integer_bounds() for domain in domains)
        assert first is not None and second is not None
        if op in {Operator.gt, Operator.geq}:
            first, second = second, first
        if op in {Operator.lt, Operator.gt}:
            return Domain(
                bools=(
                    {True}
                    if first[1] < second[0]
                    else {False}
                    if first[0] >= second[1]
                    else {True, False}
                )
            )
        return Domain(
            bools=(
                {True}
                if first[1] <= second[0]
                else {False}
                if first[0] > second[1]
                else {True, False}
            )
        )
    return integer_operation(op, domains, threshold)


def _logic(op: Operator, domains: list[Domain]) -> Domain:
    """Compute possible Boolean results without enumerating input combinations."""
    if any(domain.unknown for domain in domains):
        return TRUE_FALSE_DOMAIN
    if any(domain.is_empty() for domain in domains):
        return EMPTY_DOMAIN
    if op == Operator.has_value:
        domain = domains[0]
        count = domain.cardinality()
        return Domain(
            bools=({False} if domain.has_none else set[bool]())
            | ({True} if count is None or count > int(domain.has_none) else set[bool]())
        )
    if op in {Operator.lnot, Operator.snot, Operator.wnot}:
        domain = domains[0]
        values = (
            set(domain.bools)
            if op == Operator.wnot
            else {not value for value in domain.bools}
        )
        if domain.has_none:
            values.add(op == Operator.wnot)
        return Domain(bools=values)
    if op == Operator.limp:
        first, second = domains
        return Domain(
            bools=(
                {True} if False in first.bools or True in second.bools else set[bool]()
            )
            | (
                {False}
                if True in first.bools and False in second.bools
                else set[bool]()
            )
        )
    if any(len(domain.bools) == 2 for domain in domains):
        return TRUE_FALSE_DOMAIN
    return Domain(
        bools=(
            (sum(True in domain.bools for domain in domains) % 2 == 1)
            if op == Operator.lxor
            else (sum(False in domain.bools for domain in domains) % 2 == 0),
        )
    )
