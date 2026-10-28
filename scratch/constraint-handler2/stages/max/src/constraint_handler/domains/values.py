"""Domain values, immutable approximations, and metadata storage."""

from __future__ import annotations

import math
from collections.abc import Collection, Iterable, Iterator, Mapping
from dataclasses import dataclass
from itertools import product
from typing import TypeIs, cast

from ..analysis import ExpressionStore
from ..internal_input import Expr

type SetValue = bool | int | float | str | None
type TupleValue = tuple[SetValue | frozenset[SetValue], ...]
type DomainValue = SetValue | frozenset[SetValue] | TupleValue
type PythonTable = tuple[tuple[tuple[DomainValue, ...], DomainValue], ...]

DEFAULT_THRESHOLD = 60000
DEFAULT_BOOLEAN_THRESHOLD = 10


@dataclass(frozen=True, slots=True, eq=False)
class Domain:
    """Represent a sound domain of values or interval/set approximations.

    Equality and hashing compare stored representations, not denotations.
    For example, an explicit integer singleton and its singleton interval
    denote the same values but compare unequal. Constructors do not canonicalize
    equivalent representations. Compound keys preserve Boolean/numeric distinctions.
    """

    bools: frozenset[bool] = frozenset()
    ints: frozenset[int] = frozenset()
    int_range: tuple[int, int] | None = None
    reals: frozenset[float] = frozenset()
    has_none: bool = False
    strings: frozenset[str] = frozenset()
    tuples: Collection[TupleValue] = ()
    explicit_sets: Collection[frozenset[SetValue]] = ()
    tuple_domains: frozenset[tuple[Domain, ...]] = frozenset()
    implicit_set_elements: frozenset[SetValue] | None = None
    unknown: bool = False

    def _identity(self) -> tuple[object, ...]:
        """Retain exact compound representations independently of language equality."""
        return (
            self.bools,
            self.ints,
            self.int_range,
            self.reals,
            self.has_none,
            self.strings,
            frozenset(representation_key(value) for value in self.tuples),
            frozenset(representation_key(value) for value in self.explicit_sets),
            self.tuple_domains,
            (
                None
                if self.implicit_set_elements is None
                else frozenset(
                    representation_key(value) for value in self.implicit_set_elements
                )
            ),
            self.unknown,
        )

    def __eq__(self, other: object) -> bool:
        """Compare representations, not denotations, preserving compound Booleans."""
        if not isinstance(other, Domain):
            return NotImplemented
        return self._identity() == other._identity()

    def __hash__(self) -> int:
        """Hash the typed representation, consistently with representation equality."""
        return hash(self._identity())

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
            and not self.tuple_domains
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

    def contains_int(self, value: int) -> bool:
        """Test membership in the stored integer components, excluding Booleans."""
        return type(value) is int and (
            value in self.ints
            or (
                self.int_range is not None
                and self.int_range[0] <= value <= self.int_range[1]
            )
        )

    def integer_bounds(self) -> tuple[int, int] | None:
        """Return inclusive bounds of the stored integers, or None if absent."""
        low, high = self.min_int(), self.max_int()
        if low is None or high is None:
            return None
        return low, high

    def restrict_integers(self, low: int | None, high: int | None) -> Domain:
        """Clip the stored integer projection; None bounds are unbounded.

        Drop all non-integer components without enumerating the interval or
        removing explicit integers that overlap it.
        """
        int_range = None
        if self.int_range is not None:
            start, stop = self.int_range
            if low is not None:
                start = max(start, low)
            if high is not None:
                stop = min(stop, high)
            if start <= stop:
                int_range = (start, stop)
        return Domain(
            ints=frozenset(
                value
                for value in self.ints
                if (low is None or low <= value) and (high is None or value <= high)
            ),
            int_range=int_range,
        )

    def min_nonzero_abs_int(self) -> int | None:
        """Return the smallest nonzero integer magnitude without enumeration."""
        candidates = [abs(value) for value in self.ints if value != 0]
        if self.int_range is not None:
            low, high = self.int_range
            if low > 0:
                candidates.append(low)
            elif high < 0:
                candidates.append(abs(high))
            elif low < 0 or high > 0:
                candidates.append(1)
        return min(candidates) if candidates else None

    def cardinality(self) -> int | None:
        """Return a value-count upper bound, or None if unknown."""
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
        for positions in self.tuple_domains:
            count = 1
            for position in positions:
                size = position.cardinality()
                if size is None:
                    return None
                count *= size
            total += count
        if self.implicit_set_elements is None:
            total += len(self.explicit_sets)
        else:
            implicit_elems = self.implicit_set_elements
            implicit_keys = {representation_key(value) for value in implicit_elems}
            extra_sets = sum(
                1
                for s in self.explicit_sets
                if not {representation_key(value) for value in s} <= implicit_keys
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
        yielded_tuples = {representation_key(value) for value in self.tuples}
        for positions in self.tuple_domains:
            for value in product(*(position.iter_values() for position in positions)):
                key = representation_key(value)
                if key not in yielded_tuples:
                    yielded_tuples.add(key)
                    yield value
        if self.implicit_set_elements is None:
            yield from self.explicit_sets
        else:
            elems = tuple(self.implicit_set_elements)
            yielded: set[object] = set()
            for bits in product((False, True), repeat=len(elems)):
                subset = frozenset(
                    e for e, include in zip(elems, bits, strict=True) if include
                )
                yielded.add(representation_key(subset))
                yield subset
            for s in self.explicit_sets:
                if representation_key(s) not in yielded:
                    yield s

    def possible_set_sizes(self) -> frozenset[int]:
        """Return sizes of explicit and implicit sets without enumerating subsets."""
        sizes = {len(value) for value in self.explicit_sets}
        if self.implicit_set_elements is not None:
            sizes.update(range(len(self.implicit_set_elements) + 1))
        return frozenset(sizes)

    def potential_set_members(self) -> frozenset[SetValue]:
        """Return all potential set elements across explicit and implicit sets."""
        members: set[SetValue] = set()
        for s in self.explicit_sets:
            members.update(s)
        if self.implicit_set_elements is not None:
            members.update(self.implicit_set_elements)
        return frozenset(members)

    def has_nonfinite_values(self) -> bool:
        """Detect non-finite reals, including inside compound values."""
        return any(
            position.has_nonfinite_values()
            for positions in self.tuple_domains
            for position in positions
        ) or any(
            not is_finite_value(value)
            for values in (
                self.reals,
                self.tuples,
                self.explicit_sets,
                self.implicit_set_elements or frozenset(),
            )
            for value in values
        )


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


def representation_key(value: DomainValue) -> object:
    """Identify exact callback values, retaining integer/real and Boolean payloads."""
    if isinstance(value, tuple):
        return (tuple, tuple(representation_key(item) for item in value))
    if isinstance(value, frozenset):
        return (frozenset, frozenset(representation_key(item) for item in value))
    return (type(value), repr(value))


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
    """Recognize scalar members of flat sets."""
    return value is None or type(value) in (bool, int, float, str)


def is_domain_value(value: object) -> TypeIs[DomainValue]:
    """Recognize supported values without silently discarding Python results."""
    return (
        _is_set_value(value)
        or (
            isinstance(value, frozenset)
            and all(_is_set_value(item) for item in cast(frozenset[object], value))
        )
        or (
            isinstance(value, tuple)
            and all(
                _is_set_value(item)
                or isinstance(item, frozenset)
                and all(_is_set_value(member) for member in item)
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


class DomainStore(ExpressionStore[Domain]):
    """Own domains and validated Python tables for one set of context bindings."""

    def __init__(
        self,
        expressions: Mapping[Expr, Domain] | Iterable[tuple[Expr, Domain]] = (),
        *,
        python_context: Mapping[str, object] | None = None,
    ) -> None:
        """Keep table caches local to the domain computation and its context."""
        super().__init__(expressions)
        self.python_context = dict(python_context or {})
        self.python_tables: dict[tuple[str, tuple[Domain, ...]], PythonTable] = {}


def domain_from_values(values: Iterable[DomainValue]) -> Domain:
    """Construct an exact domain, retaining representation-distinct alternatives.

    Unlike join_domains, this builder never fills integer gaps, merges powerset
    universes, or widens at a threshold. It stores supplied values explicitly.
    """
    bools: set[bool] = set()
    ints: set[int] = set()
    reals: set[float] = set()
    has_none = False
    strings: set[str] = set()
    tuples: dict[object, TupleValue] = {}
    explicit_sets: dict[object, frozenset[SetValue]] = {}
    for val in values:
        if not is_domain_value(val):
            return UNKNOWN_DOMAIN
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
                tuples[representation_key(val)] = val
            case frozenset():
                explicit_sets[representation_key(val)] = val
    return Domain(
        bools=frozenset(bools),
        ints=frozenset(ints),
        reals=frozenset(reals),
        has_none=has_none,
        strings=frozenset(strings),
        tuples=tuple(tuples.values()),
        explicit_sets=tuple(explicit_sets.values()),
    )


def join_domains(
    domains: Iterable[Domain], threshold: int = DEFAULT_THRESHOLD
) -> Domain:
    """Return a sound approximation containing every input domain's values.

    This is neither exact runtime set union nor necessarily a least upper bound
    in the full representation space. Existing integer intervals and explicit
    integers are enclosed by one interval, filling gaps even below threshold.
    Implicit set universes are merged into a powerset that can admit sets mixing
    members from different inputs. Explicit sets outside that powerset remain.

    Above threshold, explicit integers widen to their enclosing interval and
    explicit reals widen to unknown. Unknown inputs and Boolean/numeric implicit
    member collisions also yield unknown. Exact alternatives retain their types.
    """
    bools: set[bool] = set()
    ints: set[int] = set()
    int_ranges: list[tuple[int, int]] = []
    reals: set[float] = set()
    has_none = False
    strings: set[str] = set()
    tuple_domains: set[tuple[Domain, ...]] = set()
    explicit_sets: list[frozenset[SetValue]] = []
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
        tuple_domains.update(dom.tuple_domains)
        explicit_sets.extend(dom.explicit_sets)
        if dom.implicit_set_elements is not None:
            member_values.extend(dom.implicit_set_elements)
            if implicit_elems is None:
                implicit_elems = set(dom.implicit_set_elements)
            else:
                implicit_elems.update(dom.implicit_set_elements)

    if has_value_collisions(member_values):
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
        implicit_keys = {representation_key(value) for value in final_implicit}
        explicit_sets = [
            s
            for s in explicit_sets
            if not {representation_key(value) for value in s} <= implicit_keys
        ]

    compounds = domain_from_values(
        value for value in compound_values if isinstance(value, tuple)
    )
    sets = domain_from_values(explicit_sets)

    return Domain(
        bools=frozenset(bools),
        ints=frozenset(ints),
        int_range=merged_range,
        reals=frozenset(reals),
        has_none=has_none,
        strings=frozenset(strings),
        tuples=compounds.tuples,
        tuple_domains=frozenset(tuple_domains),
        explicit_sets=sets.explicit_sets,
        implicit_set_elements=final_implicit,
    )
