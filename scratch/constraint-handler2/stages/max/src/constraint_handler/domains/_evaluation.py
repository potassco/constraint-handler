"""Check whether input combinations fit the table-evaluation limit."""

from collections.abc import Sequence
from enum import Enum, auto

from ._domain import Domain


class EnumerationDecision(Enum):
    """Classify input combinations without enumerating them.

    EXCESSIVE describes an ExcessiveDomain: the input domains have more
    combinations than the table limit permits. This is not a new domain value.
    """

    UNKNOWN = auto()
    EMPTY = auto()
    EXCESSIVE = auto()
    ENUMERABLE = auto()


def bounded_product_decision(
    domains: Sequence[Domain], threshold: int
) -> EnumerationDecision:
    """Count input combinations before enumeration; a call without inputs has one.

    Unknown counts take precedence over empty inputs. Known counts above the
    limit produce EXCESSIVE, rather than an empty or unknown domain.
    """
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
