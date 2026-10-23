"""Shared context and callable contract for value-based domain evaluators."""

from collections.abc import Callable
from dataclasses import dataclass

from ..diagnostics import Diagnostics
from ..internal_input import ExprId
from ..python_input import Operator
from .values import Domain


@dataclass(frozen=True, slots=True)
class EvaluationContext:
    """Share diagnostics and size limits without mutable expression state."""

    diagnostics: Diagnostics
    threshold: int
    boolean_threshold: int


type DomainHandler = Callable[
    [EvaluationContext, Operator, list[Domain], ExprId | None], Domain
]
