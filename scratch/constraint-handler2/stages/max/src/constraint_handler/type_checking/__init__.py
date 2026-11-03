"""Result-type caching and independent static validation."""

from .type_cache import (
    UNKNOWN,
    SetOf,
    TupleType,
    Type,
    TypeCache,
    TypeMember,
    TypeScope,
    UnknownType,
    union_types,
)
from .type_checker import TypeChecker

__all__ = [
    "UNKNOWN",
    "SetOf",
    "TupleType",
    "Type",
    "TypeCache",
    "TypeChecker",
    "TypeMember",
    "TypeScope",
    "UnknownType",
    "union_types",
]
