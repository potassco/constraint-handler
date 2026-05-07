from __future__ import annotations

import graphlib
from collections import defaultdict
from typing import NamedTuple

import clingo

import constraint_handler.multimap as multimap
import constraint_handler.schemas.expression as expression

# type ReducedExpr = expression.Val | frozenset[ReducedExpr] | refe | tuple[ReducedExpr, ...]


class Ref(NamedTuple):
    type_: expression.BaseType | clingo.Symbol
    expr: expression.Expr


class _set_contains(NamedTuple):
    expr: expression.Expr
    val: expression.Val | Ref


class _se_value(NamedTuple):
    expr: expression.Expr
    val: expression.Val | Ref


class PostProcessingPropagator(clingo.Propagator):
    def __init__(self) -> None:
        self._value_symbols: tuple[clingo.Symbol, ...] = ()
        self._set_contains_symbols: tuple[clingo.Symbol, ...] = ()
        self._optimize_symbols: tuple[clingo.Symbol, ...] = ()

    def init(self, init: clingo.PropagateInit) -> None:
        ### This can be sped up by sorting the symbols by variable
        ### and stopping after 1 value was found to be true per variable
        ### but therefore a cleaner encoding is needed,
        ### as sets and references etc... are mixed up

        self._value_symbols = tuple(
            symbolic_atom.symbol for symbolic_atom in init.symbolic_atoms.by_signature("_se_value", 2)
        )
        self._set_contains_symbols = tuple(
            symbolic_atom.symbol for symbolic_atom in init.symbolic_atoms.by_signature("_set_contains", 2)
        )
        self._optimize_symbols = tuple(
            symbolic_atom.symbol for symbolic_atom in init.symbolic_atoms.by_signature("_optimize_maximizeSum", 4)
        )

    def get_results(self, model) -> tuple[list[clingo.Symbol], list[clingo.Symbol], list[clingo.Symbol]]:
        return (
            [symbol for symbol in self._value_symbols if model.contains(symbol)],
            [symbol for symbol in self._set_contains_symbols if model.contains(symbol)],
            [symbol for symbol in self._optimize_symbols if model.contains(symbol)],
        )


def _unnest_symbol_list(symbol: clingo.Symbol) -> list[clingo.Symbol]:
    elements = []
    current = symbol
    while current.type == clingo.SymbolType.Function and current.name == "" and len(current.arguments) == 2:
        elements.append(current.arguments[0])
        current = current.arguments[1]
    assert current.type == clingo.SymbolType.Function and current.name == "" and len(current.arguments) == 0
    return elements


def _symbol_set_members(symbol: clingo.Symbol) -> set[clingo.Symbol]:
    assert symbol.match("set", 1)
    return set(_unnest_symbol_list(symbol.arguments[0]))


def _set_symbol(symbols: set[clingo.Symbol]) -> clingo.Symbol:
    nested = clingo.Function("", [])
    for symbol in reversed(list(frozenset(symbols))):
        nested = clingo.Function("", [symbol, nested])
    return clingo.Function("set", [nested])


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


def _set_valuation_from_results(
    model,
    value_results: list[clingo.Symbol],
    set_contains_results: list[clingo.Symbol],
    optimize_results: list[clingo.Symbol] | None = None,
) -> None:
    """Derives a valuation for the variables in the model from the results of the post-processing propagator.

    Collecting the values for single valued variables
    And the members of sets and multimaps in a way that respects dependencies between them.

    Assumptions could be simplified once all set variables have an _se_value(V,ref(...))
    and not _se_value(V,set(...)) is produced any longer by the ground engine.
    This would remove _symbol_set_members and simplify if not avoid the cycle check (removing self references)
    """
    vals = dict()
    mems = defaultdict(set)
    deps = defaultdict(set)

    # fill vals with explicit values or an empty set/dict
    for symbol in value_results:
        expr = symbol.arguments[0]
        value = symbol.arguments[1]
        assert value.type == clingo.SymbolType.Function
        match value.name:
            case "val":
                assert len(value.arguments) == 2
                vals[expr] = value
                vals[value] = value
            case "ref":
                assert len(value.arguments) == 2
                if value.arguments[0].match("set", 0):
                    vals[expr] = set()
                elif value.arguments[0].match("multimap", 0):
                    vals[expr] = dict()
                else:
                    raise NotImplementedError(f"unsupported _se_value reference: {symbol}")
            case "set":
                assert len(value.arguments) == 1
                vals[expr] = value
            case "bad":
                assert len(value.arguments) == 0
                vals[expr] = value
            case "":
                vals[expr] = clingo.Function("", list(value.arguments))
            case _:
                raise NotImplementedError(f"unsupported _se_value payload: {symbol}")

    # fill sets and dicts with their members and track references
    for symbol in set_contains_results:
        expr = symbol.arguments[0]
        value = symbol.arguments[1]
        assert value.type == clingo.SymbolType.Function
        assert len(value.arguments) == 2
        match value.name:
            case "ref":
                assert value.arguments[0].match("set", 0)
                ref_expr = value.arguments[1]
                vals.setdefault(expr, set())
                vals.setdefault(ref_expr, set())
                mems[ref_expr].add(expr)
                deps[expr].add(ref_expr)
            case "val":
                if expr not in vals:
                    vals[expr] = set()
                elif isinstance(vals[expr], clingo.Symbol) and vals[expr].match("set", 1):
                    vals[expr] = _symbol_set_members(vals[expr])
                vals[expr].add(value)
            case _:
                raise NotImplementedError(f"unsupported _set_contains payload: {symbol}")

    # resolve dependencies and convert sets and dicts to their final form
    graph = {expr: deps.get(expr, set()) for expr, value in vals.items() if isinstance(value, (set, dict))}
    ts = graphlib.TopologicalSorter(graph)
    try:
        ts.prepare()
    except graphlib.CycleError:
        pass
    while ts.is_active():
        for x in ts.get_ready():
            assert x in vals, f"{x},\n\n{vals}"
            if isinstance(vals[x], set):
                vals[x] = _set_symbol(vals[x])
            elif isinstance(vals[x], dict):
                vals[x] = multimap.HashableDict(vals[x])
            if x in mems:
                for s in mems[x]:
                    vals[s].add(vals[x])
            ts.done(x)
    for x in list(vals):
        if isinstance(vals[x], set):
            vals[x] = _set_symbol(vals[x])
        elif isinstance(vals[x], dict):
            vals[x] = multimap.HashableDict(vals[x])
    clVals = []
    for expr, value in vals.items():
        if expr.type != clingo.SymbolType.Function or expr.name != "variable":
            continue
        assert len(expr.arguments) == 1
        variable = expr.arguments[0]
        clVals.append(clingo.Function("value", [variable, value]))
    model.extend(clVals)

    none_value = clingo.Function("val", [clingo.Function("none"), clingo.Function("none")])
    totals: dict[tuple[clingo.Symbol, clingo.Symbol], int | float] = {}
    float_totals: set[tuple[clingo.Symbol, clingo.Symbol]] = set()
    for symbol in [] if optimize_results is None else optimize_results:
        label, expr, _, priority = symbol.arguments
        key = (label, priority)
        value = vals.get(expr, none_value)

        value_type = value.arguments[0]
        payload = value.arguments[1]
        if value_type.match("none", 0):
            amount = 0
        elif value_type.match("int", 0):
            amount = payload.number
        elif value_type.match("float", 0):
            assert payload.type == clingo.SymbolType.Function and payload.match("float", 1)
            amount = float(payload.arguments[0].string)
            float_totals.add(key)
        else:
            raise NotImplementedError(f"unsupported optimize value type: {value}")

        totals[key] = totals.get(key, 0) + amount

    model.extend(
        [
            clingo.Function("value", [label, _numeric_value_symbol(total, key in float_totals)])
            for key, total in totals.items()
            for label, priority in [key]
        ]
    )


def set_valuation(ctrl, model) -> None:
    value_results, set_contains_results, optimize_results = (
        ctrl.constraint_handler_post_processing_propagator.get_results(model)
    )
    _set_valuation_from_results(model, value_results, set_contains_results, optimize_results)
