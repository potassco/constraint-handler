from __future__ import annotations

from collections import defaultdict
from typing import Mapping

import clingo

import constraint_handler.evaluator as evaluator
import constraint_handler.myClorm as myClorm
import constraint_handler.schemas.atom as atom
import constraint_handler.schemas.warning as warning


class OptimizePostProcessingPropagator(clingo.Propagator):
    def __init__(self) -> None:
        self._optimize_symbols: list[clingo.Symbol] = []
        self._value_symbols_by_expr: defaultdict[clingo.Symbol, list[clingo.Symbol]] = defaultdict(list)
        self._cached_optimize_value_symbols: list[clingo.Symbol] | None = None
        self._last_optimize_value_symbols: list[clingo.Symbol] | None = None

    def init(self, init: clingo.PropagateInit) -> None:
        self.reset_optimize_value_symbols()
        self._optimize_symbols = [
            symbolic_atom.symbol for symbolic_atom in init.symbolic_atoms.by_signature("_optimize_component", 5)
        ]
        optimize_exprs = {
            expr for symbol in self._optimize_symbols for expr in (symbol.arguments[1], symbol.arguments[2])
        }

        self._value_symbols_by_expr.clear()
        for symbolic_atom in init.symbolic_atoms.by_signature("_shared_value", 2):
            symbol = symbolic_atom.symbol
            expr = symbol.arguments[0]
            if expr in optimize_exprs:
                self._value_symbols_by_expr[expr].append(symbol)

    def reset_optimize_value_symbols(self) -> None:
        self._cached_optimize_value_symbols = None
        self._last_optimize_value_symbols = None

    def get_results(self, model) -> tuple[dict[clingo.Symbol, int | float], list[clingo.Symbol]]:
        values = {}
        for optimize_symbol in self._optimize_symbols:
            _, value_expr, precision_expr, _, _ = optimize_symbol.arguments

            for expr in (value_expr, precision_expr):
                if expr in values:
                    continue
                for value_symbol in self._value_symbols_by_expr.get(expr, []):
                    if model.contains(value_symbol):
                        values[expr] = _to_number(value_symbol.arguments[1])
                        break
                for atom in model.symbols(theory=True):
                    if atom.name == "_shared_value" and len(atom.arguments) == 2:
                        if atom.arguments[0] == expr:
                            values[expr] = _to_number(atom.arguments[1])

        return values, self._optimize_symbols


def _to_number(value: clingo.Symbol) -> int | float:
    if value.name == "val" and len(value.arguments) == 2:
        value_type = value.arguments[0]
        payload = value.arguments[1]
        if value_type.match("int", 0):
            return payload.number
        if value_type.match("bool", 0):
            return int(payload.match("true", 0))
        if value_type.match("float", 0):
            assert payload.type == clingo.SymbolType.Function and payload.match("float", 1)
            return float(payload.arguments[0].string)
    if value.name == "bad" and len(value.arguments) == 0:
        return 0
    raise NotImplementedError(f"unsupported optimize value type: {value}")


def _extend_optimize_values(
    values: Mapping[clingo.Symbol, int | float],
    optimize_results: list[clingo.Symbol] | None = None,
) -> list[clingo.Symbol]:

    results = []
    totals: dict[tuple[clingo.Symbol, clingo.Symbol], int | float] = {}
    for symbol in [] if optimize_results is None else optimize_results:
        label, expr, precision_expr, _, priority = symbol.arguments

        key = (label, priority)
        value = values.get(expr, 0)
        if expr not in values:
            results.append(
                warning.Warning(warning.OtherError(), (), f"no value computed for {expr} used in optimization")
            )
        precision = values.get(precision_expr, 1)
        if precision_expr not in values:
            results.append(
                warning.Warning(
                    warning.OtherError(), (), f"no value computed for {precision_expr} used in optimization"
                )
            )
        amount = value / precision if precision != 1 else value

        totals[key] = totals.get(key, 0) + amount

    for key, total in totals.items():
        label, priority = key
        cTotal, errors = evaluator.reducedExpr(total)
        results.append(atom.Optimize_value(label, priority, cTotal))
        results.extend(errors)
    return [myClorm.pytocl(atom) for atom in results]


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
