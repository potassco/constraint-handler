from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import clingo
from click.decorators import R

from constraint_handler import multimap, myClorm
from constraint_handler.schemas import expression, internal, result


class ReasoningMode(Enum):
    STANDARD = 1
    BRAVE = 2
    CAUTIOUS = 3
    INTERSECTION = 4
    UNION = 5
    SUPREMUM = 6
    INFIMUM = 7


@dataclass
class _Candidate:
    literal: int
    value: Any


@dataclass
class _PairCandidate:
    literal: int
    key: Any
    value: Any


@dataclass
class _ScalarVariable:
    name: clingo.Symbol
    candidates: list[_Candidate] = field(default_factory=list)
    value: Any = None
    has_value: bool = False

    def update(self, assignment: clingo.Assignment) -> None:
        for candidate in self.candidates:
            if assignment.is_true(candidate.literal):
                self.value = candidate.value
                self.has_value = True
                return
        self.has_value = False


@dataclass
class _SetVariable:
    name: clingo.Symbol
    source: expression.Expr
    candidates: list[_Candidate] = field(default_factory=list)
    value: frozenset[Any] = frozenset()

    def update(self, assignment: clingo.Assignment) -> None:
        self.value = frozenset(
            candidate.value for candidate in self.candidates if assignment.is_true(candidate.literal)
        )


@dataclass
class _MultimapVariable:
    name: clingo.Symbol
    candidates: list[_PairCandidate] = field(default_factory=list)
    value: multimap.Multimap[Any, Any] = field(default_factory=lambda: multimap.Multimap.from_pairs([]))

    def update(self, assignment: clingo.Assignment) -> None:
        self.value = multimap.Multimap.from_pairs(
            (candidate.key, candidate.value) for candidate in self.candidates if assignment.is_true(candidate.literal)
        )


def _python_value(value: Any) -> Any:
    if isinstance(value, (expression.Val, expression.Ref)):
        return value.value
    return value


def _variable_symbol(variable: expression.Variable) -> clingo.Symbol:
    return myClorm.pytocl(variable).arguments[0]


class ReasoningStrategy(ABC):
    """Base class for reasoning modes."""

    def __init__(self) -> None:
        super().__init__()
        self.model: dict[clingo.Symbol, set[Any]] = {}

    @abstractmethod
    def join(self, model: dict[clingo.Symbol, object]) -> None:
        """Update the reasoning mode based on the join with the given model."""
        raise NotImplementedError()

    def nogoods(self) -> list[Iterable[int]]:
        """Return the nogoods associated with the current reasoning mode."""
        return []


class StandardReasoningMode(ReasoningStrategy):
    def join(self, model: dict[clingo.Symbol, object]) -> None:
        """Update the reasoning mode based on the standard join with the given model."""
        return


class IntersectionReasoningMode(ReasoningStrategy):
    def join(self, model: dict[clingo.Symbol, object]) -> None:
        """Update the reasoning mode based on the intersection with the given model."""
        # intersect the current model with the given model
        for key, value in model.items():
            if key in self.model:
                self.model[key] &= {value}
            else:
                self.model[key] = {value}


class UnionReasoningMode(ReasoningStrategy):
    def join(self, model: dict[clingo.Symbol, object]) -> None:
        """Update the reasoning mode based on the union with the given model."""
        for key, value in model.items():
            if key in self.model:
                self.model[key] |= {value}
            else:
                self.model[key] = {value}


class SupremumReasoningMode(ReasoningStrategy):
    def join(self, model: dict[clingo.Symbol, object]) -> None:
        """Update the reasoning mode based on the supremum with the given model."""
        for key, value in model.items():
            if key not in self.model:
                self.model[key] = {value}
                continue
            current = next(iter(self.model[key]))
            self.model[key] = {self._supremum(current, value)}

    @staticmethod
    def _supremum(left: Any, right: Any) -> Any:
        if isinstance(left, frozenset) and isinstance(right, frozenset):
            return left.union(right)
        if isinstance(left, multimap.Multimap) and isinstance(right, multimap.Multimap):
            return multimap.Multimap.from_pairs(
                (key, value) for source in (left, right) for key, values in source.items() for value in values
            )
        return max(left, right)


class InfimumReasoningMode(ReasoningStrategy):
    def join(self, model: dict[clingo.Symbol, object]) -> None:
        """Update the reasoning mode based on the infimum with the given model."""
        for key, value in model.items():
            if key not in self.model:
                self.model[key] = {value}
                continue
            current = next(iter(self.model[key]))
            self.model[key] = {self._infimum(current, value)}

    @staticmethod
    def _infimum(left: Any, right: Any) -> Any:
        if isinstance(left, frozenset) and isinstance(right, frozenset):
            return left.intersection(right)
        if isinstance(left, multimap.Multimap) and isinstance(right, multimap.Multimap):
            return multimap.Multimap.from_pairs(
                (key, value) for key, values in left.items() for value in values & right.get(key, frozenset())
            )
        return min(left, right)


def _supremum(left: Any, right: Any) -> Any:
    if isinstance(left, frozenset) and isinstance(right, frozenset):
        return left.union(right)
    if isinstance(left, multimap.Multimap) and isinstance(right, multimap.Multimap):
        return multimap.Multimap.from_pairs(
            (key, value) for source in (left, right) for key, values in source.items() for value in values
        )
    return max(left, right)


def _infimum(left: Any, right: Any) -> Any:
    if isinstance(left, frozenset) and isinstance(right, frozenset):
        return left.intersection(right)
    if isinstance(left, multimap.Multimap) and isinstance(right, multimap.Multimap):
        return multimap.Multimap.from_pairs(
            (key, value) for key, values in left.items() for value in values & right.get(key, frozenset())
        )
    return min(left, right)


REASONING_STRATEGIES = {
    ReasoningMode.STANDARD: StandardReasoningMode(),
    ReasoningMode.INTERSECTION: IntersectionReasoningMode(),
    ReasoningMode.UNION: UnionReasoningMode(),
    ReasoningMode.SUPREMUM: SupremumReasoningMode(),
    ReasoningMode.INFIMUM: InfimumReasoningMode(),
}


class ReasoningModesPropagator(clingo.Propagator):
    """Build complete variable models and apply nogoods from a reasoning mode."""

    def __init__(self, reasoning_mode: ReasoningMode = ReasoningMode.STANDARD) -> None:
        self.reasoning_strategy = REASONING_STRATEGIES[reasoning_mode]
        self._variables: dict[clingo.Symbol, _ScalarVariable | _SetVariable | _MultimapVariable] = {}
        self._watched_literals: set[int] = set()
        self._nogood_queue: deque[Iterable[int]] = deque()

        self.disabled = isinstance(self.reasoning_strategy, StandardReasoningMode)

    def set_mode(self, reasoning_mode: ReasoningMode) -> None:
        self.reasoning_strategy = REASONING_STRATEGIES[reasoning_mode]
        self.disabled = isinstance(self.reasoning_strategy, StandardReasoningMode)

    def init(self, init: clingo.PropagateInit) -> None:
        """Load current-solver variable values and register their literals."""
        if self.disabled:
            return
        self._variables.clear()
        self._watched_literals.clear()
        self._nogood_queue.clear()
        init.check_mode = clingo.PropagatorCheckMode.Total

        se_values = myClorm.findInPropagateInit(init, internal._se_value)
        set_values = myClorm.findInPropagateInit(init, internal._set_contains)
        multimap_values = myClorm.findInPropagateInit(init, result.Multimap_value)

        for (expr, value), literal in se_values.items():
            if not isinstance(expr, expression.Variable):
                continue
            name = _variable_symbol(expr)
            if isinstance(value, internal.Ref) and str(value.type_) == "set":
                self._variables.setdefault(name, _SetVariable(name, value.expr))
            elif isinstance(value, internal.Ref) and str(value.type_) == "multimap":
                self._variables.setdefault(name, _MultimapVariable(name))
            else:
                scalar = self._variables.setdefault(name, _ScalarVariable(name))
                if isinstance(scalar, _ScalarVariable):
                    scalar.candidates.append(_Candidate(literal, _python_value(value)))

        for (expr, value), literal in set_values.items():
            for variable in self._variables.values():
                if isinstance(variable, _SetVariable) and variable.source == expr:
                    variable.candidates.append(_Candidate(literal, _python_value(value)))
                    self._watched_literals.add(literal)

        for (name, key, value), literal in multimap_values.items():
            variable_name = myClorm.pytocl(expression.Variable(name)).arguments[0]
            variable = self._variables.get(variable_name)
            if isinstance(variable, _MultimapVariable):
                variable.candidates.append(_PairCandidate(literal, _python_value(key), _python_value(value)))
                self._watched_literals.add(literal)

        for variable in self._variables.values():
            if isinstance(variable, _ScalarVariable):
                self._watched_literals.update(candidate.literal for candidate in variable.candidates)
        for literal in self._watched_literals:
            init.add_watch(literal)

    def propagate(self, control: clingo.PropagateControl, changes: Sequence[int]) -> None:
        """Drain queued nogoods without updating variable values."""
        if self.disabled:
            return
        self._add_nogoods(control)

    def check(self, control: clingo.PropagateControl) -> None:
        """Build a total model, join it into the mode, and add its nogoods."""
        if self.disabled:
            return
        if self._add_nogoods(control):
            return
        if not control.assignment.is_total:
            return

        for variable in self._variables.values():
            variable.update(control.assignment)
        model = {variable.name: variable.value for variable in self._variables.values() if _has_value(variable)}
        self.reasoning_strategy.join(model)
        self._nogood_queue.extend(self.reasoning_strategy.nogoods())
        self._add_nogoods(control)

        # print values stored
        import pprint

        print("Stored values:")
        pprint.pprint(self.reasoning_strategy.model)

    def _add_nogoods(self, control: clingo.PropagateControl) -> bool:
        while self._nogood_queue:
            nogood = self._nogood_queue.popleft()
            if not control.add_nogood(nogood, lock=True):
                return True
        return False


def _has_value(variable: _ScalarVariable | _SetVariable | _MultimapVariable) -> bool:
    return not isinstance(variable, _ScalarVariable) or variable.has_value
