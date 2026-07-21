from __future__ import annotations

import math
from typing import Any, Protocol

from clingo import Function, Number, String, Symbol
from clingo.symbol import SymbolType

from flat_ch.core.types import Type

_FLOAT_EPSILON = 1e-9
_FLOAT_DECIMALS = 9

_SYM_TRUE = Function("true", [])
_SYM_FALSE = Function("false", [])
_SYM_NONE = Function("none", [])
_SYM_EMPTY_TUPLE = Function("()", [])

_TYPE_NUMBER_SYMBOLS: dict[Type, Symbol] = {t: Number(t.value) for t in Type}

_BOOL_MAP = {"true": True, "false": False}


def normalize_float_str(value: float | int) -> str:
    """Normalizes floating-point numbers into a consistent string representation."""
    numeric = float(value)
    if math.isfinite(numeric):
        numeric = round(numeric, _FLOAT_DECIMALS)
        nearest_int = round(numeric)
        if abs(numeric - nearest_int) <= _FLOAT_EPSILON:
            numeric = float(nearest_int)
    if numeric == 0.0:
        numeric = 0.0
    return repr(numeric)


def infer_python_type(value: Any) -> Type:
    """Infers the corresponding IR Type enum for a given Python primitive."""
    if value is None:
        return Type.NONE
    val_type = type(value)
    if val_type is bool:
        return Type.BOOL
    if val_type is int:
        return Type.INT
    if val_type is float:
        return Type.FLOAT
    if val_type is set or val_type is frozenset:
        return Type.SET
    return Type.STRING


class SerializerProtocol(Protocol):
    """Protocol for converting between Clingo Symbols and Python IR values."""

    def clingo_to_python(self, clingo_symbol: Symbol) -> tuple[Type, Any]: ...
    def python_to_clingo(self, type_id: Type, value: Any) -> Symbol: ...


class BaseSerializer:
    """Shared internal serializer for flattened CH values with pre-cached Cffi symbols."""

    def clingo_to_python(self, clingo_symbol: Symbol) -> tuple[Type, Any]:
        args = clingo_symbol.arguments
        type_id = Type(args[0].number)
        val_sym = args[1]

        match type_id:
            case Type.NONE:
                return type_id, None
            case Type.INT:
                return type_id, val_sym.number
            case Type.FLOAT:
                if val_sym.type == SymbolType.Number:
                    return type_id, float(val_sym.number)
                return type_id, float(val_sym.string)
            case Type.BOOL:
                return type_id, _BOOL_MAP.get(val_sym.name, False)
            case Type.SET:
                return type_id, self._deserialize_set(val_sym)
            case Type.FAIL | Type.STRING:
                return type_id, val_sym.string
            case _:
                return type_id, val_sym.string

    def python_to_clingo(self, type_id: Type, value: Any) -> Symbol:
        type_num_sym = _TYPE_NUMBER_SYMBOLS.get(type_id) or Number(type_id.value)

        match type_id:
            case Type.NONE:
                return Function("", [type_num_sym, _SYM_NONE])
            case Type.BOOL:
                inner = _SYM_TRUE if value else _SYM_FALSE
                return Function("", [type_num_sym, inner])
            case Type.INT:
                return Function("", [type_num_sym, Number(int(value))])
            case Type.FLOAT:
                return Function("", [type_num_sym, String(normalize_float_str(value))])
            case Type.FAIL | Type.STRING:
                return Function("", [type_num_sym, String(str(value))])
            case Type.SET:
                return Function("", [type_num_sym, self._serialize_set(value)])
            case _:
                return Function("", [type_num_sym, String(str(value))])

    def _deserialize_set(self, list_node: Symbol) -> frozenset[Any]:
        members = []
        curr = list_node
        while curr.type == SymbolType.Function:
            args = curr.arguments
            if len(args) != 2:
                break
            members.append(self.clingo_to_python(args[0])[1])
            curr = args[1]
        return frozenset(members)

    def _serialize_set(self, py_set: set | frozenset) -> Symbol:
        list_node = _SYM_EMPTY_TUPLE
        try:
            sorted_elems = sorted(py_set)
        except TypeError:
            sorted_elems = list(py_set)

        for elem in reversed(sorted_elems):
            elem_type = infer_python_type(elem)
            elem_wrap = self.python_to_clingo(elem_type, elem)
            list_node = Function("", [elem_wrap, list_node])
        return list_node
