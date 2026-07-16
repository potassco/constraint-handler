from __future__ import annotations

from collections import namedtuple
from typing import NamedTuple

import clingo

import constraint_handler.schemas.expression as expression
import constraint_handler.schemas.type_ as type_m

Main_solverIdentifiers = namedtuple("_main_solverIdentifiers", ["id"])
Main_solverIdentifiers.__annotations__ = {"id": list[expression.constant]}


class Ref(NamedTuple):
    type_: type_m.BaseType | clingo.Symbol
    expr: expression.Expr


class _set_contains(NamedTuple):
    expr: expression.Expr
    val: expression.Val | Ref


class _se_value(NamedTuple):
    expr: expression.Expr
    val: expression.Val | Ref


class _shared_value(NamedTuple):
    expr: expression.Expr
    val: expression.ReducedExpr


class _optimize_component(NamedTuple):
    label: expression.constant
    expr: expression.Expr
    precision: clingo.Symbol
    id: expression.constant
    priority: expression.Expr | expression.constant


class Valid(NamedTuple):
    result: type.Any
