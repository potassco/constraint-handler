"""Build a ground ASP fact base from a dispatched constraint store."""

import math
from collections.abc import Iterator, Mapping
from itertools import pairwise, product
from typing import assert_never, cast

from clingo.core import Library
from clingo.symbol import Function, Number, String, Symbol, Tuple_

from .dispatching import DispatchStore, Engine
from .domains import DomainStore
from .domains.values import is_domain_value, is_finite_value
from .internal_input import (
    ConstraintStore,
    Expr,
    Lambda,
    Operation,
    OperationArg,
    ValueDef,
    ValueType,
    Variable,
    _convert_expression,
)
from .python_input import FailIntegrityExn, Operator, Python, VariableRef


def _number(lib: Library, value: int) -> Symbol:
    """Reject integers that Clingo would otherwise silently wrap."""
    if not -(2**31) <= value < 2**31:
        raise ValueError("ASP integer literals must fit in a signed 32-bit integer")
    return Number(lib, value)


def _is_constant(expr: OperationArg) -> bool:
    """Recognize scalar values and collections containing only constant values."""
    if isinstance(expr, (tuple, frozenset)):
        return all(_is_constant(item) for item in expr)
    return isinstance(expr, ValueDef)


def _constant_subterms(expr: OperationArg) -> Iterator[OperationArg]:
    """Yield every constant subterm, including operands nested inside operations."""
    if _is_constant(expr):
        yield expr
    children: tuple[OperationArg, ...]
    match expr:
        case Operation(_, args):
            children = args
        case tuple() | frozenset():
            children = tuple(expr)
        case _:
            return
    for child in children:
        yield from _constant_subterms(child)


def _term(lib: Library, expr: OperationArg) -> Symbol:
    """Encode an expression without conflating scalar types or evaluating it."""
    match expr:
        case ValueDef(ValueType.none, _):
            return Function(lib, "none")
        case ValueDef(ValueType.boolean, value):
            return Function(
                lib, "boolean", [Function(lib, "true" if value else "false")]
            )
        case ValueDef(ValueType.integer, int(value)):
            return Function(lib, "integer", [_number(lib, value)])
        case ValueDef(ValueType.real, float(value)):
            return Function(lib, "real", [String(lib, repr(value))])
        case ValueDef(ValueType.string, str(value)):
            return Function(lib, "string", [String(lib, value)])
        case ValueDef():
            raise TypeError("scalar value does not match its declared type")
        case VariableRef(name):
            return Function(lib, "variable", [String(lib, name)])
        case tuple():
            return Function(
                lib, "tuple", [Tuple_(lib, [_term(lib, item) for item in expr])]
            )
        case frozenset():
            return Function(
                lib, "set", [Tuple_(lib, sorted(_term(lib, item) for item in expr))]
            )
        case Operation(op, args):
            return Function(
                lib,
                "operation",
                [
                    Function(lib, op.value),
                    Tuple_(lib, [_term(lib, arg) for arg in args]),
                ],
            )
        case Python(source):
            return Function(lib, "python", [String(lib, source)])
        case Lambda():
            raise TypeError("ASP facts require lambda conversion before dispatch")
    assert_never(expr)


def _complex_facts(
    lib: Library,
    store: ConstraintStore,
    engines: DispatchStore,
    domains: DomainStore,
    python_context: Mapping[str, object],
) -> Iterator[Symbol]:
    """Enumerate Python calls with exact scalar and set input/output rows."""
    solution_id = 0
    for expr_id, expr in sorted(store.expressions.items()):
        if engines[expr_id] != Engine.complex:
            continue
        if not (
            isinstance(expr, Operation)
            and expr.op == Operator.python_eval
            and isinstance(expr.args[0], Python)
        ):
            raise TypeError("complex evaluation requires a converted Python call")
        arguments = cast(tuple[OperationArg, ...], expr.args[1:])
        argument_domains = [domains[cast(Expr, arg)] for arg in arguments]
        if any(domain.unknown for domain in argument_domains):
            raise ValueError("complex evaluation requires known input domains")
        callback: object = eval(expr.args[0].fn, {"math": math, **python_context})
        if not callable(callback):
            raise TypeError("Python source must evaluate to a callable")
        axes = [
            sorted(
                domain.iter_values(),
                key=lambda value: (type(value).__name__, repr(value)),
            )
            for domain in argument_domains
        ]
        for values in product(*axes):
            try:
                result = callback(*values)
            except FailIntegrityExn:
                continue
            except ArithmeticError, LookupError, TypeError, ValueError:
                continue
            if isinstance(result, set):
                result = frozenset(result)
            if not is_domain_value(result):
                raise TypeError(
                    f"unsupported Python result type: {type(result).__name__}"
                )
            if not is_finite_value(result) or not all(
                is_finite_value(value) for value in values
            ):
                raise ValueError("complex evaluation requires finite values")
            solution = _number(lib, solution_id)
            yield Function(lib, "solution", [_number(lib, expr_id), solution])
            for arg, value, domain in zip(
                arguments, values, argument_domains, strict=True
            ):
                argument = _term(lib, arg)
                yield Function(
                    lib,
                    "input",
                    [
                        solution,
                        argument,
                        Function(lib, "set")
                        if isinstance(value, frozenset)
                        else _term(lib, _convert_expression(value)),
                    ],
                )
                if isinstance(value, frozenset):
                    included = {_term(lib, _convert_expression(item)) for item in value}
                    universe = {
                        _term(lib, _convert_expression(item))
                        for item in domain.potential_set_members()
                    }
                    for predicate, members in (
                        ("set_input_include", included),
                        ("set_input_exclude", universe - included),
                    ):
                        for member in sorted(members):
                            yield Function(lib, predicate, [solution, argument, member])
            yield Function(
                lib,
                "output",
                [
                    solution,
                    Function(lib, "set")
                    if isinstance(result, frozenset)
                    else _term(lib, _convert_expression(result)),
                ],
            )
            if isinstance(result, frozenset):
                for member in sorted(
                    _term(lib, _convert_expression(item)) for item in result
                ):
                    yield Function(lib, "set_output", [solution, member])
            solution_id += 1


def asp_facts(
    lib: Library,
    store: ConstraintStore,
    engines: DispatchStore,
    domains: DomainStore | None = None,
    python_context: Mapping[str, object] | None = None,
) -> tuple[Symbol, ...]:
    """Return ground facts retaining every declaration, expression, and engine assignment."""
    if engines.keys() != store.expressions.keys():
        raise ValueError("dispatch must classify exactly the stored expression IDs")
    facts: list[Symbol] = [
        Function(lib, "set_variable", [String(lib, variable.name)])
        for variable in store.set_variables
    ]
    for variables, predicates in (
        (
            store.variables,
            ("variable_choose", "variable_define", "variable_default_to"),
        ),
        (
            store.set_variables,
            ("set_contain_choose", "set_contain", "set_contain_default_to"),
        ),
    ):
        for variable, entries in variables.items():
            if isinstance(entries, Variable):
                choices, definitions = entries.choices, entries.definitions
            else:
                choices, definitions = entries.bases, entries.assigns
            for predicate, records in (
                (predicates[0], choices),
                (predicates[1], definitions),
            ):
                facts.extend(
                    Function(
                        lib,
                        predicate,
                        [
                            String(lib, variable.name),
                            _number(lib, entry.value),
                            _number(lib, entry.condition),
                            String(lib, entry.label),
                        ],
                    )
                    for entry in records
                )
            facts.extend(
                Function(
                    lib,
                    predicates[2],
                    [
                        String(lib, variable.name),
                        _number(lib, entry.value),
                        _number(lib, entry.condition),
                        _number(lib, entry.priority),
                        String(lib, entry.label),
                    ],
                )
                for entry in entries.defaults
            )
    facts.extend(
        Function(
            lib,
            "check" if constraint.is_check else "ensure",
            [_number(lib, constraint.expr), String(lib, constraint.label)],
        )
        for constraint in store.constraints
    )
    constants = {
        _term(lib, subterm)
        for expr in store.expressions.values()
        for subterm in _constant_subterms(expr)
    }
    facts.extend(Function(lib, "constant", [term]) for term in sorted(constants))
    facts.extend(
        Function(lib, "constant_set_value", [term, member])
        for term in sorted(constants)
        if term.name == "set"
        for member in term.arguments[0].arguments
    )
    order_minima: dict[Expr, int | None] = {}
    for expr_id, expr in sorted(store.expressions.items()):
        facts.append(Function(lib, "expr", [_number(lib, expr_id), _term(lib, expr)]))
        facts.append(
            Function(
                lib,
                "engine",
                [Function(lib, engines[expr_id].value), _number(lib, expr_id)],
            )
        )
        if (
            engines[expr_id] == Engine.native
            and isinstance(expr, Operation)
            and expr.op in {Operator.conj, Operator.disj, Operator.set_make}
        ):
            facts.extend(
                Function(
                    lib,
                    "set_argument"
                    if expr.op == Operator.set_make
                    else "boolean_argument",
                    [_number(lib, expr_id), _term(lib, arg)],
                )
                for arg in expr.args
            )
        if (
            engines[expr_id] == Engine.native
            and isinstance(expr, Operation)
            and expr.op == Operator.leqv
        ):
            facts.extend(
                Function(
                    lib,
                    "boolean_equivalence_argument",
                    [_number(lib, expr_id), _number(lib, index), _term(lib, arg)],
                )
                for index, arg in enumerate(expr.args)
            )
        if (
            engines[expr_id] == Engine.native
            and isinstance(expr, Operation)
            and expr.op in {Operator.linear_integer, Operator.linear_comparison}
        ):
            comparison = expr.op == Operator.linear_comparison
            pairs = expr.args[1:-1] if comparison else expr.args[:-1]
            facts.append(
                Function(
                    lib,
                    "linear_comparison_relation"
                    if comparison
                    else "linear_integer_offset",
                    [
                        _number(lib, expr_id),
                        _term(lib, expr.args[0] if comparison else expr.args[-1]),
                    ],
                )
            )
            baseline: int | None = cast(int, cast(ValueDef, expr.args[-1]).value)
            for index, pair in enumerate(pairs):
                coefficient, argument = cast(tuple[ValueDef, Expr], pair)
                facts.append(
                    Function(
                        lib,
                        "linear_integer_term",
                        [
                            _number(lib, expr_id),
                            _number(lib, index),
                            _term(lib, coefficient),
                            _term(lib, argument),
                        ],
                    )
                )
                if not comparison and len(pairs) == 1:
                    continue
                if argument not in order_minima:
                    if isinstance(argument, ValueDef):
                        values = [cast(int, argument.value)]
                    elif domains is None:
                        raise ValueError("native multi-term sums require input domains")
                    else:
                        domain = domains[argument]
                        if domain.unknown:
                            raise ValueError(
                                "native order encoding requires known domains"
                            )
                        values = sorted(domain.iter_ints())
                    order_minima[argument] = values[0] if values else None
                    if values:
                        facts.append(
                            Function(
                                lib,
                                "order_min",
                                [_term(lib, argument), _number(lib, values[0])],
                            )
                        )
                    facts.extend(
                        Function(
                            lib,
                            "order_next",
                            [
                                _term(lib, argument),
                                _number(lib, lower),
                                _number(lib, upper),
                            ],
                        )
                        for lower, upper in pairwise(values)
                    )
                minimum = order_minima[argument]
                baseline = (
                    baseline + cast(int, coefficient.value) * minimum
                    if baseline is not None and minimum is not None
                    else None
                )
            if (comparison or len(pairs) != 1) and baseline is not None:
                facts.append(
                    Function(
                        lib,
                        "linear_comparison_base"
                        if comparison
                        else "linear_integer_base",
                        [_number(lib, expr_id), _number(lib, baseline)],
                    )
                )
    if domains is not None:
        facts.extend(_complex_facts(lib, store, engines, domains, python_context or {}))
    return tuple(facts)
