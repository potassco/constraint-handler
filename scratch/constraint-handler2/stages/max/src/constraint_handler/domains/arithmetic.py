"""Domain evaluation for arithmetic operators."""

from __future__ import annotations

import math
from collections.abc import Iterator
from itertools import chain, product
from typing import Literal

from ..diagnostics import ExpressionLocation
from ..python_input import Operator
from .evaluation import DomainHandler, EvaluationContext
from .values import (
    EMPTY_DOMAIN,
    UNKNOWN_DOMAIN,
    Domain,
    DomainValue,
    domain_from_values,
)

MAX_POWER_BITS = 65_536


class NumericProduct:
    """Plan numeric partitions without enumerating integer intervals."""

    def __init__(self, domains: list[Domain]) -> None:
        """Count integer-only and real-containing tuples, ignoring other values."""
        self.domains = domains
        self.int_count = math.prod(domain.int_count() for domain in domains)
        self.total_count = math.prod(domain.int_count() + len(domain.reals) for domain in domains)
        self.real_count = self.total_count - self.int_count

    def integers(self) -> Iterator[tuple[int, ...]]:
        """Yield integer-only tuples, skipping empty products before enumeration."""
        if self.int_count:
            yield from product(*(domain.iter_ints() for domain in self.domains))

    def reals(self) -> Iterator[tuple[int | float, ...]]:
        """Yield each tuple containing a real once, excluding integer-only tuples."""
        if self.real_count:
            yield from numeric_combinations(self.domains, "reals")


def numeric_combinations(
    doms: list[Domain], kind: Literal["integers", "reals", "all"]
) -> Iterator[tuple[int | float, ...]]:
    """Enumerate integer, real-containing, or all numeric products without overlap."""
    if kind == "integers":
        yield from product(*(domain.iter_ints() for domain in doms))
        return
    if kind == "all":
        yield from product(*([*domain.iter_ints(), *domain.reals] for domain in doms))
        return
    for index, domain in enumerate(doms):
        if not domain.reals:
            continue
        before, after = doms[:index], doms[index + 1 :]
        if any(item.int_count() == 0 for item in before) or any(
            item.int_count() + len(item.reals) == 0 for item in after
        ):
            continue
        pools: list[list[int | float]] = [list(item.iter_ints()) for item in before]
        pools.append(list(domain.reals))
        pools.extend([*item.iter_ints(), *item.reals] for item in after)
        yield from product(*pools)


def _is_odd_multiple_of_half_pi(val: float) -> bool:
    """Recognize exact half-pi remainders without excluding neighboring floats."""
    return abs(math.remainder(val, math.pi)) == math.pi / 2


def _safe_pow(a: float, b: float) -> int | float | None:
    """Filter undefined or complex powers, allowing numerical overflow to propagate."""
    if a == 0 and b < 0:
        return None
    if a < 0 and isinstance(b, float) and not b.is_integer():
        return None
    try:
        res = a**b
    except ZeroDivisionError, ValueError:
        return None
    if isinstance(res, complex):
        return None
    return res


def _eval_min_max(context: EvaluationContext, op: Operator, doms: list[Domain], location: ExpressionLocation) -> Domain:
    """Compute domain for Operation(Min/Max, [x1, ..., xn])."""
    if not doms:
        context.diagnostics.error(f"{op} requires at least 1 argument", location=location)
        return UNKNOWN_DOMAIN
    if any(d.unknown for d in doms):
        return UNKNOWN_DOMAIN
    if any(d.is_empty() for d in doms):
        return EMPTY_DOMAIN
    if any(d.strings or d.tuples or d.explicit_sets or d.implicit_set_elements is not None for d in doms):
        context.diagnostics.error(
            f"{op} requires numeric or boolean arguments; ignoring unsupported values",
            location=location,
        )
    cards = [d.int_count() + len(d.reals) + len(d.bools) for d in doms]
    if any(count == 0 for count in cards):
        return EMPTY_DOMAIN
    fn = min if op == Operator.min else max
    if math.prod(cards) <= context.threshold:
        vals: list[DomainValue] = []
        for combo in product(*([*d.bools, *d.iter_ints(), *d.reals] for d in doms)):
            vals.append(fn(combo))
        return domain_from_values(vals)
    if all(not d.reals and not d.bools and d.min_int() is not None for d in doms):
        lows = [d.min_int() for d in doms]
        highs = [d.max_int() for d in doms]
        int_lows = [v for v in lows if v is not None]
        int_highs = [v for v in highs if v is not None]
        return Domain(int_range=(fn(int_lows), fn(int_highs)))
    return UNKNOWN_DOMAIN


def _eval_unary_math(
    context: EvaluationContext, op: Operator, doms: list[Domain], location: ExpressionLocation
) -> Domain:
    """Compute domain for unary mathematical and conversion operators."""
    if len(doms) != 1:
        context.diagnostics.error(f"{op} expects 1 argument, got {len(doms)}", location=location)
        return UNKNOWN_DOMAIN
    dx = doms[0]
    if dx.unknown:
        return UNKNOWN_DOMAIN
    if dx.is_empty():
        return EMPTY_DOMAIN

    if op == Operator.minus:
        int_range = (-dx.int_range[1], -dx.int_range[0]) if dx.int_range is not None else None
        return Domain(
            ints=frozenset(-v for v in dx.ints),
            int_range=int_range,
            reals=frozenset(-v for v in dx.reals),
        )

    if op == Operator.abs:
        int_range = None
        if dx.int_range is not None:
            lo, hi = dx.int_range
            if lo <= 0 <= hi:
                int_range = (0, max(abs(lo), abs(hi)))
            else:
                int_range = (min(abs(lo), abs(hi)), max(abs(lo), abs(hi)))
        return Domain(
            ints=frozenset(abs(v) for v in dx.ints),
            int_range=int_range,
            reals=frozenset(abs(v) for v in dx.reals),
        )

    total_nums = dx.int_count() + len(dx.reals)
    all_nums = list(dx.iter_ints()) if dx.int_count() <= context.threshold else []
    all_nums_real: list[int | float] = [*all_nums, *dx.reals]

    match op:
        case Operator.sqrt:
            min_i = dx.min_int()
            has_neg = (min_i is not None and min_i < 0) or any(f < 0 for f in dx.reals)
            if has_neg:
                context.diagnostics.warn("sqrt domain contains negative values", location=location)
            if total_nums > context.threshold:
                return UNKNOWN_DOMAIN
            return Domain(reals=frozenset(math.sqrt(v) for v in all_nums_real if v >= 0))
        case Operator.cos:
            if total_nums > context.threshold:
                return UNKNOWN_DOMAIN
            return Domain(reals=frozenset(math.cos(v) for v in all_nums_real))
        case Operator.sin:
            if total_nums > context.threshold:
                return UNKNOWN_DOMAIN
            return Domain(reals=frozenset(math.sin(v) for v in all_nums_real))
        case Operator.tan:
            if total_nums > context.threshold:
                return UNKNOWN_DOMAIN
            reals_out: set[float] = set()
            warned_pole = False
            for v in all_nums_real:
                if _is_odd_multiple_of_half_pi(v):
                    if not warned_pole:
                        context.diagnostics.warn(
                            "tan domain contains an odd multiple of pi/2",
                            location=location,
                        )
                        warned_pole = True
                else:
                    reals_out.add(math.tan(v))
            return Domain(reals=frozenset(reals_out))
        case Operator.acos | Operator.asin:
            fn = math.acos if op == Operator.acos else math.asin
            bounds = dx.integer_bounds()
            out_of_bounds = (bounds is not None and (bounds[0] < -1 or bounds[1] > 1)) or any(
                f < -1.0 or f > 1.0 for f in dx.reals
            )
            if out_of_bounds:
                context.diagnostics.warn(
                    f"{op} domain contains values outside [-1, 1]",
                    location=location,
                )
            in_bounds_ints = [v for v in (-1, 0, 1) if dx.contains_int(v)]
            in_bounds_reals = [f for f in dx.reals if -1.0 <= f <= 1.0]
            if len(in_bounds_ints) + len(in_bounds_reals) > context.threshold:
                return UNKNOWN_DOMAIN
            return Domain(reals=frozenset(fn(v) for v in (*in_bounds_ints, *in_bounds_reals)))
        case Operator.atan:
            if total_nums > context.threshold:
                return UNKNOWN_DOMAIN
            return Domain(reals=frozenset(math.atan(v) for v in all_nums_real))
        case _:  # pragma: no cover
            return UNKNOWN_DOMAIN


def _eval_add(context: EvaluationContext, op: Operator, doms: list[Domain], location: ExpressionLocation) -> Domain:
    """Compute domain for Operation(Add, [x1, ..., xn])."""
    if not doms:
        context.diagnostics.error("add requires at least 1 argument", location=location)
        return UNKNOWN_DOMAIN
    if any(d.unknown for d in doms):
        return UNKNOWN_DOMAIN
    numeric = NumericProduct(doms)
    if numeric.real_count > context.threshold:
        return UNKNOWN_DOMAIN

    r_real: set[float] = set()
    for combo in numeric.reals():
        r_real.add(float(sum(combo)))

    if numeric.int_count == 0:
        return Domain(reals=frozenset(r_real))
    if numeric.total_count <= context.threshold:
        r_ints = frozenset(int(sum(combo)) for combo in numeric.integers())
        return Domain(ints=r_ints, reals=frozenset(r_real))

    min_sum = sum(d.min_int() or 0 for d in doms)
    max_sum = sum(d.max_int() or 0 for d in doms)
    return Domain(int_range=(min_sum, max_sum), reals=frozenset(r_real))


def _eval_sub(context: EvaluationContext, op: Operator, doms: list[Domain], location: ExpressionLocation) -> Domain:
    """Compute domain for Operation(Sub, [x, y])."""
    if len(doms) != 2:
        context.diagnostics.error(f"sub expects 2 arguments, got {len(doms)}", location=location)
        return UNKNOWN_DOMAIN
    dx, dy = doms
    if dx.unknown or dy.unknown:
        return UNKNOWN_DOMAIN
    numeric = NumericProduct(doms)
    if numeric.real_count > context.threshold:
        return UNKNOWN_DOMAIN

    r_real: set[float] = set()
    for a, b in numeric.reals():
        r_real.add(float(a - b))

    if numeric.int_count == 0:
        return Domain(reals=frozenset(r_real))
    if numeric.total_count <= context.threshold:
        r_ints = frozenset(int(a - b) for a, b in numeric.integers())
        return Domain(ints=r_ints, reals=frozenset(r_real))

    bounds_x, bounds_y = dx.integer_bounds(), dy.integer_bounds()
    assert bounds_x is not None and bounds_y is not None
    min_x, max_x = bounds_x
    min_y, max_y = bounds_y
    return Domain(
        int_range=(min_x - max_y, max_x - min_y),
        reals=frozenset(r_real),
    )


def _eval_mult(context: EvaluationContext, op: Operator, doms: list[Domain], location: ExpressionLocation) -> Domain:
    """Compute domain for Operation(Mult, [x1, ..., xn])."""
    if not doms:
        context.diagnostics.error("mult requires at least 1 argument", location=location)
        return UNKNOWN_DOMAIN
    if any(d.unknown for d in doms):
        return UNKNOWN_DOMAIN
    numeric = NumericProduct(doms)
    if numeric.real_count > context.threshold:
        return UNKNOWN_DOMAIN

    r_real: set[float] = set()
    for combo in numeric.reals():
        r_real.add(float(math.prod(combo)))

    if numeric.int_count == 0:
        return Domain(reals=frozenset(r_real))
    if numeric.total_count <= context.threshold:
        r_ints = frozenset(int(math.prod(combo)) for combo in numeric.integers())
        return Domain(ints=r_ints, reals=frozenset(r_real))

    low, high = 1, 1
    for d in doms:
        bounds = d.integer_bounds()
        assert bounds is not None
        minimum, maximum = bounds
        products = (low * minimum, low * maximum, high * minimum, high * maximum)
        low, high = min(products), max(products)
    return Domain(int_range=(low, high), reals=frozenset(r_real))


def _eval_int_div_or_mod(
    context: EvaluationContext, op: Operator, doms: list[Domain], location: ExpressionLocation
) -> Domain:
    """Compute domain for Operation(IntDiv/Mod, [x, y])."""
    if len(doms) != 2:
        context.diagnostics.error(f"{op} expects 2 arguments, got {len(doms)}", location=location)
        return UNKNOWN_DOMAIN
    dx, dy = doms
    if dx.unknown or dy.unknown:
        return UNKNOWN_DOMAIN

    has_zero_y = dy.contains_int(0) or 0.0 in dy.reals
    if has_zero_y:
        context.diagnostics.warn(f"{op} divisor domain contains 0", location=location)

    numeric = NumericProduct(doms)
    if numeric.real_count > context.threshold:
        return UNKNOWN_DOMAIN

    r_ints: set[int] = set()
    r_real: set[float] = set()
    for a, b in numeric.reals():
        if b != 0:
            if op == Operator.int_div:
                r_ints.add(int(a // b))
            else:
                r_real.add(float(a % b))

    if numeric.int_count == 0:
        return Domain(ints=frozenset(r_ints), reals=frozenset(r_real))
    if numeric.total_count <= context.threshold:
        r_ints.update((a // b if op == Operator.int_div else a % b) for a, b in numeric.integers() if b != 0)
        return Domain(ints=frozenset(r_ints), reals=frozenset(r_real))

    bounds_x = dx.integer_bounds()
    min_abs_y = dy.min_nonzero_abs_int()
    if bounds_x is None or min_abs_y is None:
        return Domain(ints=frozenset(r_ints), reals=frozenset(r_real))
    min_x, max_x = bounds_x
    if op == Operator.int_div:
        m_bound = max(abs(min_x), abs(max_x))
        bound = -(-m_bound // min_abs_y)
        return Domain(ints=frozenset(r_ints), int_range=(-bound, bound))
    max_abs_y = max(abs(dy.min_int() or 0), abs(dy.max_int() or 0))
    return Domain(
        int_range=(-(max_abs_y - 1), max_abs_y - 1),
        reals=frozenset(r_real),
    )


def _eval_real_div(
    context: EvaluationContext, op: Operator, doms: list[Domain], location: ExpressionLocation
) -> Domain:
    """Compute domain for Operation(RealDiv, [x, y])."""
    if len(doms) != 2:
        context.diagnostics.error(
            f"real_div expects 2 arguments, got {len(doms)}",
            location=location,
        )
        return UNKNOWN_DOMAIN
    dx, dy = doms
    if dx.unknown or dy.unknown:
        return UNKNOWN_DOMAIN
    if any(d.int_count() + len(d.reals) == 0 for d in doms):
        return EMPTY_DOMAIN
    has_zero_y = dy.contains_int(0) or 0.0 in dy.reals
    if has_zero_y:
        context.diagnostics.warn("real_div divisor domain contains 0", location=location)
    cx, cy = dx.cardinality(), dy.cardinality()
    if cx is None or cy is None or cx * cy > context.threshold:
        return UNKNOWN_DOMAIN
    nums_x = [*dx.iter_ints(), *dx.reals]
    nums_y = [*dy.iter_ints(), *dy.reals]
    return Domain(reals=frozenset(float(a / b) for a, b in product(nums_x, nums_y) if b != 0))


def _eval_pow(context: EvaluationContext, op: Operator, doms: list[Domain], location: ExpressionLocation) -> Domain:
    """Compute domain for Operation(Pow, [x, y])."""
    if len(doms) != 2:
        context.diagnostics.error(f"pow expects 2 arguments, got {len(doms)}", location=location)
        return UNKNOWN_DOMAIN
    dx, dy = doms
    if dx.unknown or dy.unknown:
        return UNKNOWN_DOMAIN
    if dx.is_empty() or dy.is_empty():
        return EMPTY_DOMAIN
    if dy == Domain(ints=frozenset({0})):
        return Domain(
            ints=frozenset({1}) if dx.int_count() else frozenset(),
            reals=frozenset({1.0}) if dx.reals else frozenset(),
        )
    if dy == Domain(ints=frozenset({1})):
        return dx

    base_bounds = dx.integer_bounds()
    max_exponent = dy.max_int()
    if base_bounds is not None and max_exponent is not None:
        min_base, max_base = base_bounds
        magnitude = max(abs(min_base), abs(max_base))
        if magnitude > 1 and max_exponent > (MAX_POWER_BITS - 1) // (magnitude - 1).bit_length():
            return UNKNOWN_DOMAIN

    cx, cy = dx.cardinality(), dy.cardinality()
    if cx is not None and cy is not None and cx * cy <= context.threshold:
        ints_out: set[int] = set()
        reals_out: set[float] = set()
        warned = False
        nums_x = [*dx.iter_ints(), *dx.reals]
        nums_y = [*dy.iter_ints(), *dy.reals]
        for a, b in product(nums_x, nums_y):
            val = _safe_pow(a, b)
            if val is None:
                if not warned:
                    context.diagnostics.warn(
                        "pow domain contains undefined or non-real power",
                        location=location,
                    )
                    warned = True
            elif isinstance(val, int):
                ints_out.add(val)
            else:
                reals_out.add(val)
        return Domain(ints=frozenset(ints_out), reals=frozenset(reals_out))

    nonneg_ints_y = dy.restrict_integers(0, None)
    nonneg_count = nonneg_ints_y.int_count()
    ix = dx.int_count()
    n_int = ix * nonneg_count
    assert cx is not None and cy is not None
    n_real = cx * cy - n_int
    if n_real > context.threshold:
        return UNKNOWN_DOMAIN

    r_real: set[float] = set()
    if n_real > 0:
        neg_ints_y = dy.restrict_integers(None, -1)
        integer_pairs: Iterator[tuple[int | float, ...]] = iter(())
        if ix and neg_ints_y.int_count():
            integer_pairs = numeric_combinations([Domain(ints=dx.ints, int_range=dx.int_range), neg_ints_y], "integers")
        warned = False
        for a, b in chain(NumericProduct(doms).reals(), integer_pairs):
            val = _safe_pow(a, b)
            if val is None:
                if not warned:
                    context.diagnostics.warn(
                        "pow domain contains undefined or non-real power",
                        location=location,
                    )
                    warned = True
            else:
                r_real.add(float(val))

    if n_int == 0:
        return Domain(reals=frozenset(r_real))
    if n_int + n_real <= context.threshold:
        r_ints: set[int] = set()
        for a, b in product(dx.iter_ints(), nonneg_ints_y.iter_ints()):
            val = a**b
            assert isinstance(val, int)
            r_ints.add(val)
        return Domain(ints=frozenset(r_ints), reals=frozenset(r_real))

    bounds_x = dx.integer_bounds()
    max_y = dy.max_int()
    assert bounds_x is not None and max_y is not None
    min_x, max_x = bounds_x
    a_max = max(abs(min_x), abs(max_x))
    r_bound = max(1, int(a_max**max_y))
    return Domain(int_range=(-r_bound, r_bound), reals=frozenset(r_real))


def linear_integer(
    context: EvaluationContext,
    coeffs: list[int],
    term_doms: list[Domain],
    offset: int,
    location: ExpressionLocation,
) -> Domain:
    """Evaluate an integer linear combination with exact or interval domains."""
    if any(d.unknown for d in term_doms):
        return UNKNOWN_DOMAIN
    if any(
        d.reals
        or d.bools
        or d.strings
        or d.has_none
        or d.tuples
        or d.explicit_sets
        or d.implicit_set_elements is not None
        for d in term_doms
    ):
        context.diagnostics.error("linear_integer terms must be integers", location=location)
        return UNKNOWN_DOMAIN
    if any(d.is_empty() for d in term_doms):
        return EMPTY_DOMAIN
    if not term_doms:
        return domain_from_values((offset,))

    n_total = math.prod(d.int_count() for d in term_doms)
    if n_total <= context.threshold:
        r_ints = frozenset(
            sum(c * v for c, v in zip(coeffs, combo, strict=True)) + offset
            for combo in product(*(domain.iter_ints() for domain in term_doms))
        )
        return Domain(ints=r_ints)

    low_sum = offset
    high_sum = offset
    for c, d in zip(coeffs, term_doms, strict=True):
        bounds = d.integer_bounds()
        assert bounds is not None
        mi, ma = bounds
        low_sum += min(c * mi, c * ma)
        high_sum += max(c * mi, c * ma)
    return Domain(int_range=(low_sum, high_sum))


HANDLERS: dict[Operator, DomainHandler] = {
    Operator.min: _eval_min_max,
    Operator.max: _eval_min_max,
    Operator.abs: _eval_unary_math,
    Operator.minus: _eval_unary_math,
    Operator.sqrt: _eval_unary_math,
    Operator.cos: _eval_unary_math,
    Operator.sin: _eval_unary_math,
    Operator.tan: _eval_unary_math,
    Operator.acos: _eval_unary_math,
    Operator.asin: _eval_unary_math,
    Operator.atan: _eval_unary_math,
    Operator.add: _eval_add,
    Operator.sub: _eval_sub,
    Operator.mult: _eval_mult,
    Operator.int_div: _eval_int_div_or_mod,
    Operator.mod: _eval_int_div_or_mod,
    Operator.real_div: _eval_real_div,
    Operator.pow: _eval_pow,
}
