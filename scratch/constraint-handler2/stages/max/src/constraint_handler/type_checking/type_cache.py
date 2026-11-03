"""Immutable result types and session-local, binding-aware memoization."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Final, final

from ..internal_input import ConstraintStore, Expr, ValueType, VariableRef


@dataclass(frozen=True, slots=True)
class SetOf:
    """Describe a flat set's possible scalar members and emptiness."""

    elements: frozenset[ValueType]
    can_be_empty: bool


@dataclass(frozen=True, slots=True)
class TupleType:
    """Describe a flat tuple using one result type per position."""

    elements: tuple[Type, ...]


@final
@dataclass(frozen=True, slots=True)
class UnknownType:
    """Represent unavailable result-type information."""

    def __new__(cls) -> UnknownType:
        """Return the immutable shared unknown marker."""
        return UNKNOWN


UNKNOWN: Final = object.__new__(UnknownType)

type TypeMember = ValueType | SetOf | TupleType
type Type = frozenset[TypeMember] | UnknownType
type TypeScope = frozenset[tuple[VariableRef, Type]]


def union_types(types: Iterable[Type]) -> Type:
    """Union alternatives, merging set members and absorbing unknown inputs."""
    members: set[TypeMember] = set()
    set_elements: set[ValueType] = set()
    has_set = False
    set_can_be_empty = False
    for kind in types:
        if isinstance(kind, UnknownType):
            return UNKNOWN
        for member in kind:
            if isinstance(member, SetOf):
                has_set = True
                set_elements.update(member.elements)
                set_can_be_empty |= member.can_be_empty
            else:
                members.add(member)
    if has_set:
        members.add(SetOf(frozenset(set_elements), set_can_be_empty))
    return frozenset(members)


class TypeCache:
    """Memoize result types without validating expressions or executing input."""

    def __init__(self, store: ConstraintStore) -> None:
        """Own one stable store typing context for a preprocessing session."""
        from ._type_inference import _TypeInference

        self._entries: dict[tuple[Expr, TypeScope], Type] = {}
        self._computing: set[tuple[Expr, TypeScope]] = set()
        self._inference = _TypeInference(self, store)

    def get_type(
        self, expr: Expr, bindings: Mapping[VariableRef, Type] | None = None
    ) -> Type:
        """Return or infer a result type in an immutable snapshot of the bindings."""
        scope: TypeScope = frozenset(bindings.items()) if bindings else frozenset()
        key = (expr, scope)
        if key in self._entries:
            return self._entries[key]
        if key in self._computing:
            return UNKNOWN
        self._computing.add(key)
        try:
            result = self._inference.compute(expr, dict(scope))
            self.set_type(expr, result, dict(scope))
            return result
        finally:
            self._computing.remove(key)

    def set_type(
        self,
        expr: Expr,
        known_type: Type,
        bindings: Mapping[VariableRef, Type] | None = None,
    ) -> None:
        """Trust a supplied type, rejecting conflicting writes to an existing key."""
        scope: TypeScope = frozenset(bindings.items()) if bindings else frozenset()
        key = (expr, scope)
        if key in self._entries and self._entries[key] != known_type:
            raise ValueError("A different type is already cached for this expression")
        self._entries[key] = known_type
