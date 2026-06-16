from __future__ import annotations

from collections import namedtuple
from typing import Any, NamedTuple

import constraint_handler.schemas.domain as domain  # fmt: skip
import constraint_handler.schemas.expression as expression
import constraint_handler.schemas.statement as statement
import constraint_handler.schemas.warning as warning


class FailIntegrity(NamedTuple):
    pass


class EvalResult(NamedTuple):
    value: Any
    errors: tuple[tuple[warning.Kind, str], ...]


class Variable_declare(NamedTuple):
    label: expression.constant
    name: expression.constant
    domain: domain.Domain


class Variable_define(NamedTuple):
    label: expression.constant
    name: expression.constant
    value: expression.Expr


class Variable_domain(NamedTuple):
    label: expression.constant
    name: expression.constant
    value: expression.Expr


class Variable_declareOptional(NamedTuple):
    label: expression.constant
    name: expression.constant


type VariableAtom = Variable_declare | Variable_define | Variable_domain | Variable_declareOptional


class Bool_evaluate(NamedTuple):
    label: expression.constant
    expr: expression.Expr


class Bool_evaluated(NamedTuple):
    expr: expression.Expr
    value: expression.ReducedExpr


class Set_declare(NamedTuple):
    label: expression.constant
    name: expression.constant


class Set_assign(NamedTuple):
    label: expression.constant
    name: expression.constant
    member: expression.Expr


class Set_baseDomain(NamedTuple):
    label: expression.constant
    name: expression.constant
    value: expression.Expr


class Set_value(NamedTuple):
    name: expression.constant
    elt: expression.ReducedExpr


type SetAtom = Set_declare | Set_assign | Set_baseDomain


class Multimap_declare(NamedTuple):
    label: expression.constant
    name: expression.constant


class Multimap_assign(NamedTuple):
    label: expression.constant
    name: expression.constant
    key: expression.Expr
    val: expression.Expr


class Multimap_value(NamedTuple):
    name: expression.constant
    key: expression.ReducedExpr
    cst: expression.ReducedExpr


type MultimapAtom = Multimap_declare | Multimap_assign


class Execution_declare(NamedTuple):
    label: expression.constant
    name: expression.constant
    body: statement.Stmt
    inputs_vars: list[expression.constant]
    outputs_vars: list[expression.constant]


class Execution_run(NamedTuple):
    label: expression.constant
    name: expression.constant


type ExecutionAtom = Execution_declare | Execution_run


class Optimize_maximizeSum(NamedTuple):
    label: expression.constant
    value: expression.Expr
    id: expression.constant
    priority: expression.Expr | expression.constant


class Optimize_precision(NamedTuple):
    value: expression.Expr
    priority: expression.Expr


type OptimizeAtom = Optimize_maximizeSum | Optimize_precision


class Preference_maximizeScore(NamedTuple):
    pass


class Preference_holds(NamedTuple):
    label: expression.constant
    value: expression.Expr
    factor: int


class Preference_variableValue(NamedTuple):
    label: expression.constant
    variable: expression.constant
    value: expression.Expr
    factor: int


type PreferenceAtom = Preference_maximizeScore | Preference_holds | Preference_variableValue


class Preference_score(NamedTuple):
    score: int


class Ensure(NamedTuple):
    label: expression.constant
    expr: expression.Expr


class Value(NamedTuple):
    name: expression.constant
    val: expression.ReducedExpr

    def __repr__(self):
        return f"Value({str(self.name)},{str(self.val)})"


class Evaluate(NamedTuple):
    label: expression.constant
    operator: expression.Operator | expression.Variable
    args: list[expression.Expr]


class Evaluated(NamedTuple):
    name: expression.Operator
    expr: list[expression.Expr]
    value: expression.ReducedExpr


type MainAtom = Ensure | Evaluate
type Atom = ExecutionAtom | MainAtom | MultimapAtom | OptimizeAtom | PreferenceAtom | SetAtom | VariableAtom
type ResultAtom = Value | Evaluated | Set_value | Multimap_value | Preference_score | warning.Warning


Main_solverIdentifiers = namedtuple("_main_solverIdentifiers", ["id"])
Main_solverIdentifiers.__annotations__ = {"id": list[expression.constant]}
