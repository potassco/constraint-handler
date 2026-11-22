from __future__ import annotations

from typing import Any, NamedTuple

import clingo

import constraint_handler.schemas.domain as domain  # fmt: skip
import constraint_handler.schemas.expression as expression
import constraint_handler.schemas.type_ as type_m
import constraint_handler.schemas.warning as warning


class EvalResult(NamedTuple):
    value: Any
    errors: tuple[tuple[warning.Kind, str], ...]


class Bool_evaluated(NamedTuple):
    expr: expression.Expr
    value: expression.ReducedExpr


class Set_value(NamedTuple):
    name: expression.constant
    elt: expression.ReducedExpr


class Multimap_value(NamedTuple):
    name: expression.constant
    key: expression.ReducedExpr
    cst: expression.ReducedExpr


class Optimize_modelValue(NamedTuple):
    label: expression.constant
    priority: expression.constant
    total: expression.ReducedExpr


class Optimize_value(NamedTuple):
    label: expression.constant
    priority: expression.constant
    total: expression.ReducedExpr


class Preference_score(NamedTuple):
    score: int


type OptimizeResult = Optimize_modelValue | Optimize_value


class Value(NamedTuple):
    name: expression.constant
    val: expression.ReducedExpr

    def __repr__(self):
        return f"Value({str(self.name)},{str(self.val)})"


class Variable_declared(NamedTuple):
    name: expression.constant


class Variable_defined(NamedTuple):
    name: expression.constant


class Variable_typed(NamedTuple):
    name: expression.constant
    type_: type_m.BaseType | type_m.OtherType | clingo.Symbol


class Evaluated(NamedTuple):
    expr: expression.Expr
    value: expression.ReducedExpr


type ResultAtom = Bool_evaluated | Evaluated | Set_value | Multimap_value | OptimizeResult | Preference_score | Value | Variable_declared | Variable_defined | Variable_typed | warning.Warning | warning.Warning_raised
