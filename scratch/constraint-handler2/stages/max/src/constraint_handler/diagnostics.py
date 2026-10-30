"""Diagnostics collection for preprocessing passes."""

from dataclasses import dataclass, field
from enum import StrEnum, auto

from .internal_input import Expr, ExprId, VariableRef


class DiagnosticSeverity(StrEnum):
    """Distinguish non-fatal warnings from analysis errors."""

    warning = auto()
    error = auto()


@dataclass(frozen=True, slots=True)
class ExpressionLocation:
    """Pair a stored root ID with the relevant analysis-time expression node."""

    root_id: ExprId
    expression: Expr


@dataclass(frozen=True, slots=True)
class Diagnostic:
    """Record a single warning or error message and its optional location."""

    severity: DiagnosticSeverity
    message: str
    variable: VariableRef | None = None
    location: ExpressionLocation | None = None


@dataclass(slots=True)
class Diagnostics:
    """Collect general warnings and errors without halting analysis."""

    items: list[Diagnostic] = field(default_factory=list[Diagnostic])

    def warn(
        self,
        message: str,
        *,
        variable: VariableRef | None = None,
        location: ExpressionLocation | None = None,
    ) -> None:
        """Append a warning diagnostic."""
        self.items.append(
            Diagnostic(DiagnosticSeverity.warning, message, variable, location)
        )

    def error(
        self,
        message: str,
        *,
        variable: VariableRef | None = None,
        location: ExpressionLocation | None = None,
    ) -> None:
        """Append an error diagnostic."""
        self.items.append(
            Diagnostic(DiagnosticSeverity.error, message, variable, location)
        )

    @property
    def warnings(self) -> tuple[Diagnostic, ...]:
        """Return all collected warning diagnostics."""
        return tuple(
            item for item in self.items if item.severity == DiagnosticSeverity.warning
        )

    @property
    def errors(self) -> tuple[Diagnostic, ...]:
        """Return all collected error diagnostics."""
        return tuple(
            item for item in self.items if item.severity == DiagnosticSeverity.error
        )

    @property
    def has_errors(self) -> bool:
        """Return True if at least one error diagnostic was recorded."""
        return any(item.severity == DiagnosticSeverity.error for item in self.items)
