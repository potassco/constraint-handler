"""Normalize arithmetic in a constraint store while retaining expression IDs."""

from itertools import product
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
from .static_types import StaticTypeStore, Type, TypeScope, UnknownType

_NUMERIC = frozenset({ValueType.integer})
_RELATIONS = frozenset(
    {Operator.eq, Operator.neq, Operator.lt, Operator.leq, Operator.gt, Operator.geq}
)
_ARITHMETIC = frozenset({Operator.add, Operator.sub, Operator.minus, Operator.mult})
_ZERO = ValueDef(ValueType.integer, 0)


class _Normalizer:
    """Rewrite integer expressions using the previously computed variable types."""

    def __init__(self, static_types: StaticTypeStore) -> None:
        """Retain type information used to guard arithmetic rewrites."""
        self._types = static_types
        self._integer_expressions: set[tuple[Expr, TypeScope]] = {
            (expr, frozenset())
            for expr, known in static_types.items()
            if not isinstance(known, UnknownType) and bool(known) and known <= _NUMERIC
        }
        self._integer_expressions.update(
            (expr, scope)
            for (expr, scope), known in static_types.scoped_expressions.items()
            if not isinstance(known, UnknownType) and bool(known) and known <= _NUMERIC
        )

    def is_numeric(self, expr: OperationArg, scopes: frozenset[TypeScope]) -> bool:
        """Prove integer inputs conservatively, without assuming callable results."""
        match expr:
            case ValueDef(kind, _):
                return kind in _NUMERIC
            case VariableRef():
                for scope in scopes:
                    known = dict(scope).get(expr, self._types.get(expr, UnknownType()))
                    if (
                        isinstance(known, UnknownType)
                        or not known
                        or not known <= _NUMERIC
                    ):
                        return False
                return bool(scopes)
            case Operation(Operator.linear_integer, args):
                return (
                    bool(args)
                    and isinstance(args[-1], ValueDef)
                    and self.is_numeric(args[-1], scopes)
                    and all(
                        isinstance(pair, tuple)
                        and len(pair) == 2
                        and isinstance(pair[0], ValueDef)
                        and all(self.is_numeric(item, scopes) for item in pair)
                        for pair in args[:-1]
                    )
                )
            case Operation(op, args) if op in _ARITHMETIC:
                valid_arity = (
                    len(args) == 2
                    if op == Operator.sub
                    else len(args) == 1
                    if op == Operator.minus
                    else bool(args)
                )
                return valid_arity and all(self.is_numeric(arg, scopes) for arg in args)
            case Operation():
                return bool(scopes) and all(
                    (expr, scope) in self._integer_expressions for scope in scopes
                )
            case _:
                return False

    def lambda_scopes(
        self,
        parameters: tuple[VariableRef, ...],
        arguments: tuple[OperationArg, ...],
        scopes: frozenset[TypeScope],
    ) -> frozenset[TypeScope]:
        """Bind each call's argument type alternatives in its lexical environment."""
        bindings: set[TypeScope] = set()
        for scope in scopes:
            alternatives: list[tuple[Type, ...]] = []
            for arg in arguments:
                known = (
                    UnknownType()
                    if isinstance(arg, (Lambda, Python))
                    else self._types.scoped_expressions.get((arg, scope), UnknownType())
                    if scope
                    else self._types.get(arg, UnknownType())
                )
                if isinstance(known, UnknownType) and self.is_numeric(
                    arg, frozenset({scope})
                ):
                    known = _NUMERIC
                alternatives.append(
                    (known,)
                    if isinstance(known, UnknownType)
                    else tuple(frozenset({member}) for member in known)
                    or (UnknownType(),)
                )
            for combination in product(*alternatives):
                local = dict(scope)
                local.update(zip(parameters, combination, strict=True))
                bindings.add(frozenset(local.items()))
        return frozenset(bindings)

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
                    pending.extend(
                        ((-factor, cast(Expr, right)), (factor, cast(Expr, left)))
                    )
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
        return Operation(
            Operator.linear_integer, (*pairs, ValueDef(ValueType.integer, offset))
        )

    def visit(
        self,
        expr: OperationArg,
        scopes: frozenset[TypeScope] = frozenset({frozenset()}),
    ) -> OperationArg:
        """Normalize nested expressions, retaining lexical lambda boundaries."""
        match expr:
            case ValueDef() | VariableRef() | Python():
                return expr
            case Lambda(parameters, body):
                local_scopes = frozenset(
                    frozenset(
                        (dict(scope) | dict.fromkeys(parameters, UnknownType())).items()
                    )
                    for scope in scopes
                )
                return Lambda(
                    parameters,
                    cast(Expr, self.visit(body, local_scopes)),
                )
            case tuple():
                return tuple(cast(Expr, self.visit(item, scopes)) for item in expr)
            case frozenset():
                return frozenset(cast(Expr, self.visit(item, scopes)) for item in expr)
            case Operation(op, args):
                if (
                    op == Operator.lambda_
                    and args
                    and isinstance(args[0], Lambda)
                    and len(args[0].vars) == len(args) - 1
                ):
                    callback = args[0]
                    local_scopes = self.lambda_scopes(callback.vars, args[1:], scopes)
                    rewritten = Operation(
                        op,
                        (
                            Lambda(
                                callback.vars,
                                cast(Expr, self.visit(callback.expr, local_scopes)),
                            ),
                            *(self.visit(arg, scopes) for arg in args[1:]),
                        ),
                    )
                else:
                    rewritten = Operation(
                        op, tuple(self.visit(arg, scopes) for arg in args)
                    )
                for scope in scopes:
                    if (expr, scope) in self._integer_expressions:
                        self._integer_expressions.add((rewritten, scope))
                if (
                    op in _RELATIONS
                    and len(args) == 2
                    and all(self.is_numeric(arg, scopes) for arg in rewritten.args)
                ):
                    difference = Operation(Operator.sub, rewritten.args)
                    return Operation(
                        Operator.linear_comparison,
                        (
                            ValueDef(ValueType.string, op.value),
                            *self.linear_integer(difference).args,
                        ),
                    )
                if (
                    op in _ARITHMETIC or op == Operator.linear_integer
                ) and self.is_numeric(rewritten, scopes):
                    if op == Operator.mult:
                        coefficient = 1
                        factors: list[Expr] = []
                        for arg in rewritten.args:
                            if isinstance(arg, ValueDef):
                                coefficient *= cast(int, arg.value)
                            elif (
                                isinstance(arg, Operation)
                                and arg.op == Operator.linear_integer
                            ):
                                if len(arg.args) == 1:
                                    coefficient *= cast(
                                        int, cast(ValueDef, arg.args[0]).value
                                    )
                                elif len(arg.args) == 2 and arg.args[-1] == _ZERO:
                                    scalar, term = cast(
                                        tuple[ValueDef, Expr], arg.args[0]
                                    )
                                    coefficient *= cast(int, scalar.value)
                                    factors.append(term)
                                else:
                                    factors.append(arg)
                            else:
                                factors.append(cast(Expr, arg))
                        if coefficient == 0 or not factors:
                            return self.linear_integer(
                                ValueDef(ValueType.integer, coefficient)
                            )
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
