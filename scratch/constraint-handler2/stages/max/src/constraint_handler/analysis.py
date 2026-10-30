"""Shared expression metadata and structural contracts for analysis passes."""

from collections.abc import Hashable, Iterable, Mapping
from typing import cast

from .diagnostics import Diagnostics, ExpressionLocation
from .internal_input import (
    Expr,
    Lambda,
    Operation,
    OperationArg,
    ValueDef,
    ValueType,
    VariableRef,
)
from .python_input import Operator

type LinearIntegerArg = tuple[ValueDef, Expr] | ValueDef

LINEAR_RELATIONS = frozenset({"eq", "neq", "lt", "leq", "gt", "geq"})


def linear_operands(expr: Operation) -> tuple[OperationArg, ...]:
    """Extract terms and the final offset from a validated linear operation."""
    pairs = expr.args[1:-1] if expr.op == Operator.linear_comparison else expr.args[:-1]
    return (
        *(cast(tuple[Expr, Expr], pair)[1] for pair in pairs),
        expr.args[-1],
    )


def linear_comparison_arguments(
    args: tuple[OperationArg, ...],
    diagnostics: Diagnostics,
    location: ExpressionLocation,
) -> list[LinearIntegerArg] | None:
    """Validate a literal relation followed by integer linear arguments."""
    if (
        not args
        or not isinstance(args[0], ValueDef)
        or args[0].value_type != ValueType.string
        or args[0].value not in LINEAR_RELATIONS
    ):
        diagnostics.error(
            "linear_comparison requires a literal relation: eq, neq, lt, leq, gt, geq",
            location=location,
        )
        return None
    return linear_integer_arguments(args[1:], diagnostics, location)


def lambda_call(
    args: tuple[OperationArg, ...],
    diagnostics: Diagnostics,
    location: ExpressionLocation,
) -> Lambda | None:
    """Validate a lambda call's callable and argument count without evaluating it."""
    if not args or not isinstance(args[0], Lambda):
        diagnostics.error(
            "lambda_ requires a Lambda as first argument", location=location
        )
        return None
    callback = args[0]
    if len(args) - 1 != len(callback.vars):
        diagnostics.error(
            f"Lambda expects {len(callback.vars)} arguments, got {len(args) - 1}",
            location=location,
        )
        return None
    return callback


def linear_integer_arguments(
    args: tuple[OperationArg, ...],
    diagnostics: Diagnostics,
    location: ExpressionLocation,
) -> list[LinearIntegerArg] | None:
    """Validate integer coefficient/term pairs followed by a required integer offset."""
    if not args:
        diagnostics.error(
            "linear_integer requires at least one argument", location=location
        )
        return None
    offset = args[-1]
    if (
        not isinstance(offset, ValueDef)
        or offset.value_type != ValueType.integer
        or type(offset.value) is not int
    ):
        diagnostics.error(
            "linear_integer constant offset must be a constant integer literal",
            location=location,
        )
        return None
    validated: list[LinearIntegerArg] = []
    for index, arg in enumerate(args[:-1]):
        if isinstance(arg, tuple) and len(arg) == 2:
            coefficient, term = arg
            if (
                not isinstance(coefficient, ValueDef)
                or coefficient.value_type != ValueType.integer
                or type(coefficient.value) is not int
            ):
                diagnostics.error(
                    "linear_integer coefficient must be a constant integer literal",
                    location=location,
                )
                return None
            validated.append((coefficient, term))
        else:
            diagnostics.error(
                f"Invalid linear_integer argument at position {index}: {arg}",
                location=location,
            )
            return None
    validated.append(offset)
    return validated


class ExpressionStore[Metadata: Hashable](dict[Expr, Metadata]):
    """Own global expression metadata and separate lambda-binding metadata."""

    def __init__(
        self,
        expressions: Mapping[Expr, Metadata] | Iterable[tuple[Expr, Metadata]] = (),
    ) -> None:
        """Copy initial global entries and create an independent scoped mapping."""
        super().__init__(expressions)
        self.scoped_expressions: dict[
            tuple[Expr, frozenset[tuple[VariableRef, Metadata]]], Metadata
        ] = {}

    def lookup(
        self,
        expr: Expr,
        *,
        scope: frozenset[tuple[VariableRef, Metadata]] = frozenset(),
    ) -> Metadata:
        """Use exactly the requested binding scope, without global fallback."""
        return self.scoped_expressions[expr, scope] if scope else self[expr]

    def record(
        self,
        expr: Expr,
        value: Metadata,
        *,
        scope: frozenset[tuple[VariableRef, Metadata]] = frozenset(),
    ) -> None:
        """Record metadata globally or under its explicit lambda bindings."""
        if scope:
            self.scoped_expressions[expr, scope] = value
        else:
            self[expr] = value
