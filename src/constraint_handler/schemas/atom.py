from __future__ import annotations

from typing import NamedTuple

import clingo

import constraint_handler.myClorm as myClorm
import constraint_handler.schemas.domain as domain  # fmt: skip
import constraint_handler.schemas.expression as expression
import constraint_handler.schemas.statement as statement

LABEL_ANONYMOUS: expression.constant = clingo.Function("_label_anonymous")


class FailIntegrity(NamedTuple):
    pass


class Variable_assign(NamedTuple):
    name: expression.constant
    value: expression.Expr
    label: expression.constant = LABEL_ANONYMOUS


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


type VariableAtom = Variable_assign | Variable_choice | Variable_declare | Variable_default | Variable_define | Variable_domain


class Bool_evaluate(NamedTuple):
    expr: expression.Expr
    label: expression.constant = LABEL_ANONYMOUS


class Set_assign(NamedTuple):
    name: expression.constant
    member: expression.Expr
    label: expression.constant = LABEL_ANONYMOUS


class Set_baseDomain(NamedTuple):
    name: expression.constant
    value: expression.Expr
    label: expression.constant = LABEL_ANONYMOUS


type SetAtom = Set_assign | Set_baseDomain


class Multimap_assign(NamedTuple):
    name: expression.constant
    key: expression.Expr
    val: expression.Expr
    label: expression.constant = LABEL_ANONYMOUS


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


class Ensure(NamedTuple):
    expr: expression.Expr
    label: expression.constant = LABEL_ANONYMOUS


class Evaluate(NamedTuple):
    expr: expression.Expr
    label: expression.constant = LABEL_ANONYMOUS


type MainAtom = Bool_evaluate | Ensure | Evaluate
type Atom = ExecutionAtom | MainAtom | Multimap_assign | OptimizeAtom | PreferenceAtom | SetAtom | VariableAtom
