"""Core type-model structures used by Python statement analysis."""

from __future__ import annotations

from enum import Enum
from typing import NamedTuple

import clingo


class UnknownType:
    """Marker type used when expression type cannot be inferred."""


class UnsupportedType:
    """Marker type used when expression type is outside supported model types."""


class ListOf(NamedTuple):
    element_types: TypeInfo


class TupleOf(NamedTuple):
    element_types: tuple[TypeInfo, ...]


class RepeatedTupleOf(NamedTuple):
    element_type: TypeInfo


class SetOf(NamedTuple):
    element_types: TypeInfo


class DictOf(NamedTuple):
    key_types: TypeInfo
    value_types: TypeInfo


class Scalar(Enum):
    NONE = type(None)
    BOOL = bool
    INT = int
    FLOAT = float
    STRING = str
    SYMBOL = clingo.Symbol


class FunctionType(NamedTuple):
    input_types: tuple[TypeInfo, ...] | None
    return_type: TypeInfo


TypeInfo = (
    Scalar
    | ListOf
    | TupleOf
    | RepeatedTupleOf
    | SetOf
    | DictOf
    | FunctionType
    | type[UnknownType]
    | type[UnsupportedType]
)
