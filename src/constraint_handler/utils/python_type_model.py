"""Core type-model structures used by Python statement analysis."""

from __future__ import annotations

from collections import namedtuple


class UnknownType:
    """Marker type used when expression type cannot be inferred."""


ListOf = namedtuple("ListOf", ["element_types"])
TupleOf = namedtuple("TupleOf", ["element_types"])
RepeatedTupleOf = namedtuple("RepeatedTupleOf", ["pattern_types"])
SetOf = namedtuple("SetOf", ["element_types"])
DictOf = namedtuple("DictOf", ["key_types", "value_types"])
ScalarType = namedtuple("ScalarType", ["typ"])
FunctionType = namedtuple("FunctionType", ["input_types", "return_types"])

TypeInfo = ScalarType | ListOf | TupleOf | RepeatedTupleOf | SetOf | DictOf | FunctionType | type[UnknownType]
_NONE_SCALAR = ScalarType(type(None))
_BOOL_SCALAR = ScalarType(bool)
_INT_SCALAR = ScalarType(int)
_FLOAT_SCALAR = ScalarType(float)
_STR_SCALAR = ScalarType(str)
