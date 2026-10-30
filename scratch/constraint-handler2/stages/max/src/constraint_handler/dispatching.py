"""Classify preprocessed expression IDs by their execution engine."""

from enum import StrEnum, auto
from typing import cast

from .analysis import linear_operands
from .domains import DomainStore
from .internal_input import (
    ConstraintStore,
    Expr,
    ExprId,
    Lambda,
    Operation,
    Python,
    ValueDef,
)
from .python_input import Operator


class Engine(StrEnum):
    """Name the mutually exclusive execution engines."""

    native = auto()
    complex = auto()
    propagator = auto()


class DispatchStore(dict[ExprId, Engine]):
    """Map every stored expression ID to exactly one execution engine."""


def dispatch(store: ConstraintStore, domains: DomainStore) -> DispatchStore:
    """Classify flat roots without evaluating expressions or changing metadata."""
    engines = DispatchStore()
    for expr_id, expr in sorted(store.expressions.items()):
        match expr:
            case Operation(Operator.lambda_, _):
                raise TypeError("lambda applications must be converted before dispatch")
            case Operation(Operator.python_eval, (Python(), *actual)):
                parameters = tuple(actual)
            case Operation(Operator.linear_integer | Operator.linear_comparison):
                parameters = linear_operands(expr)
            case Operation(_, args):
                parameters = args
            case tuple() | frozenset():
                parameters = tuple(expr)
            case _:
                parameters = ()
        pending = list(parameters)
        while pending:
            arg = pending.pop()
            if isinstance(arg, (Operation, Lambda, Python)):
                raise TypeError(
                    "dispatch requires flat expressions without lambda descriptors"
                )
            if isinstance(arg, (tuple, frozenset)):
                pending.extend(arg)
        unknown = [
            domains[cast(Expr, arg)].unknown
            for arg in parameters
            if not isinstance(arg, ValueDef)
        ]
        if isinstance(expr, Operation) and expr.op in {Operator.conj, Operator.disj}:
            engines[expr_id] = Engine.native
        elif any(unknown):
            engines[expr_id] = Engine.propagator
        elif isinstance(expr, Operation) and expr.op == Operator.python_eval:
            engines[expr_id] = Engine.complex
        else:
            engines[expr_id] = Engine.native
    return engines
