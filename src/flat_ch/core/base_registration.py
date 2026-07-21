from __future__ import annotations

from functools import lru_cache
from typing import Any

import clingo

from flat_ch.core.evaluation.operators import Operator
from flat_ch.core.serialization import SerializerProtocol
from flat_ch.core.types import Type

_ASP_NAME_TO_OPERATOR = {op.asp_name: op for op in Operator}


def parse_operator(operator_symbol: clingo.Symbol) -> Operator | str:
    try:
        args = operator_symbol.arguments
        if not args:
            op_name = operator_symbol.name
            return _ASP_NAME_TO_OPERATOR.get(op_name, op_name)
    except (AttributeError, RuntimeError):
        pass
    return BaseRegistration.to_str(operator_symbol)


def parse_python_operator(operator_symbol: clingo.Symbol) -> str | None:
    try:
        if operator_symbol.name == "python":
            args = operator_symbol.arguments
            if len(args) == 1:
                payload = args[0]
                if payload.type == clingo.SymbolType.String:
                    return payload.string
                raise ValueError(f"Unsupported python operator payload: {operator_symbol}")
    except (AttributeError, RuntimeError):
        pass
    return None


class BaseRegistration:
    """Shared low-level symbol and value utilities used by registrations."""

    def __init__(self, serializer: SerializerProtocol) -> None:
        self._serializer = serializer

    @staticmethod
    @lru_cache(maxsize=10240)
    def to_str(symbol: clingo.Symbol) -> str:
        sym_type = symbol.type
        if sym_type == clingo.SymbolType.String:
            return symbol.string
        if sym_type == clingo.SymbolType.Number:
            return str(symbol.number)
        if sym_type == clingo.SymbolType.Function:
            args = symbol.arguments
            if not args:
                return symbol.name

            rendered_args = ",".join(BaseRegistration.to_str(arg) for arg in args)
            name = symbol.name
            if not name:
                return f"({rendered_args})"
            return f"{name}({rendered_args})"

        return str(symbol)

    @staticmethod
    def unnest(symbol: clingo.Symbol) -> list[clingo.Symbol]:
        items = []
        while symbol.type == clingo.SymbolType.Function and symbol.name == "":
            args = symbol.arguments
            if len(args) != 2:
                items.extend(args)
                return items
            items.append(args[0])
            symbol = args[1]

        if symbol.type != clingo.SymbolType.Function or symbol.name != "()":
            items.append(symbol)
        return items

    def scalar_value(self, symbol: clingo.Symbol) -> Any:
        sym_type = symbol.type
        if sym_type == clingo.SymbolType.Number:
            return symbol.number
        if sym_type == clingo.SymbolType.String:
            return symbol.string
        if sym_type == clingo.SymbolType.Infimum:
            return "#inf"
        if sym_type == clingo.SymbolType.Supremum:
            return "#sup"

        if sym_type == clingo.SymbolType.Function:
            args = symbol.arguments
            if not args:
                return symbol.name

        return str(symbol)

    def cast_runtime_value(self, type_hint: Type, val_sym: clingo.Symbol) -> Any:
        sym_type = val_sym.type
        if sym_type == clingo.SymbolType.Number:
            return val_sym.number
        if sym_type == clingo.SymbolType.String:
            return val_sym.string

        wrapped_value = clingo.Function("", [clingo.Number(type_hint.value), val_sym])
        return self._serializer.clingo_to_python(wrapped_value)[1]
