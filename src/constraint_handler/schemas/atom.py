from __future__ import annotations

from typing import Any, NamedTuple

import clingo

import constraint_handler.myClorm as myClorm
import constraint_handler.schemas.domain as domain  # fmt: skip
import constraint_handler.schemas.expression as expression
import constraint_handler.schemas.statement as statement
import constraint_handler.schemas.warning as warning

LABEL_ANONYMOUS: expression.constant = clingo.Function("_label_anonymous")


class FailIntegrity(NamedTuple):
    pass


class EvalResult(NamedTuple):
    value: Any
    errors: tuple[tuple[warning.Kind, str], ...]


class Variable_choice(NamedTuple):
    name: expression.constant
    value: expression.Expr
    label: expression.constant = LABEL_ANONYMOUS


class Variable_declare(NamedTuple):
    name: expression.constant
    domain: domain.Domain
    label: expression.constant = LABEL_ANONYMOUS


class Variable_define(NamedTuple):
    name: expression.constant
    value: expression.Expr
    label: expression.constant = LABEL_ANONYMOUS


class Variable_default(NamedTuple):
    name: expression.constant
    value: expression.Expr
    condition: expression.Expr = expression.TRUE
    priority: expression.constant = 0
    label: expression.constant = LABEL_ANONYMOUS


class Variable_domain(NamedTuple):
    name: expression.constant
    value: expression.Expr
    label: expression.constant = LABEL_ANONYMOUS


type VariableAtom = Variable_declare | Variable_define | Variable_default | Variable_domain


class Bool_evaluate(NamedTuple):
    expr: expression.Expr
    label: expression.constant = LABEL_ANONYMOUS


class Bool_evaluated(NamedTuple):
    expr: expression.Expr
    value: expression.ReducedExpr


class Set_assign(NamedTuple):
    name: expression.constant
    member: expression.Expr
    label: expression.constant = LABEL_ANONYMOUS


class Set_baseDomain(NamedTuple):
    name: expression.constant
    value: expression.Expr
    label: expression.constant = LABEL_ANONYMOUS


class Set_value(NamedTuple):
    name: expression.constant
    elt: expression.ReducedExpr


type SetAtom = Set_assign | Set_baseDomain


class Multimap_assign(NamedTuple):
    name: expression.constant
    key: expression.Expr
    val: expression.Expr
    label: expression.constant = LABEL_ANONYMOUS


class Multimap_value(NamedTuple):
    name: expression.constant
    key: expression.ReducedExpr
    cst: expression.ReducedExpr


type MultimapAtom = Multimap_assign


class Execution_declare(NamedTuple):
    name: expression.constant
    body: statement.Stmt
    inputs_vars: myClorm.ImmutableList[expression.constant]
    outputs_vars: myClorm.ImmutableList[expression.constant]
    label: expression.constant = LABEL_ANONYMOUS


class Execution_run(NamedTuple):
    name: expression.constant
    label: expression.constant = LABEL_ANONYMOUS


type ExecutionAtom = Execution_declare | Execution_run


class Optimize_maximizeSum(NamedTuple):
    value: expression.Expr
    id: expression.constant = 0
    priority: expression.constant = 0
    label: expression.constant = LABEL_ANONYMOUS


class Optimize_precision(NamedTuple):
    value: expression.Expr
    priority: expression.constant


type OptimizeAtom = Optimize_maximizeSum | Optimize_precision


class Optimize_modelValue(NamedTuple):
    label: expression.constant
    priority: expression.constant
    total: expression.ReducedExpr


class Optimize_value(NamedTuple):
    label: expression.constant
    priority: expression.constant
    total: expression.ReducedExpr


type OptimizeResult = Optimize_modelValue | Optimize_value


class Preference_maximizeScore(NamedTuple):
    pass


class Preference_holds(NamedTuple):
    value: expression.Expr
    factor: int = 1
    label: expression.constant = LABEL_ANONYMOUS


class Preference_variableValue(NamedTuple):
    variable: expression.constant
    value: expression.Expr
    factor: int = 1
    label: expression.constant = LABEL_ANONYMOUS


type PreferenceAtom = Preference_maximizeScore | Preference_holds | Preference_variableValue


class Preference_score(NamedTuple):
    score: int


class Ensure(NamedTuple):
    expr: expression.Expr
    label: expression.constant = LABEL_ANONYMOUS


class Value(NamedTuple):
    name: expression.constant
    val: expression.ReducedExpr

    def __repr__(self):
        return f"Value({str(self.name)},{str(self.val)})"


class Evaluate(NamedTuple):
    expr: expression.Expr
    label: expression.constant = LABEL_ANONYMOUS


class Evaluated(NamedTuple):
    expr: expression.Expr
    value: expression.ReducedExpr


type MainAtom = Ensure | Evaluate
type Atom = ExecutionAtom | MainAtom | MultimapAtom | OptimizeAtom | PreferenceAtom | SetAtom | VariableAtom
type ResultAtom = Value | Evaluated | Set_value | Multimap_value | OptimizeResult | Preference_score | warning.Warning
