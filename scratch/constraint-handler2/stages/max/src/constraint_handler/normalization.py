"""Normalize arithmetic in a constraint store while retaining expression IDs."""

from typing import cast

from .internal_input import (
    ConstraintStore,
    Expr,
    Lambda,
    Operation,
    OperationArg,
    Python,
    ValueDef,
    ValueType,
    VariableRef,
)
from .python_input import Operator
from .static_types import StaticTypeStore, UnknownType

_NUMERIC = frozenset({ValueType.integer})
_RELATIONS = frozenset({Operator.eq, Operator.neq, Operator.lt, Operator.leq, Operator.gt, Operator.geq})
_ARITHMETIC = frozenset({Operator.add, Operator.sub, Operator.minus, Operator.mult})
_ZERO = ValueDef(ValueType.integer, 0)


class _Normalizer:
    """Rewrite integer expressions using the previously computed variable types."""

    def __init__(self, static_types: StaticTypeStore) -> None:
        """Retain type information used to guard arithmetic rewrites."""
        self._types = static_types

    def is_numeric(self, expr: OperationArg, bound: frozenset[VariableRef]) -> bool:
        """Prove integer inputs conservatively, without assuming callable results."""
        match expr:
            case ValueDef(kind, _):
                return kind in _NUMERIC
            case VariableRef():
                if expr in bound:
                    return False
                known = self._types.get(expr, UnknownType())
                return not isinstance(known, UnknownType) and bool(known) and known <= _NUMERIC
            case Operation(Operator.linear_integer, args):
                return (
                    bool(args)
                    and isinstance(args[-1], ValueDef)
                    and self.is_numeric(args[-1], bound)
                    and all(
                        isinstance(pair, tuple)
                        and len(pair) == 2
                        and isinstance(pair[0], ValueDef)
                        and all(self.is_numeric(item, bound) for item in pair)
                        for pair in args[:-1]
                    )
                )
            case Operation(op, args) if op in _ARITHMETIC:
                valid_arity = (
                    len(args) == 2 if op == Operator.sub else len(args) == 1 if op == Operator.minus else bool(args)
                )
                return valid_arity and all(self.is_numeric(arg, bound) for arg in args)
            case _:
                return False

    def linear_integer(self, expr: Expr) -> Operation:
        """Collect additive terms without distributing products over sums."""
        terms: dict[Expr, int] = {}
        offset = 0
        pending: list[tuple[int, Expr]] = [(1, expr)]
        while pending:
            factor, term = pending.pop()
            match term:
                case ValueDef(_, value):
                    offset += factor * cast(int, value)
                case Operation(Operator.add, args):
                    pending.extend((factor, cast(Expr, arg)) for arg in reversed(args))
                case Operation(Operator.sub, (left, right)):
                    pending.extend(((-factor, cast(Expr, right)), (factor, cast(Expr, left))))
                case Operation(Operator.minus, (arg,)):
                    pending.append((-factor, cast(Expr, arg)))
                case Operation(Operator.linear_integer, args):
                    pending.append((factor, cast(Expr, args[-1])))
                    for pair in reversed(args[:-1]):
                        coefficient, item = cast(tuple[ValueDef, Expr], pair)
                        pending.append((factor * cast(int, coefficient.value), item))
                case _:
                    terms[term] = terms.get(term, 0) + factor
        pairs: list[OperationArg] = []
        for term, coefficient in terms.items():
            if coefficient != 0:
                pairs.append((ValueDef(ValueType.integer, coefficient), term))
        return Operation(Operator.linear_integer, (*pairs, ValueDef(ValueType.integer, offset)))

    def visit(self, expr: OperationArg, bound: frozenset[VariableRef] = frozenset()) -> OperationArg:
        """Normalize nested expressions, retaining lexical lambda boundaries."""
        match expr:
            case ValueDef() | VariableRef() | Python():
                return expr
            case Lambda(parameters, body):
                return Lambda(
                    parameters,
                    cast(Expr, self.visit(body, bound | frozenset(parameters))),
                )
            case tuple():
                return tuple(cast(Expr, self.visit(item, bound)) for item in expr)
            case frozenset():
                return frozenset(cast(Expr, self.visit(item, bound)) for item in expr)
            case Operation(op, args):
                rewritten = Operation(op, tuple(self.visit(arg, bound) for arg in args))
                if op in _RELATIONS and len(args) == 2 and all(self.is_numeric(arg, bound) for arg in rewritten.args):
                    difference = Operation(Operator.sub, rewritten.args)
                    return Operation(op, (self.linear_integer(difference), _ZERO))
                if (op in _ARITHMETIC or op == Operator.linear_integer) and self.is_numeric(rewritten, bound):
                    if op == Operator.mult:
                        coefficient = 1
                        factors: list[Expr] = []
                        for arg in rewritten.args:
                            if isinstance(arg, ValueDef):
                                coefficient *= cast(int, arg.value)
                            else:
                                factors.append(cast(Expr, arg))
                        if not factors:
                            return self.linear_integer(ValueDef(ValueType.integer, coefficient))
                        if len(factors) != 1 or isinstance(factors[0], Operation):
                            return rewritten
                        return self.linear_integer(
                            Operation(
                                Operator.linear_integer,
                                (
                                    (
                                        ValueDef(ValueType.integer, coefficient),
                                        factors[0],
                                    ),
                                    _ZERO,
                                ),
                            )
                        )
                    return self.linear_integer(rewritten)
                return rewritten


def normalize(store: ConstraintStore, static_types: StaticTypeStore) -> None:
    """Rewrite store expressions in place, preserving IDs and declaration metadata."""
    normalizer = _Normalizer(static_types)
    for expr_id, expr in store.expressions.items():
        store.replace_expression(expr_id, cast(Expr, normalizer.visit(expr)))
