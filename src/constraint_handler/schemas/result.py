from __future__ import annotations

from typing import Any, NamedTuple

import clingo

import constraint_handler.schemas.domain as domain  # fmt: skip
import constraint_handler.schemas.expression as expression
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


class Evaluated(NamedTuple):
    expr: expression.Expr
    value: expression.ReducedExpr


type ResultAtom = Bool_evaluated | Evaluated | Set_value | Multimap_value | OptimizeResult | Preference_score | Value | warning.Warning
