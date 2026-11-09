from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import clingo

from constraint_handler import multimap, myClorm
from constraint_handler.schemas import expression, internal, result


class ReasoningMode(Enum):
    """Available strategies for combining values across solver models.

    STANDARD leaves model enumeration unchanged. The other modes accumulate,
    intersect, or combine variable values according to their strategy.
    """

    STANDARD = 1
    BRAVE = 2
    CAUTIOUS = 3
    INTERSECTION = 4
    UNION = 5
    SUPREMUM = 6
    INFIMUM = 7


@dataclass
class _Value:
    """Associate a solver literal with a possible variable value.

    Attributes:
        literal: Solver literal that is true when the value is selected.
        value: Python representation of the possible value.
    """

    literal: int
    value: Any


@dataclass
class _PairValue:
    """Associate a solver literal with a possible multimap pair.

    Attributes:
        literal: Solver literal that is true when the pair is present.
        key: Key in the multimap.
        value: Value associated with the key.
    """

    literal: int
    key: Any
    value: Any


@dataclass
class _ScalarVariable:
    """Track possible and currently selected values for a scalar variable.

    Attributes:
        name: Clingo symbol identifying the variable.
        possible_values: Values that can be selected by this variable.
        value: Selected value from the latest assignment, if any.
        has_value: Whether the latest assignment selected a value.
    """

    name: clingo.Symbol
    possible_values: list[_Value] = field(default_factory=list)
    value: Any = None
    has_value: bool = False

    def update(self, assignment: clingo.Assignment) -> None:
        """Update the selected value from a solver assignment.

        Args:
            assignment: Current solver assignment used to inspect literals.
        """
        for candidate in self.possible_values:
            if assignment.is_true(candidate.literal):
                self.value = candidate.value
                self.has_value = True
                return
        self.has_value = False


@dataclass
class _SetVariable:
    """Track the possible members and current value of a set variable.

    Attributes:
        name: Clingo symbol identifying the variable.
        source: Expression whose member literals represent this set.
        possible_values: Members that can be present in the set.
        value: Set of members present in the latest assignment.
    """

    name: clingo.Symbol
    source: expression.Expr
    possible_values: list[_Value] = field(default_factory=list)
    value: frozenset[Any] = frozenset()

    def update(self, assignment: clingo.Assignment) -> None:
        """Rebuild the set value from true member literals.

        Args:
            assignment: Current solver assignment used to inspect literals.
        """
        self.value = frozenset(
            candidate.value for candidate in self.possible_values if assignment.is_true(candidate.literal)
        )


@dataclass
class _MultimapVariable:
    """Track the possible pairs and current value of a multimap variable.

    Attributes:
        name: Clingo symbol identifying the variable.
        possible_values: Key/value pairs that can be present in the multimap.
        value: Multimap containing the pairs present in the latest assignment.
    """

    name: clingo.Symbol
    possible_values: list[_PairValue] = field(default_factory=list)
    value: multimap.Multimap[Any, Any] = field(default_factory=lambda: multimap.Multimap.from_pairs([]))

    def update(self, assignment: clingo.Assignment) -> None:
        """Rebuild the multimap value from true pair literals.

        Args:
            assignment: Current solver assignment used to inspect literals.
        """
        self.value = multimap.Multimap.from_pairs(
            (candidate.key, candidate.value)
            for candidate in self.possible_values
            if assignment.is_true(candidate.literal)
        )


def _python_value(value: Any) -> Any:
    """Unwrap an expression value or reference into its Python value.

    Args:
        value: Expression value, reference, or already-converted value.

    Returns:
        The underlying Python value for expression values and references;
        otherwise, the input unchanged.
    """
    if isinstance(value, (expression.Val, expression.Ref)):
        return value.value
    return value


def _variable_to_symbol(variable: expression.Variable) -> clingo.Symbol:
    """Convert an expression variable to its Clingo symbol.

    Args:
        variable: Expression variable to convert.

    Returns:
        The Clingo symbol identifying the variable.
    """
    return myClorm.pytocl(variable).arguments[0]


class ReasoningStrategy(ABC):
    """Base class for strategies that combine values across solver models.

    Attributes:
        rm_model: Accumulated values keyed by Clingo variable symbol.
    """

    def __init__(self) -> None:
        """Initialize an empty accumulated model."""
        super().__init__()
        self.rm_model: dict[clingo.Symbol, set[Any]] = {}

    def init(
        self,
        init: clingo.PropagateInit,
        variables: dict[clingo.Symbol, _ScalarVariable | _SetVariable | _MultimapVariable],
    ) -> None:
        """Reset strategy state before a solve begins.

        Args:
            init: Clingo initialization context for the current solve.
            variables: Tracked scalar, set, and multimap variables.
        """
        self.rm_model.clear()

    @abstractmethod
    def join(self, model: dict[clingo.Symbol, object]) -> None:
        """Combine a complete model with the strategy's accumulated state.

        Args:
            model: Variable values from the current solver model.
        """
        raise NotImplementedError()

    def nogoods(self) -> list[Iterable[int]]:
        """Return constraints that guide enumeration for this strategy.

        Returns:
            Nogoods to add to the solver; the base strategy adds none.
        """
        return []


class StandardReasoningMode(ReasoningStrategy):
    """Use ordinary model enumeration without accumulating constraints."""

    def join(self, model: dict[clingo.Symbol, object]) -> None:
        """Leave the strategy state unchanged for a model.

        Args:
            model: Variable values from the current solver model.
        """
        return


class _LiteralReasoningMode(ReasoningStrategy):
    """Share witness and value literals used to prune repeated model values."""

    def __init__(self) -> None:
        """Initialize maps for witness and semantic value literals."""
        super().__init__()
        self.variable_lit: dict[clingo.Symbol, int] = {}
        self.set_or_multimap_value_literals: dict[clingo.Symbol, dict[Any, int]] = {}
        self.scalar_literals: dict[clingo.Symbol, dict[Any, set[int]]] = {}

    def init(
        self,
        init: clingo.PropagateInit,
        variables: dict[clingo.Symbol, _ScalarVariable | _SetVariable | _MultimapVariable],
    ) -> None:
        """Create witnesses and group literals representing equal values.

        Args:
            init: Clingo initialization context for the current solve.
            variables: Tracked variables and their possible values.
        """
        super().init(init, variables)
        self.variable_lit.clear()
        self.set_or_multimap_value_literals.clear()
        self.scalar_literals.clear()

        for name, variable in variables.items():
            self.variable_lit[name] = init.add_literal(freeze=True)
            # Different source atoms may encode the same member or key/value pair.
            value2lits: dict[Any, set[int]] = {}
            for candidate in variable.possible_values:
                if isinstance(candidate, _PairValue):
                    value = (candidate.key, candidate.value)
                else:
                    value = candidate.value
                value2lits.setdefault(value, set()).add(candidate.literal)

            # for scalars we don't need prescence literals since only 1 if true at a time.
            if isinstance(variable, _ScalarVariable):
                self.scalar_literals[name] = value2lits
                continue

            self.set_or_multimap_value_literals[name] = {}
            for value, literals in value2lits.items():
                # With one source literal, that literal already means this value is present.
                if len(literals) == 1:
                    self.set_or_multimap_value_literals[name][value] = next(iter(literals))
                    continue
                # Encode presence as the OR of all literals representing this value.
                presence = init.add_literal(freeze=True)
                self.set_or_multimap_value_literals[name][value] = presence
                init.add_clause([-presence, *literals])
                for literal in literals:
                    init.add_clause([-literal, presence])

    def _set_or_multimap_value_nogood(self, name: clingo.Symbol, value: Any, helper: int) -> tuple[int, ...]:
        """Build a nogood that disables a witness for an unchanged collection.

        The returned literals describe the complete set or multimap value,
        followed by the helper literal.

        Args:
            name: Symbol identifying the set or multimap variable.
            value: Complete set or multimap value to match.
            helper: Literal representing this variable's progress witness.

        Returns:
            A nogood matching the complete value and helper literal.
        """
        if isinstance(value, multimap.Multimap):
            retained = set()
            # build the key, value pairs for the multimap
            for key, items in value.items():
                for item in items:
                    retained.add((key, item))
        else:
            retained = value

        # Exact-value matching is identical for union and intersection, so no union flag is needed.
        # Their callers choose which accumulated values to block from witnessing progress.
        equality = []
        for item, literal in self.set_or_multimap_value_literals[name].items():
            # Match both present and absent members so this represents the whole value.
            if item in retained:
                equality.append(literal)
            else:
                equality.append(-literal)
        equality.append(helper)
        return tuple(equality)

    def _set_or_multimap_member_nogood(
        self, name: clingo.Symbol, value: Any, helper: int, *, union: bool = False
    ) -> tuple[int, ...]:
        """Build a progress nogood from collection members rather than whole values.

        Args:
            name: Symbol identifying the set or multimap variable.
            value: Collection containing retained or already-seen members.
            helper: Literal representing this variable's progress witness.
            union: Match absent unseen members instead of present retained members.

        Returns:
            Member literals followed by the helper literal.
        """
        if isinstance(value, multimap.Multimap):
            members = {(key, item) for key, items in value.items() for item in items}
        else:
            members = value

        literals = self.set_or_multimap_value_literals[name]
        # Memberwise progress is directional, so the union flag selects which condition to match.
        if union:
            # Union needs an unseen member to appear; match all unseen members being absent.
            nogood = [-literal for item, literal in literals.items() if item not in members]
        else:
            # Intersection needs a retained member to disappear; match all retained members being present.
            nogood = [literals[item] for item in members]
        return (*nogood, helper)


class IntersectionReasoningMode(_LiteralReasoningMode):
    """Retain complete variable values that agree across all models."""

    def __init__(self) -> None:
        """Initialize intersection state for a new solve."""
        super().__init__()
        self._initialized = False

    def init(
        self,
        init: clingo.PropagateInit,
        variables: dict[clingo.Symbol, _ScalarVariable | _SetVariable | _MultimapVariable],
    ) -> None:
        """Reset the accumulated intersection and initialize its literals.

        Args:
            init: Clingo initialization context for the current solve.
            variables: Tracked variables and their possible values.
        """
        super().init(init, variables)
        self._initialized = False

    def join(self, model: dict[clingo.Symbol, object]) -> None:
        """Intersect accumulated variable values with a solver model.

        Args:
            model: Variable values from the current solver model.
        """
        if not self._initialized:
            self.rm_model = {key: {value} for key, value in model.items()}
            self._initialized = True
            return
        for key, values in tuple(self.rm_model.items()):
            if key not in model:
                del self.rm_model[key]
            else:
                values.intersection_update({model[key]})
                if not values:
                    del self.rm_model[key]

    def nogoods(self) -> list[Iterable[int]]:
        """Require progress beyond the retained complete variable values.

        Returns:
            Nogoods that allow another model only when a retained value changes.
        """
        nogoods: list[Iterable[int]] = []
        witnesses = []
        for name, helper in self.variable_lit.items():
            rm_values = self.rm_model.get(name, set())
            if not rm_values:
                # An empty intersection cannot witness another change.
                nogoods.append((helper,))
                continue
            # we do this because for intersection there is always just one value in values_in_rm_model
            value = next(iter(rm_values))
            if name in self.scalar_literals:
                for literal in self.scalar_literals[name][value]:
                    # if the literal corresponds to the retained value then the helper is false
                    # and thus the witness nogood can still fire
                    nogoods.append((literal, helper))
            else:
                nogoods.append(self._set_or_multimap_value_nogood(name, value, helper))
            witnesses.append(-helper)
        # A nogood of negated helpers requires at least one active helper to be true.
        nogoods.append(tuple(witnesses))
        return nogoods


class UnionReasoningMode(_LiteralReasoningMode):
    """Accumulate distinct complete variable values and search for unseen values."""

    def init(
        self,
        init: clingo.PropagateInit,
        variables: dict[clingo.Symbol, _ScalarVariable | _SetVariable | _MultimapVariable],
    ) -> None:
        """Initialize literals and add witness and scalar selection guards once.

        Args:
            init: Clingo initialization context for the current solve.
            variables: Tracked variables and their possible values.
        """
        super().init(init, variables)
        init.add_clause(list(self.variable_lit.values()))
        for name, value2lit in self.scalar_literals.items():
            literals = set()
            for alternatives in value2lit.values():
                literals.update(alternatives)
            init.add_clause([*literals, -self.variable_lit[name]])

    def join(self, model: dict[clingo.Symbol, object]) -> None:
        """Add each model value to the accumulated set of values.

        Args:
            model: Variable values from the current solver model.
        """
        for key, value in model.items():
            if key in self.rm_model:
                self.rm_model[key].add(value)
            else:
                self.rm_model[key] = {value}

    def nogoods(self) -> list[Iterable[int]]:
        """Require progress from at least one variable's unseen value.

        Returns:
            Nogoods that prevent already-seen values from witnessing progress.
        """
        nogoods: list[Iterable[int]] = []
        for name, helper in self.variable_lit.items():
            rm_values = self.rm_model.get(name, set())
            if name in self.scalar_literals:
                value2lit = self.scalar_literals[name]
                for value in rm_values:
                    for literal in value2lit[value]:
                        nogoods.append((literal, helper))
            else:
                nogoods.extend([self._set_or_multimap_value_nogood(name, value, helper) for value in rm_values])
        return nogoods


class SupremumReasoningMode(ReasoningStrategy):
    """Accumulate the supremum of each variable across solver models."""

    def join(self, model: dict[clingo.Symbol, object]) -> None:
        """Accumulate the least upper bound of a model's variable values.

        Args:
            model: Variable values from the current solver model.
        """
        for key, value in model.items():
            if key not in self.rm_model:
                self.rm_model[key] = {value}
                continue
            current = next(iter(self.rm_model[key]))
            self.rm_model[key] = {self._supremum(current, value)}

    @staticmethod
    def _supremum(left: Any, right: Any) -> Any:
        """Compute the least upper bound of two values.

        Args:
            left: First scalar or collection value.
            right: Second scalar or collection value.

        Returns:
            Their union for collections or their maximum for scalars.
        """
        if isinstance(left, frozenset) and isinstance(right, frozenset):
            return left.union(right)
        if isinstance(left, multimap.Multimap) and isinstance(right, multimap.Multimap):
            return multimap.Multimap.from_pairs(
                (key, value) for source in (left, right) for key, values in source.items() for value in values
            )
        # if left or right are not a number return "TOP"
        if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
            return "TOP"
        return max(left, right)


class InfimumReasoningMode(ReasoningStrategy):
    """Accumulate the infimum of each variable across solver models."""

    def join(self, model: dict[clingo.Symbol, object]) -> None:
        """Accumulate the greatest lower bound of a model's variable values.

        Args:
            model: Variable values from the current solver model.
        """
        for key, value in model.items():
            if key not in self.rm_model:
                self.rm_model[key] = {value}
                continue
            current = next(iter(self.rm_model[key]))
            self.rm_model[key] = {self._infimum(current, value)}

    @staticmethod
    def _infimum(left: Any, right: Any) -> Any:
        """Compute the greatest lower bound of two values.

        Args:
            left: First scalar or collection value.
            right: Second scalar or collection value.

        Returns:
            Their intersection for collections or their minimum for scalars.
        """
        if isinstance(left, frozenset) and isinstance(right, frozenset):
            return left.intersection(right)
        if isinstance(left, multimap.Multimap) and isinstance(right, multimap.Multimap):
            return multimap.Multimap.from_pairs(
                (key, value) for key, values in left.items() for value in values & right.get(key, frozenset())
            )
        # if left or right are not a number return "BOT"
        if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
            return "BOT"
        return min(left, right)


REASONING_STRATEGIES = {
    ReasoningMode.STANDARD: StandardReasoningMode,
    ReasoningMode.INTERSECTION: IntersectionReasoningMode,
    ReasoningMode.UNION: UnionReasoningMode,
    ReasoningMode.SUPREMUM: SupremumReasoningMode,
    ReasoningMode.INFIMUM: InfimumReasoningMode,
}


class ReasoningModesPropagator(clingo.Propagator):
    """Build variable models and apply nogoods for a reasoning strategy.

    Attributes:
        reasoning_strategy: Strategy used to combine successive models.
        disabled: Whether standard enumeration makes propagation unnecessary.
    """

    def __init__(self, reasoning_mode: ReasoningMode = ReasoningMode.STANDARD) -> None:
        """Create a propagator using the selected reasoning mode.

        Args:
            reasoning_mode: Strategy to use during model enumeration.
        """
        self.reasoning_strategy: ReasoningStrategy = REASONING_STRATEGIES[reasoning_mode]()
        self._variables: dict[clingo.Symbol, _ScalarVariable | _SetVariable | _MultimapVariable] = {}
        self._watched_literals: set[int] = set()
        self._nogood_queue: deque[Iterable[int]] = deque()

        self.disabled = isinstance(self.reasoning_strategy, StandardReasoningMode)

    def set_mode(self, reasoning_mode: ReasoningMode) -> None:
        """Replace the active reasoning strategy.

        Args:
            reasoning_mode: Strategy to use during model enumeration.
        """
        self.reasoning_strategy = REASONING_STRATEGIES[reasoning_mode]()
        self.disabled = isinstance(self.reasoning_strategy, StandardReasoningMode)

    def init(self, init: clingo.PropagateInit) -> None:
        """Load variable values and register watched solver literals.

        Args:
            init: Clingo initialization context for the current solve.
        """
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
            name = _variable_to_symbol(expr)
            if isinstance(value, internal.Ref) and str(value.type_) == "set":
                self._variables.setdefault(name, _SetVariable(name, value.expr))
            elif isinstance(value, internal.Ref) and str(value.type_) == "multimap":
                self._variables.setdefault(name, _MultimapVariable(name))
            else:
                scalar = self._variables.setdefault(name, _ScalarVariable(name))
                if isinstance(scalar, _ScalarVariable):
                    scalar.possible_values.append(_Value(literal, _python_value(value)))

        for (expr, value), literal in set_values.items():
            for variable in self._variables.values():
                if isinstance(variable, _SetVariable) and variable.source == expr:
                    variable.possible_values.append(_Value(literal, _python_value(value)))
                    self._watched_literals.add(literal)

        for (name, key, value), literal in multimap_values.items():
            variable_name = myClorm.pytocl(expression.Variable(name)).arguments[0]
            variable = self._variables.get(variable_name)
            if isinstance(variable, _MultimapVariable):
                variable.possible_values.append(_PairValue(literal, _python_value(key), _python_value(value)))
                self._watched_literals.add(literal)

        for variable in self._variables.values():
            if isinstance(variable, _ScalarVariable):
                self._watched_literals.update(candidate.literal for candidate in variable.possible_values)
        for literal in self._watched_literals:
            init.add_watch(literal)
        self.reasoning_strategy.init(init, self._variables)

    def propagate(self, control: clingo.PropagateControl, changes: Sequence[int]) -> None:
        """Add queued nogoods without updating tracked variable values.

        Args:
            control: Clingo control used to add nogoods.
            changes: Watched literals whose assignments changed.
        """
        if self.disabled:
            return
        self._add_nogoods(control)

    def check(self, control: clingo.PropagateControl) -> None:
        """Process a total assignment and queue constraints for further progress.

        Args:
            control: Clingo control containing the current assignment.
        """
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
        # Let this assignment finish before installing nogoods that demand further progress.
        self._nogood_queue.extend(tuple(nogood) for nogood in self.reasoning_strategy.nogoods())

        # print values stored
        import pprint

        print("Stored values:")
        pprint.pprint(self.reasoning_strategy.rm_model)

    def _add_nogoods(self, control: clingo.PropagateControl) -> bool:
        """Add queued nogoods until the queue is empty or propagation stops.

        Args:
            control: Clingo control used to add nogoods.

        Returns:
            Whether adding a nogood stopped propagation.
        """
        while self._nogood_queue:
            nogood = self._nogood_queue.popleft()
            if not control.add_nogood(nogood, tag=True, lock=True):
                return True
        return False


def _has_value(variable: _ScalarVariable | _SetVariable | _MultimapVariable) -> bool:
    """Report whether a tracked variable has a selected scalar value.

    Collection variables always have a value, including when empty.

    Args:
        variable: Tracked scalar, set, or multimap variable.

    Returns:
        Whether the variable has a value in the current assignment.
    """
    return not isinstance(variable, _ScalarVariable) or variable.has_value
