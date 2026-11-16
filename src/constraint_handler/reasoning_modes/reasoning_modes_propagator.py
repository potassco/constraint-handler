from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import clingo

from constraint_handler import evaluator, multimap, myClorm
from constraint_handler.schemas import expression, internal, post, result


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


class _LatticeBound(Enum):
    TOP = "TOP"
    BOT = "BOT"


@dataclass
class _Value:
    """Associate a program literal with a possible variable value.

    Attributes:
        literal: Program literal that is true when the value is selected.
        value: Python representation of the possible value.
    """

    literal: int
    value: Any


@dataclass
class _PairValue:
    """Associate a program literal with a possible multimap pair.

    Attributes:
        literal: Program literal that is true when the pair is present.
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

    def update(self, model: clingo.Model) -> None:
        """Update the selected value from an accepted model.

        Args:
            model: Current model used to inspect program literals.
        """
        for candidate in self.possible_values:
            if model.is_true(candidate.literal):
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

    def update(self, model: clingo.Model) -> None:
        """Rebuild the set value from true member literals.

        Args:
            model: Current model used to inspect program literals.
        """
        self.value = frozenset(
            candidate.value for candidate in self.possible_values if model.is_true(candidate.literal)
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

    def update(self, model: clingo.Model) -> None:
        """Rebuild the multimap value from true pair literals.

        Args:
            model: Current model used to inspect program literals.
        """
        self.value = multimap.Multimap.from_pairs(
            (candidate.key, candidate.value) for candidate in self.possible_values if model.is_true(candidate.literal)
        )


def _python_value(value: Any) -> Any:
    """Unwrap an expression value or reference into its Python value.

    Args:
        value: Expression value, reference, or already-converted value.

    Returns:
        The underlying Python value for expression values and references;
        otherwise, the input unchanged.
    """
    if isinstance(value, internal.Ref):
        evaluated_value, errors = evaluator.evaluate_expr(value.expr)
        if errors or evaluated_value is expression.Bad.bad:
            return expression.Bad.bad
        if str(value.type_) == "set" and isinstance(evaluated_value, (set, frozenset)):
            return frozenset(evaluated_value)
        return expression.Bad.bad
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
        variable_lit: Witness literals keyed by Clingo variable symbol.
        value_literals: Value literals keyed by variable and value.
        scalar_variables: Names of scalar variables.
    """

    def __init__(self) -> None:
        """Initialize an empty accumulated model."""
        super().__init__()
        self.rm_model: dict[clingo.Symbol, set[Any]] = {}
        self.variable_lit: dict[clingo.Symbol, int] = {}
        self.value_literals: dict[clingo.Symbol, dict[Any, int]] = {}
        self.scalar_variables: set[clingo.Symbol] = set()

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

    def _init_literals(
        self,
        init: clingo.PropagateInit,
        variables: dict[clingo.Symbol, _ScalarVariable | _SetVariable | _MultimapVariable],
    ) -> None:
        """Freeze prepared witnesses and map values to program literals."""
        self.value_literals.clear()
        self.scalar_variables.clear()

        for name, variable in variables.items():
            init.freeze_literal(init.solver_literal(self.variable_lit[name]))
            self.value_literals[name] = {}
            if isinstance(variable, _ScalarVariable):
                self.scalar_variables.add(name)

            for candidate in variable.possible_values:
                if isinstance(candidate, _PairValue):
                    value = (candidate.key, candidate.value)
                else:
                    value = candidate.value
                self.value_literals[name][value] = candidate.literal

    def _set_or_multimap_value_nogood(self, name: clingo.Symbol, value: Any, helper: int) -> tuple[int, ...]:
        """Build a nogood that matches a complete collection value and witness."""
        if isinstance(value, multimap.Multimap):
            retained = {(key, item) for key, items in value.items() for item in items}
        else:
            retained = value

        equality = []
        for item, literal in self.value_literals[name].items():
            equality.append(literal if item in retained else -literal)
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
            members = set()
            for key, items in value.items():
                for item in items:
                    members.add((key, item))
        else:
            members = value

        literals = self.value_literals[name]
        if union:
            nogood = []
            for item, literal in literals.items():
                if item not in members:
                    nogood.append(-literal)
        else:
            nogood = [literals[item] for item in members]
        return (*nogood, helper)


class StandardReasoningMode(ReasoningStrategy):
    """Use ordinary model enumeration without accumulating constraints."""

    def join(self, model: dict[clingo.Symbol, object]) -> None:
        """Leave the strategy state unchanged for a model.

        Args:
            model: Variable values from the current solver model.
        """
        return


class IntersectionReasoningMode(ReasoningStrategy):
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
        self._init_literals(init, variables)
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
        if not self.variable_lit:
            return []

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
            if name in self.scalar_variables:
                # If the literal corresponds to the retained value, the helper
                # is false and the witness nogood can still fire.
                nogoods.append((self.value_literals[name][value], helper))
            else:
                nogoods.append(self._set_or_multimap_value_nogood(name, value, helper))
            witnesses.append(-helper)
        # A nogood of negated helpers requires at least one active helper to be true.
        nogoods.append(tuple(witnesses))
        return nogoods


class UnionReasoningMode(ReasoningStrategy):
    """Accumulate distinct complete variable values and search for unseen values."""

    def init(
        self,
        init: clingo.PropagateInit,
        variables: dict[clingo.Symbol, _ScalarVariable | _SetVariable | _MultimapVariable],
    ) -> None:
        """Initialize literals used to track candidate values.

        Args:
            init: Clingo initialization context for the current solve.
            variables: Tracked variables and their possible values.
        """
        super().init(init, variables)
        self._init_literals(init, variables)

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
            if name in self.scalar_variables:
                for value in rm_values:
                    nogoods.append((self.value_literals[name][value], helper))
            else:
                nogoods.extend([self._set_or_multimap_value_nogood(name, value, helper) for value in rm_values])
        return nogoods


class SupremumReasoningMode(ReasoningStrategy):
    """Accumulate the supremum of each variable across solver models."""

    def init(
        self,
        init: clingo.PropagateInit,
        variables: dict[clingo.Symbol, _ScalarVariable | _SetVariable | _MultimapVariable],
    ) -> None:
        """Reset accumulated bounds and initialize candidate literals."""
        super().init(init, variables)
        self._init_literals(init, variables)

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
            Their union for collections, maximum for numbers, or TOP for
            unequal nonnumeric values. Equal nonnumeric values are unchanged.
        """
        if isinstance(left, frozenset) and isinstance(right, frozenset):
            return left.union(right)
        if isinstance(left, multimap.Multimap) and isinstance(right, multimap.Multimap):
            pairs = []
            for source in (left, right):
                for key, values in source.items():
                    for value in values:
                        pairs.append((key, value))
            return multimap.Multimap.from_pairs(pairs)
        if isinstance(left, bool) and isinstance(right, bool):
            return left or right
        if isinstance(left, bool) or isinstance(right, bool):
            return _LatticeBound.TOP
        if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
            return left if left == right else _LatticeBound.TOP
        return max(left, right)

    def nogoods(self) -> list[Iterable[int]]:
        """Require at least one variable to improve the accumulated supremum.

        Returns:
            Nogoods blocking unchanged scalar bounds and already-seen members
            from witnessing progress after the current model.
        """
        nogoods: list[Iterable[int]] = []
        for name, helper in self.variable_lit.items():
            if name not in self.rm_model:
                continue
            current = next(iter(self.rm_model[name]))
            if name in self.scalar_variables:
                for value, literal in self.value_literals[name].items():
                    if self._supremum(current, value) == current:
                        nogoods.append((literal, helper))
            else:
                nogoods.append(self._set_or_multimap_member_nogood(name, current, helper, union=True))
        return nogoods


class InfimumReasoningMode(ReasoningStrategy):
    """Accumulate the infimum of each variable across solver models."""

    def init(
        self,
        init: clingo.PropagateInit,
        variables: dict[clingo.Symbol, _ScalarVariable | _SetVariable | _MultimapVariable],
    ) -> None:
        """Reset accumulated bounds and initialize candidate literals."""
        super().init(init, variables)
        self._init_literals(init, variables)

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
            Their intersection for collections, minimum for numbers, or BOT for
            unequal nonnumeric values. Equal nonnumeric values are unchanged.
        """
        if isinstance(left, frozenset) and isinstance(right, frozenset):
            return left.intersection(right)
        if isinstance(left, multimap.Multimap) and isinstance(right, multimap.Multimap):
            return multimap.Multimap.from_pairs(
                (key, value) for key, values in left.items() for value in values & right.get(key, frozenset())
            )
        if isinstance(left, bool) and isinstance(right, bool):
            return left and right
        if isinstance(left, bool) or isinstance(right, bool):
            return _LatticeBound.BOT
        if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
            return left if left == right else _LatticeBound.BOT
        return min(left, right)

    def nogoods(self) -> list[Iterable[int]]:
        """Require at least one variable to improve the accumulated infimum.

        Returns:
            Nogoods blocking unchanged scalar bounds and retained members
            from witnessing progress after the current model.
        """
        nogoods: list[Iterable[int]] = []
        for name, helper in self.variable_lit.items():
            if name not in self.rm_model:
                continue
            current = next(iter(self.rm_model[name]))
            if name in self.scalar_variables:
                for value, literal in self.value_literals[name].items():
                    if self._infimum(current, value) == current:
                        nogoods.append((literal, helper))
            else:
                nogoods.append(self._set_or_multimap_member_nogood(name, current, helper))
        return nogoods


REASONING_STRATEGIES = {
    ReasoningMode.STANDARD: StandardReasoningMode,
    ReasoningMode.INTERSECTION: IntersectionReasoningMode,
    ReasoningMode.UNION: UnionReasoningMode,
    ReasoningMode.SUPREMUM: SupremumReasoningMode,
    ReasoningMode.INFIMUM: InfimumReasoningMode,
}


class ReasoningModesPropagator(clingo.Propagator):
    """Build variable models and apply nogoods for a reasoning strategy.

    Call prepare after grounding and before each solve, and pass on_model to
    the solve callback. The main API wires both steps automatically.

    Attributes:
        reasoning_mode: Selected mode used to name aggregate model atoms.
        reasoning_strategy: Strategy used to combine successive models.
        disabled: Whether standard enumeration makes propagation unnecessary.
    """

    def __init__(self, reasoning_mode: ReasoningMode = ReasoningMode.STANDARD) -> None:
        """Create a propagator using the selected reasoning mode.

        Args:
            reasoning_mode: Strategy to use during model enumeration.
        """
        self.reasoning_mode = reasoning_mode
        self.reasoning_strategy: ReasoningStrategy = REASONING_STRATEGIES[reasoning_mode]()
        self._variables: dict[clingo.Symbol, _ScalarVariable | _SetVariable | _MultimapVariable] = {}
        self._witnesses: dict[clingo.Symbol, int] = {}

        self.disabled = isinstance(self.reasoning_strategy, StandardReasoningMode)

    def set_mode(self, reasoning_mode: ReasoningMode) -> None:
        """Replace the active reasoning strategy.

        Args:
            reasoning_mode: Strategy to use during model enumeration.
        """
        self.reasoning_mode = reasoning_mode
        self.reasoning_strategy = REASONING_STRATEGIES[reasoning_mode]()
        self.disabled = isinstance(self.reasoning_strategy, StandardReasoningMode)

    def prepare(self, control: clingo.Control) -> None:
        """Load program literals and support progress witnesses before solving.

        Args:
            control: Grounded control whose next solve will use this strategy.
        """
        if self.disabled:
            return
        self._variables.clear()

        se_values = myClorm.findInControl(control, internal._se_value)
        set_values = myClorm.findInControl(control, internal._set_contains)
        multimap_values = myClorm.findInControl(control, result.Multimap_value)
        user_variables: set[clingo.Symbol] = set()
        for ch_post_atom in myClorm.findInControl(control, post.Ch_post).values():
            interface = ch_post_atom.declaration
            if isinstance(interface, post.Variable_interface):
                variable = expression.Variable(interface.variable)
                user_variables.add(_variable_to_symbol(variable))

        for atom, (expr, value) in se_values.items():
            if not isinstance(expr, expression.Variable):
                continue
            name = _variable_to_symbol(expr)
            if name not in user_variables:
                continue
            if isinstance(value, internal.Ref) and str(value.type_) == "set":
                self._variables.setdefault(name, _SetVariable(name, value.expr))
            elif isinstance(value, internal.Ref) and str(value.type_) == "multimap":
                self._variables.setdefault(name, _MultimapVariable(name))
            else:
                scalar = self._variables.setdefault(name, _ScalarVariable(name))
                if isinstance(scalar, _ScalarVariable):
                    scalar.possible_values.append(_Value(atom.literal, _python_value(value)))

        for atom, (expr, value) in set_values.items():
            for variable in self._variables.values():
                if isinstance(variable, _SetVariable) and variable.source == expr:
                    variable.possible_values.append(_Value(atom.literal, _python_value(value)))

        for atom, (name, key, value) in multimap_values.items():
            variable_name = myClorm.pytocl(expression.Variable(name)).arguments[0]
            variable = self._variables.get(variable_name)
            if isinstance(variable, _MultimapVariable):
                variable.possible_values.append(_PairValue(atom.literal, _python_value(key), _python_value(value)))

        with control.backend() as backend:
            for name in self._variables:
                if name not in self._witnesses:
                    helper = backend.add_atom()
                    backend.add_rule([helper], choice=True)
                    self._witnesses[name] = helper
        self.reasoning_strategy.variable_lit = {name: self._witnesses[name] for name in self._variables}

    def init(self, init: clingo.PropagateInit) -> None:
        """Reset accumulation and initialize guards for the current solve."""
        if self.disabled:
            return
        self.reasoning_strategy.init(init, self._variables)

    def on_model(self, model: clingo.Model) -> None:
        """Accumulate an accepted model and constrain the search for the next.

        Args:
            model: Accepted model whose program literals determine its values.
        """
        if self.disabled:
            return

        for variable in self._variables.values():
            variable.update(model)
        values = {variable.name: variable.value for variable in self._variables.values() if _has_value(variable)}
        self.reasoning_strategy.join(values)
        nogoods = self.reasoning_strategy.nogoods()
        for name, variable in self._variables.items():
            if isinstance(variable, _ScalarVariable):
                candidate_literals = (candidate.literal for candidate in variable.possible_values)
                nogoods.append(
                    (
                        self.reasoning_strategy.variable_lit[name],
                        *(-literal for literal in candidate_literals),
                    )
                )
        if self._variables:
            nogoods.append(tuple(-helper for helper in self.reasoning_strategy.variable_lit.values()))
        for nogood in nogoods:
            model.context.add_nogood(tuple(nogood))


def _has_value(variable: _ScalarVariable | _SetVariable | _MultimapVariable) -> bool:
    """Report whether a tracked variable has a selected scalar value.

    Collection variables always have a value, including when empty.

    Args:
        variable: Tracked scalar, set, or multimap variable.

    Returns:
        Whether the variable has a value in the current assignment.
    """
    return not isinstance(variable, _ScalarVariable) or variable.has_value
