"""Immutable approximate domains, integer intervals, and supported result values."""

from __future__ import annotations

import math
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from itertools import product
from typing import TypeIs, cast

from ..python_conversion import value_key

__all__ = ["_Range"]

type SetValue = bool | int | float | str | None
type TupleValue = tuple[SetValue | frozenset[SetValue], ...]
type DomainValue = SetValue | frozenset[SetValue] | TupleValue
type PythonTable = tuple[tuple[tuple[DomainValue, ...], DomainValue], ...]

DEFAULT_THRESHOLD = 60000
DEFAULT_BOOLEAN_THRESHOLD = 10


@dataclass(frozen=True, slots=True, init=False)
class _Range:
    """Store integers as normalized, disjoint inclusive intervals."""

    intervals: tuple[tuple[int, int], ...]

    def __init__(self, intervals: Iterable[tuple[int, int]] = ()) -> None:
        """Sort and merge intervals, rejecting reversed or noninteger endpoints."""
        pending = tuple(intervals)
        for lower, upper in pending:
            if type(lower) is not int or type(upper) is not int:
                raise TypeError("Integer interval endpoints must be integers")
            if lower > upper:
                raise ValueError(
                    "Integer interval lower endpoint exceeds upper endpoint"
                )
        normalized: list[tuple[int, int]] = []
        for lower, upper in sorted(pending):
            if normalized and lower <= normalized[-1][1] + 1:
                normalized[-1] = (normalized[-1][0], max(normalized[-1][1], upper))
            else:
                normalized.append((lower, upper))
        object.__setattr__(self, "intervals", tuple(normalized))

    def __contains__(self, value: object) -> bool:
        """Test integer membership without admitting Booleans or real values."""
        if type(value) is not int:
            return False
        for lower, upper in self.intervals:
            if value < lower:
                return False
            if value <= upper:
                return True
        return False

    def union(self, other: _Range) -> _Range:
        """Combine integer intervals without filling gaps or enumerating values."""
        return _Range((*self.intervals, *other.intervals))

    def intersection(self, other: _Range) -> _Range:
        """Intersect interval sequences without enumerating their integers."""
        intersections: list[tuple[int, int]] = []
        left_index = right_index = 0
        while left_index < len(self.intervals) and right_index < len(other.intervals):
            left_lower, left_upper = self.intervals[left_index]
            right_lower, right_upper = other.intervals[right_index]
            lower, upper = max(left_lower, right_lower), min(left_upper, right_upper)
            if lower <= upper:
                intersections.append((lower, upper))
            if left_upper < right_upper:
                left_index += 1
            else:
                right_index += 1
        return _Range(intersections)

    def bounds(self) -> tuple[int, int] | None:
        """Return inclusive outer bounds, or None when no integers are stored."""
        if not self.intervals:
            return None
        return self.intervals[0][0], self.intervals[-1][1]

    def cardinality(self) -> int:
        """Count integers exactly using interval lengths rather than enumeration."""
        return sum(upper - lower + 1 for lower, upper in self.intervals)


@dataclass(frozen=True, slots=True, eq=False, init=False)
class Domain:
    """Describe possible values, including approximations that admit extra results.

    Integers use intervals, floats remain individual values, and tuples keep a
    domain per position. A set base lists possible members and admits every
    subset; it does not say which members must occur together.
    """

    bools: frozenset[bool]
    integers: _Range
    reals: tuple[float, ...]
    has_none: bool
    strings: frozenset[str]
    tuple_domains: frozenset[tuple[Domain, ...]]
    set_base: Domain | None
    unknown: bool

    def __init__(
        self,
        *,
        bools: Iterable[bool] = (),
        integers: _Range | None = None,
        reals: Iterable[float] = (),
        has_none: bool = False,
        strings: Iterable[str] = (),
        tuple_domains: Iterable[tuple[Domain, ...]] = (),
        set_base: Domain | None = None,
        unknown: bool = False,
        ints: Iterable[int] = (),
        int_range: tuple[int, int] | None = None,
    ) -> None:
        """Merge integer intervals and copy inputs into immutable domain components."""
        intervals = (
            *(integers.intervals if integers is not None else ()),
            *((value, value) for value in ints),
        )
        if int_range is not None:
            intervals = (*intervals, int_range)
        positions = set(tuple_domains)
        base = set_base
        if base is not None and (base.set_base is not None or base.tuple_domains):
            raise ValueError("Set bases contain scalars only")
        if any(position.tuple_domains for shape in positions for position in shape):
            raise ValueError("Tuple positions cannot contain tuples")
        object.__setattr__(self, "bools", frozenset(bools))
        object.__setattr__(self, "integers", _Range(intervals))
        object.__setattr__(
            self,
            "reals",
            tuple(sorted({repr(value): value for value in reals}.values(), key=repr)),
        )
        object.__setattr__(self, "has_none", has_none)
        object.__setattr__(self, "strings", frozenset(strings))
        object.__setattr__(self, "tuple_domains", frozenset(positions))
        object.__setattr__(self, "set_base", base)
        object.__setattr__(self, "unknown", unknown)

    def _identity(self) -> tuple[object, ...]:
        """Build a cache key that preserves stored types and float representations."""
        return (
            self.bools,
            self.integers,
            tuple(repr(value) for value in self.reals),
            self.has_none,
            self.strings,
            self.tuple_domains,
            self.set_base,
            self.unknown,
        )

    def _order_key(self) -> tuple[object, ...]:
        """Build a sort key that ignores frozenset iteration order."""
        base = self.set_base
        return (
            tuple(sorted(self.bools)),
            self.integers.intervals,
            tuple(repr(value) for value in self.reals),
            self.has_none,
            tuple(sorted(self.strings)),
            tuple(
                sorted(
                    tuple(position._order_key() for position in shape)
                    for shape in self.tuple_domains
                )
            ),
            () if base is None else (base._order_key(),),
            self.unknown,
        )

    def __eq__(self, other: object) -> bool:
        """Compare stored components, keeping Booleans, integers, and floats distinct."""
        if not isinstance(other, Domain):
            return NotImplemented
        return self._identity() == other._identity()

    def __hash__(self) -> int:
        """Hash the same components used for domain equality."""
        return hash(self._identity())

    def is_empty(self) -> bool:
        """Return True if the domain is known and contains no values."""
        if self.unknown:
            return False
        return (
            not self.bools
            and not self.integers.intervals
            and not self.reals
            and not self.has_none
            and not self.strings
            and not self.tuple_domains
            and self.set_base is None
        )

    def int_count(self) -> int:
        """Count integers without expanding intervals."""
        return self.integers.cardinality()

    def iter_ints(self) -> Iterator[int]:
        """Yield individual integers; the caller must check the enumeration limit first."""
        for lower, upper in self.integers.intervals:
            yield from range(lower, upper + 1)

    def max_int(self) -> int | None:
        """Return the maximum integer in the domain, or None if none exist."""
        return self.integers.intervals[-1][1] if self.integers.intervals else None

    def contains_int(self, value: int) -> bool:
        """Test membership in the stored integer components, excluding Booleans."""
        return value in self.integers

    def integer_bounds(self) -> tuple[int, int] | None:
        """Return inclusive bounds of the stored integers, or None if absent."""
        return self.integers.bounds()

    def min_nonzero_abs_int(self) -> int | None:
        """Return the smallest nonzero integer magnitude without enumeration."""
        candidates: list[int] = []
        for low, high in self.integers.intervals:
            if low > 0:
                candidates.append(low)
            elif high < 0:
                candidates.append(abs(high))
            elif low < 0 or high > 0:
                candidates.append(1)
        return min(candidates) if candidates else None

    def cardinality(self) -> int | None:
        """Count admitted values, possibly overestimating; return None if unavailable."""
        if self.unknown:
            return None
        total = (
            len(self.bools)
            + self.int_count()
            + len(self.reals)
            + (1 if self.has_none else 0)
            + len(self.strings)
        )
        for positions in self.tuple_domains:
            count = 1
            for position in positions:
                size = position.cardinality()
                if size is None:
                    return None
                count *= size
            total += count
        if self.set_base is not None:
            size = self.set_base.cardinality()
            if size is None:
                return None
            if size > DEFAULT_THRESHOLD:
                return None
            total += 1 << size
        return total

    def iter_values(self) -> Iterator[DomainValue]:
        """Yield all distinct values in a known domain."""
        yield from self.bools
        yield from self.iter_ints()
        yield from self.reals
        if self.has_none:
            yield None
        yield from sorted(self.strings)
        yielded_tuples: set[object] = set()
        shapes = sorted(
            self.tuple_domains,
            key=lambda shape: tuple(position._order_key() for position in shape),
        )
        for positions in shapes:
            for value in cast(
                Iterator[TupleValue],
                product(*(position.iter_values() for position in positions)),
            ):
                key = representation_key(value)
                if key not in yielded_tuples:
                    yielded_tuples.add(key)
                    yield value
        if self.set_base is not None:
            if self.set_base.unknown:
                raise ValueError("Cannot enumerate an unknown set member base")
            elems = tuple(cast(Iterable[SetValue], self.set_base.iter_values()))
            if has_value_collisions(elems):
                raise ValueError(
                    "Python sets cannot represent distinct Boolean/numeric members"
                )
            for bits in product((False, True), repeat=len(elems)):
                yield frozenset(
                    e for e, include in zip(elems, bits, strict=True) if include
                )

    def has_nonfinite_values(self) -> bool:
        """Detect non-finite reals, including inside compound values."""
        return (
            any(
                position.has_nonfinite_values()
                for positions in self.tuple_domains
                for position in positions
            )
            or any(not math.isfinite(value) for value in self.reals)
            or (self.set_base is not None and self.set_base.has_nonfinite_values())
        )


UNKNOWN_DOMAIN = Domain(unknown=True)
EMPTY_DOMAIN = Domain()
TRUE_FALSE_DOMAIN = Domain(bools=frozenset({False, True}))


def representation_key(value: DomainValue) -> object:
    """Distinguish callback inputs by type and representation, including signed zero."""
    if isinstance(value, tuple):
        return (tuple, tuple(representation_key(item) for item in value))
    if isinstance(value, frozenset):
        return (frozenset, frozenset(representation_key(item) for item in value))
    return (type(value), repr(value))


def has_value_collisions(values: Iterable[DomainValue]) -> bool:
    """Detect distinct values, such as True and 1, that Python sets would merge."""
    keys: dict[DomainValue, object] = {}
    for value in values:
        key = value_key(value)
        if value in keys and keys[value] != key:
            return True
        keys[value] = key
    return False


def is_set_value(value: object) -> TypeIs[SetValue]:
    """Recognize scalar members of flat sets."""
    return value is None or type(value) in (bool, int, float, str)


def is_domain_value(value: object) -> TypeIs[DomainValue]:
    """Recognize supported values without silently discarding Python results."""
    return (
        is_set_value(value)
        or (
            isinstance(value, frozenset)
            and all(is_set_value(item) for item in cast(frozenset[object], value))
        )
        or (
            isinstance(value, tuple)
            and all(
                is_set_value(item)
                or isinstance(item, frozenset)
                and all(
                    is_set_value(member) for member in cast(frozenset[object], item)
                )
                for item in cast(tuple[object, ...], value)
            )
        )
    )


def is_finite_value(value: DomainValue) -> bool:
    """Reject non-finite floats recursively without converting large integers."""
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, (tuple, frozenset)):
        return all(is_finite_value(item) for item in value)
    return True


def domain_from_values(values: Iterable[DomainValue]) -> Domain:
    """Build an approximate domain from values, merging set members into one base."""
    bools: set[bool] = set()
    ints: set[int] = set()
    reals: dict[str, float] = {}
    has_none = False
    strings: set[str] = set()
    tuples: set[tuple[Domain, ...]] = set()
    bases: list[Domain] = []
    for val in values:
        if not is_domain_value(val):
            return UNKNOWN_DOMAIN
        match val:
            case bool():
                bools.add(val)
            case int():
                ints.add(val)
            case float():
                reals[repr(val)] = val
            case None:
                has_none = True
            case str():
                strings.add(val)
            case tuple():
                tuples.add(tuple(domain_from_values((item,)) for item in val))
            case frozenset():
                bases.append(domain_from_values(val))
    return Domain(
        bools=frozenset(bools),
        ints=frozenset(ints),
        reals=reals.values(),
        has_none=has_none,
        strings=frozenset(strings),
        tuple_domains=tuples,
        set_base=join_domains(bases) if bases else None,
    )


def join_domains(domains: Iterable[Domain]) -> Domain:
    """Combine domains without filling integer gaps or replacing individual floats.

    Set bases combine possible members, not exact sets or required members.
    Enumeration limits do not restrict combining values already known.
    """
    bools: set[bool] = set()
    intervals: list[tuple[int, int]] = []
    reals: dict[str, float] = {}
    has_none = False
    strings: set[str] = set()
    tuple_domains: set[tuple[Domain, ...]] = set()
    bases: list[Domain] = []
    for dom in domains:
        if dom.unknown:
            return UNKNOWN_DOMAIN
        bools.update(dom.bools)
        intervals.extend(dom.integers.intervals)
        reals.update((repr(value), value) for value in dom.reals)
        has_none = has_none or dom.has_none
        strings.update(dom.strings)
        tuple_domains.update(dom.tuple_domains)
        if dom.set_base is not None:
            bases.append(dom.set_base)
    base = join_domains(bases) if bases else None
    return Domain(
        bools=bools,
        integers=_Range(intervals),
        reals=reals.values(),
        has_none=has_none,
        strings=strings,
        tuple_domains=tuple_domains,
        set_base=base,
    )
