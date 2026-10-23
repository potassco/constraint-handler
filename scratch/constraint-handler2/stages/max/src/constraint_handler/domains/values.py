"""Domain values, immutable approximations, and metadata storage."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass
from itertools import product
from typing import TypeIs, cast

from ..internal_input import Expr, VariableRef

type SetValue = bool | int | float | str | None | tuple[SetValue, ...]
type DomainValue = SetValue | frozenset[SetValue]

DEFAULT_THRESHOLD = 1000
DEFAULT_BOOLEAN_THRESHOLD = 10


@dataclass(frozen=True, slots=True)
class Domain:
    """Represent a sound domain of values or interval/set approximations."""

    bools: frozenset[bool] = frozenset()
    ints: frozenset[int] = frozenset()
    int_range: tuple[int, int] | None = None
    reals: frozenset[float] = frozenset()
    has_none: bool = False
    strings: frozenset[str] = frozenset()
    tuples: frozenset[tuple[SetValue, ...]] = frozenset()
    explicit_sets: frozenset[frozenset[SetValue]] = frozenset()
    implicit_set_elements: frozenset[SetValue] | None = None
    unknown: bool = False

    def is_empty(self) -> bool:
        """Return True if the domain is known and contains no values."""
        if self.unknown:
            return False
        return (
            not self.bools
            and not self.ints
            and self.int_range is None
            and not self.reals
            and not self.has_none
            and not self.strings
            and not self.tuples
            and not self.explicit_sets
            and self.implicit_set_elements is None
        )

    def int_count(self) -> int:
        """Return the number of distinct integers in ints union int_range."""
        if self.int_range is None:
            return len(self.ints)
        low, high = self.int_range
        range_size = max(0, high - low + 1)
        extra = sum(1 for v in self.ints if v < low or v > high)
        return range_size + extra

    def iter_ints(self) -> Iterator[int]:
        """Yield each distinct integer in ints union int_range."""
        if self.int_range is None:
            yield from self.ints
            return
        low, high = self.int_range
        for v in self.ints:
            if v < low or v > high:
                yield v
        yield from range(low, high + 1)

    def min_int(self) -> int | None:
        """Return the minimum integer in the domain, or None if none exist."""
        candidates: list[int] = []
        if self.ints:
            candidates.append(min(self.ints))
        if self.int_range is not None:
            candidates.append(self.int_range[0])
        return min(candidates) if candidates else None

    def max_int(self) -> int | None:
        """Return the maximum integer in the domain, or None if none exist."""
        candidates: list[int] = []
        if self.ints:
            candidates.append(max(self.ints))
        if self.int_range is not None:
            candidates.append(self.int_range[1])
        return max(candidates) if candidates else None

    def cardinality(self) -> int | None:
        """Return the number of distinct values in the domain, or None if unknown."""
        if self.unknown:
            return None
        total = (
            len(self.bools)
            + self.int_count()
            + len(self.reals)
            + (1 if self.has_none else 0)
            + len(self.strings)
            + len(self.tuples)
        )
        if self.implicit_set_elements is None:
            total += len(self.explicit_sets)
        else:
            implicit_elems = self.implicit_set_elements
            implicit_keys = {value_key(value) for value in implicit_elems}
            extra_sets = sum(
                1
                for s in self.explicit_sets
                if not {value_key(value) for value in s} <= implicit_keys
            )
            total += (1 << len(implicit_elems)) + extra_sets
        return total

    def iter_values(self) -> Iterator[DomainValue]:
        """Yield all distinct values in a known domain."""
        yield from self.bools
        yield from self.iter_ints()
        yield from self.reals
        if self.has_none:
            yield None
        yield from self.strings
        yield from self.tuples
        if self.implicit_set_elements is None:
            yield from self.explicit_sets
        else:
            elems = tuple(self.implicit_set_elements)
            yielded: set[object] = set()
            for bits in product((False, True), repeat=len(elems)):
                subset = frozenset(
                    e for e, include in zip(elems, bits, strict=True) if include
                )
                yielded.add(value_key(subset))
                yield subset
            for s in self.explicit_sets:
                if value_key(s) not in yielded:
                    yield s

    def potential_set_members(self) -> frozenset[SetValue]:
        """Return all potential set elements across explicit and implicit sets."""
        members: set[SetValue] = set()
        for s in self.explicit_sets:
            members.update(s)
        if self.implicit_set_elements is not None:
            members.update(self.implicit_set_elements)
        return frozenset(members)


UNKNOWN_DOMAIN = Domain(unknown=True)
EMPTY_DOMAIN = Domain()
TRUE_FALSE_DOMAIN = Domain(bools=frozenset({False, True}))


def value_key(value: DomainValue) -> object:
    """Key values recursively, separating Booleans from numeric values."""
    if isinstance(value, bool):
        return (bool, value)
    if isinstance(value, (int, float)):
        return (int, value)
    if isinstance(value, tuple):
        return (tuple, tuple(value_key(item) for item in value))
    if isinstance(value, frozenset):
        return (frozenset, frozenset(value_key(item) for item in value))
    return (type(value), value)


def has_value_collisions(values: Iterable[DomainValue]) -> bool:
    """Detect distinct language values that Python hashed collections conflate."""
    keys: dict[DomainValue, object] = {}
    for value in values:
        key = value_key(value)
        if value in keys and keys[value] != key:
            return True
        keys[value] = key
    return False


def _is_set_value(value: object) -> TypeIs[SetValue]:
    """Recognize supported scalars and recursively supported tuple members."""
    if value is None or type(value) in (bool, int, float, str):
        return True
    return isinstance(value, tuple) and all(
        _is_set_value(item) for item in cast(tuple[object, ...], value)
    )


def is_domain_value(value: object) -> TypeIs[DomainValue]:
    """Recognize supported values without silently discarding Python results."""
    return _is_set_value(value) or (
        isinstance(value, frozenset)
        and all(_is_set_value(item) for item in cast(frozenset[object], value))
    )


class DomainStore(dict[Expr, Domain]):
    """Map expressions, including variables, to their precomputed domains."""

    def __init__(
        self, expressions: Mapping[Expr, Domain] | Iterable[tuple[Expr, Domain]] = ()
    ) -> None:
        """Initialize expression metadata and a separate lambda-context mapping."""
        super().__init__(expressions)
        self.scoped_expressions: dict[
            tuple[Expr, frozenset[tuple[VariableRef, Domain]]], Domain
        ] = {}

    def lookup(
        self,
        expr: Expr,
        *,
        scope: frozenset[tuple[VariableRef, Domain]] = frozenset(),
    ) -> Domain:
        """Look up an expression in its explicit lambda binding environment."""
        return self.scoped_expressions[expr, scope] if scope else self[expr]


def domain_from_values(values: Iterable[DomainValue]) -> Domain:
    """Construct an exact domain, or unknown if compound values would collapse."""
    bools: set[bool] = set()
    ints: set[int] = set()
    reals: set[float] = set()
    has_none = False
    strings: set[str] = set()
    tuples: set[tuple[SetValue, ...]] = set()
    explicit_sets: set[frozenset[SetValue]] = set()
    compound_keys: dict[DomainValue, object] = {}
    for val in values:
        if isinstance(val, (tuple, frozenset)):
            key = value_key(val)
            if val in compound_keys and compound_keys[val] != key:
                return UNKNOWN_DOMAIN
            compound_keys[val] = key
        match val:
            case bool():
                bools.add(val)
            case int():
                ints.add(val)
            case float():
                reals.add(val)
            case None:
                has_none = True
            case str():
                strings.add(val)
            case tuple():
                tuples.add(val)
            case frozenset():
                explicit_sets.add(val)
    return Domain(
        bools=frozenset(bools),
        ints=frozenset(ints),
        reals=frozenset(reals),
        has_none=has_none,
        strings=frozenset(strings),
        tuples=frozenset(tuples),
        explicit_sets=frozenset(explicit_sets),
    )


def union_domains(
    domains: Iterable[Domain], threshold: int = DEFAULT_THRESHOLD
) -> Domain:
    """Combine multiple domains into a single sound Domain."""
    bools: set[bool] = set()
    ints: set[int] = set()
    int_ranges: list[tuple[int, int]] = []
    reals: set[float] = set()
    has_none = False
    strings: set[str] = set()
    tuples: set[tuple[SetValue, ...]] = set()
    explicit_sets: set[frozenset[SetValue]] = set()
    implicit_elems: set[SetValue] | None = None
    compound_values: list[DomainValue] = []
    member_values: list[SetValue] = []

    for dom in domains:
        if dom.unknown:
            return UNKNOWN_DOMAIN
        bools.update(dom.bools)
        ints.update(dom.ints)
        if dom.int_range is not None:
            int_ranges.append(dom.int_range)
        reals.update(dom.reals)
        has_none = has_none or dom.has_none
        strings.update(dom.strings)
        compound_values.extend(dom.tuples)
        compound_values.extend(dom.explicit_sets)
        tuples.update(dom.tuples)
        explicit_sets.update(dom.explicit_sets)
        if dom.implicit_set_elements is not None:
            member_values.extend(dom.implicit_set_elements)
            if implicit_elems is None:
                implicit_elems = set(dom.implicit_set_elements)
            else:
                implicit_elems.update(dom.implicit_set_elements)

    if has_value_collisions(compound_values) or has_value_collisions(member_values):
        return UNKNOWN_DOMAIN

    merged_range: tuple[int, int] | None = None
    if int_ranges:
        low = min(r[0] for r in int_ranges)
        high = max(r[1] for r in int_ranges)
        if ints:
            low = min(low, min(ints))
            high = max(high, max(ints))
            ints.clear()
        merged_range = (low, high)
    elif len(ints) > threshold:
        merged_range = (min(ints), max(ints))
        ints.clear()

    if len(reals) > threshold:
        return UNKNOWN_DOMAIN

    final_implicit = frozenset(implicit_elems) if implicit_elems is not None else None
    if final_implicit is not None:
        implicit_keys = {value_key(value) for value in final_implicit}
        explicit_sets = {
            s
            for s in explicit_sets
            if not {value_key(value) for value in s} <= implicit_keys
        }

    return Domain(
        bools=frozenset(bools),
        ints=frozenset(ints),
        int_range=merged_range,
        reals=frozenset(reals),
        has_none=has_none,
        strings=frozenset(strings),
        tuples=frozenset(tuples),
        explicit_sets=frozenset(explicit_sets),
        implicit_set_elements=final_implicit,
    )
