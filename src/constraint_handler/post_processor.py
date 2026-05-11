from __future__ import annotations

from collections import defaultdict
from typing import Mapping, NamedTuple

import clingo

import constraint_handler.schemas.expression as expression
import constraint_handler.schemas.type_ as type_


class Ref(NamedTuple):
    type_: type_.BaseType | clingo.Symbol
    expr: expression.Expr


class _set_contains(NamedTuple):
    expr: expression.Expr
    val: expression.Val | Ref


class _se_value(NamedTuple):
    expr: expression.Expr
    val: expression.Val | Ref


class OptimizePostProcessingPropagator(clingo.Propagator):
    def __init__(self) -> None:
        self._optimize_symbols: list[clingo.Symbol] = []
        self._value_symbols_by_expr: defaultdict[clingo.Symbol, list[clingo.Symbol]] = defaultdict(list)
        self._cached_optimize_value_symbols: list[clingo.Symbol] | None = None
        self._last_optimize_value_symbols: list[clingo.Symbol] | None = None

    def init(self, init: clingo.PropagateInit) -> None:
        self.reset_optimize_value_symbols()
        self._optimize_symbols = [
            symbolic_atom.symbol for symbolic_atom in init.symbolic_atoms.by_signature("_optimize_maximizeSum", 4)
        ]
        optimize_exprs = {symbol.arguments[1] for symbol in self._optimize_symbols}

        self._value_symbols_by_expr.clear()
        for symbolic_atom in init.symbolic_atoms.by_signature("_se_value", 2):
            symbol = symbolic_atom.symbol
            expr = symbol.arguments[0]
            if expr in optimize_exprs:
                self._value_symbols_by_expr[expr].append(symbol)

    def reset_optimize_value_symbols(self) -> None:
        self._cached_optimize_value_symbols = None
        self._last_optimize_value_symbols = None

    def get_results(self, model) -> tuple[dict[clingo.Symbol, clingo.Symbol], list[clingo.Symbol]]:
        values = {}
        for optimize_symbol in self._optimize_symbols:
            expr = optimize_symbol.arguments[1]
            if expr in values:
                continue
            for value_symbol in self._value_symbols_by_expr.get(expr, []):
                if model.contains(value_symbol):
                    values[expr] = value_symbol.arguments[1]
                    break

        return values, self._optimize_symbols


def _numeric_value_symbol(total: int | float, uses_float: bool) -> clingo.Symbol:
    """returns a clingo Symbol or either an int or float"""
    if uses_float:
        return clingo.Function(
            "val",
            [
                clingo.Function("float"),
                clingo.Function("float", [clingo.String(str(total))]),
            ],
        )
    return clingo.Function("val", [clingo.Function("int"), clingo.Number(int(total))])


def _extend_optimize_values(
    values: Mapping[clingo.Symbol, clingo.Symbol],
    optimize_results: list[clingo.Symbol] | None = None,
) -> list[clingo.Symbol]:
    none_value = clingo.Function("val", [clingo.Function("none"), clingo.Function("none")])
    totals: dict[tuple[clingo.Symbol, clingo.Symbol], int | float] = {}
    float_totals: set[tuple[clingo.Symbol, clingo.Symbol]] = set()
    for symbol in [] if optimize_results is None else optimize_results:
        label, expr, _, priority = symbol.arguments
        key = (label, priority)
        value = values.get(expr, none_value)

        value_type = value.arguments[0]
        payload = value.arguments[1]
        if value_type.match("none", 0):
            amount = 0
        elif value_type.match("int", 0):
            amount = payload.number
        elif value_type.match("bool", 0):
            amount = int(payload.match("true", 0))
        elif value_type.match("float", 0):
            assert payload.type == clingo.SymbolType.Function and payload.match("float", 1)
            amount = float(payload.arguments[0].string)
            float_totals.add(key)
        else:
            raise NotImplementedError(f"unsupported optimize value type: {value}")

        totals[key] = totals.get(key, 0) + amount

    return [
        clingo.Function("optimize_value", [label, priority, _numeric_value_symbol(total, key in float_totals)])
        for key, total in totals.items()
        for label, priority in [key]
    ]


def set_optimize_valuation(propagator: OptimizePostProcessingPropagator, model) -> None:
    if propagator._cached_optimize_value_symbols is not None:
        model.extend(propagator._cached_optimize_value_symbols)
        return

    values, optimize_results = propagator.get_results(model)
    optimize_value_symbols = _extend_optimize_values(values, optimize_results)

    # Brave/cautious consequence models can no longer be trusted to reconstruct per-label
    # optimize totals from their remaining expression values. Freeze the optimize values from
    # the immediately preceding stable model instead.
    if (
        model.optimality_proven
        and model.type in {clingo.ModelType.BraveConsequences, clingo.ModelType.CautiousConsequences}
        and propagator._last_optimize_value_symbols is not None
    ):
        optimize_value_symbols = propagator._last_optimize_value_symbols.copy()

    model.extend(optimize_value_symbols)
    propagator._last_optimize_value_symbols = optimize_value_symbols.copy()

    if model.optimality_proven:
        propagator._cached_optimize_value_symbols = optimize_value_symbols.copy()
