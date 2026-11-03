"""Compute integer domains using intervals, sometimes including extra possible values."""

from itertools import product
from math import prod

from ..python_input import Operator
from ._domain import EMPTY_DOMAIN, UNKNOWN_DOMAIN, Domain, _Range

_MAX_POWER_BITS = 65_536


def integer_operation(
    op: Operator, domains: list[Domain], threshold: int
) -> Domain | None:
    """Compute an approximate integer domain, or return None to request table evaluation."""
    if op not in {
        Operator.abs,
        Operator.minus,
        Operator.add,
        Operator.sub,
        Operator.mult,
        Operator.int_div,
        Operator.mod,
        Operator.pow,
        Operator.min,
        Operator.max,
        Operator.floor,
        Operator.ceil,
    }:
        return None
    if any(domain.unknown for domain in domains):
        return UNKNOWN_DOMAIN
    if any(domain.is_empty() for domain in domains):
        return EMPTY_DOMAIN
    first = domains[0]
    if op in {Operator.floor, Operator.ceil}:
        return first
    if op == Operator.minus:
        return Domain(
            integers=_Range(
                (-upper, -lower) for lower, upper in first.integers.intervals
            )
        )
    if op == Operator.abs:
        return Domain(
            integers=_Range(
                (0, max(-lower, upper))
                if lower <= 0 <= upper
                else (min(abs(lower), abs(upper)), max(abs(lower), abs(upper)))
                for lower, upper in first.integers.intervals
            )
        )
    if op in {Operator.min, Operator.max}:
        bounds = [domain.integer_bounds() for domain in domains]
        known = [bound for bound in bounds if bound is not None]
        if len(known) != len(domains):
            return EMPTY_DOMAIN
        limit = (
            min(upper for _, upper in known)
            if op == Operator.min
            else max(lower for lower, _ in known)
        )
        return Domain(
            integers=_Range(
                (lower, min(upper, limit))
                if op == Operator.min
                else (max(lower, limit), upper)
                for domain in domains
                for lower, upper in domain.integers.intervals
                if (lower <= limit if op == Operator.min else upper >= limit)
            )
        )
    second = domains[1]
    if op in {Operator.add, Operator.sub}:
        return Domain(
            integers=_Range(
                (left_lower + right_lower, left_upper + right_upper)
                if op == Operator.add
                else (left_lower - right_upper, left_upper - right_lower)
                for (left_lower, left_upper), (right_lower, right_upper) in product(
                    first.integers.intervals, second.integers.intervals
                )
            )
        )
    if op == Operator.pow:
        first_bounds, second_bounds = first.integer_bounds(), second.integer_bounds()
        assert first_bounds is not None and second_bounds is not None
        magnitude = max(abs(value) for value in first_bounds)
        exponent = second_bounds[1]
        if (
            magnitude > 1
            and exponent > (_MAX_POWER_BITS - 1) // (magnitude - 1).bit_length()
        ):
            return UNKNOWN_DOMAIN
        if second_bounds[0] < 0:
            return None
    if prod(domain.int_count() for domain in domains) <= threshold:
        return None
    if op == Operator.mult:
        intervals: list[tuple[int, int]] = []
        for left, right in product(first.integers.intervals, second.integers.intervals):
            endpoints = [a * b for a, b in product(left, right)]
            intervals.append((min(endpoints), max(endpoints)))
        return Domain(integers=_Range(intervals))
    if op in {Operator.int_div, Operator.mod}:
        divisor = second.min_nonzero_abs_int()
        if divisor is None:
            return EMPTY_DOMAIN
        if op == Operator.int_div:
            bounds = first.integer_bounds()
            assert bounds is not None
            magnitude = max(abs(value) for value in bounds)
            bound = (magnitude + divisor - 1) // divisor
        else:
            bounds = second.integer_bounds()
            assert bounds is not None
            bound = max(abs(value) for value in bounds) - 1
        return Domain(int_range=(-bound, bound))
    bounds = first.integer_bounds()
    exponent = second.max_int()
    assert bounds is not None and exponent is not None
    bound = max(1, max(abs(value) for value in bounds) ** exponent)
    return Domain(int_range=(-bound, bound))


def linear_integer(
    coefficients: list[int], domains: list[Domain], offset: int
) -> Domain:
    """Compute a linear expression's approximate domain using interval arithmetic."""
    if any(domain.unknown for domain in domains):
        return UNKNOWN_DOMAIN
    if any(domain.is_empty() for domain in domains):
        return EMPTY_DOMAIN
    result = Domain(ints=(offset,))
    for coefficient, domain in zip(coefficients, domains, strict=True):
        scaled = Domain(
            integers=_Range(
                (
                    min(coefficient * lower, coefficient * upper),
                    max(coefficient * lower, coefficient * upper),
                )
                for lower, upper in domain.integers.intervals
            )
        )
        combined = integer_operation(Operator.add, [result, scaled], 0)
        assert combined is not None
        result = combined
    return result
