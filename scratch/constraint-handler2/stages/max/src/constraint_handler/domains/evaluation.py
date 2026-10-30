"""Shared context and callable contract for value-based domain evaluators."""

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import Enum, auto

from ..diagnostics import Diagnostics, ExpressionLocation
from ..python_input import Operator
from .values import Domain


class EnumerationDecision(Enum):
    """Distinguish whole-domain Cartesian products before materializing axes."""

    UNKNOWN = auto()
    EMPTY = auto()
    EXCESSIVE = auto()
    ENUMERABLE = auto()


def bounded_product_decision(
    domains: Sequence[Domain], threshold: int
) -> EnumerationDecision:
    """Check whole-domain counts, with unknown before empty and nullary size one."""
    counts = [domain.cardinality() for domain in domains]
    if any(count is None for count in counts):
        return EnumerationDecision.UNKNOWN
    if 0 in counts:
        return EnumerationDecision.EMPTY
    size = 1
    for count in counts:
        assert count is not None
        size *= count
        if size > threshold:
            return EnumerationDecision.EXCESSIVE
    if size > threshold:
        return EnumerationDecision.EXCESSIVE
    return EnumerationDecision.ENUMERABLE


@dataclass(frozen=True, slots=True)
class EvaluationContext:
    """Share diagnostics and size limits without mutable expression state."""

    diagnostics: Diagnostics
    threshold: int
    boolean_threshold: int


type DomainHandler = Callable[
    [EvaluationContext, Operator, list[Domain], ExpressionLocation], Domain
]
