from __future__ import annotations

from typing import Any

from clingo import Function, Number, String, Symbol
from clingo.symbol import SymbolType

from flat_ch.core.serialization import BaseSerializer, normalize_float_str
from flat_ch.core.types import Type


class CHSerializer(BaseSerializer):
    """Legacy CH dialect serializer: Floats wrapped in float(...) function terms."""

    def clingo_to_python(self, clingo_symbol: Symbol) -> tuple[Type, Any]:
        args = clingo_symbol.arguments
        type_id = Type(args[0].number)
        val_sym = args[1]

        if type_id == Type.FLOAT:
            if val_sym.type == SymbolType.Function and val_sym.name == "float" and len(val_sym.arguments) == 1:
                wrapped = val_sym.arguments[0]
                if wrapped.type == SymbolType.Number:
                    return type_id, float(wrapped.number)
                return type_id, float(wrapped.string)
            if val_sym.type == SymbolType.Number:
                return type_id, float(val_sym.number)
            return type_id, float(val_sym.string)

        return super().clingo_to_python(clingo_symbol)

    def python_to_clingo(self, type_id: Type, value: Any) -> Symbol:
        if type_id == Type.FLOAT:
            inner = Function("float", [String(normalize_float_str(value))])
            return Function("", [Number(type_id.value), inner])

        return super().python_to_clingo(type_id, value)
