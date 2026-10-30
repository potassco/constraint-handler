"""Table dispatch for value-based domain operator families."""

from ..diagnostics import Diagnostics, ExpressionLocation
from ..python_input import Operator
from . import (
    arithmetic,
    comparisons,
    conversions,
    logic,
    sets,
)
from .evaluation import DomainHandler, EvaluationContext
from .values import UNKNOWN_DOMAIN, Domain

DOMAIN_HANDLERS: dict[Operator, DomainHandler] = {
    **arithmetic.HANDLERS,
    **comparisons.HANDLERS,
    **conversions.HANDLERS,
    **logic.HANDLERS,
    **sets.HANDLERS,
}


class DomainOperationEvaluator:
    """Dispatch value operators to families sharing one evaluation context."""

    def __init__(
        self, diagnostics: Diagnostics, threshold: int, boolean_threshold: int
    ) -> None:
        """Retain diagnostics and enumeration limits without expression state."""
        self._context = EvaluationContext(diagnostics, threshold, boolean_threshold)

    def evaluate(
        self, op: Operator, doms: list[Domain], location: ExpressionLocation
    ) -> Domain:
        """Evaluate a value operator using its registered family handler."""
        handler = DOMAIN_HANDLERS.get(op)
        if handler is None:
            raise ValueError(f"{op} requires unevaluated expression arguments")
        if any(dom.has_nonfinite_values() for dom in doms):
            self._context.diagnostics.warn(
                f"{op} domain contains non-finite real values; returning unknown",
                location=location,
            )
            return UNKNOWN_DOMAIN
        diagnostic_count = len(self._context.diagnostics.items)
        try:
            result = handler(self._context, op, doms, location)
        except (OverflowError, ValueError, ZeroDivisionError) as error:
            self._context.diagnostics.warn(
                f"{op} domain evaluation failed: {error}; returning unknown",
                location=location,
            )
            return UNKNOWN_DOMAIN
        if result.has_nonfinite_values():
            self._context.diagnostics.warn(
                f"{op} produced non-finite real values; returning unknown",
                location=location,
            )
            return UNKNOWN_DOMAIN
        if (
            result.unknown
            and all(not dom.unknown for dom in doms)
            and op in (Operator.set_make, Operator.union, Operator.inter, Operator.diff)
            and len(self._context.diagnostics.items) == diagnostic_count
        ):
            self._context.diagnostics.warn(
                f"{op} domain cannot be represented exactly; returning unknown",
                location=location,
            )
        return result

    def linear_integer(
        self,
        coeffs: list[int],
        term_doms: list[Domain],
        offset: int,
        location: ExpressionLocation,
    ) -> Domain:
        """Evaluate a linear combination after the coordinator resolves its terms."""
        return arithmetic.linear_integer(
            self._context, coeffs, term_doms, offset, location
        )
