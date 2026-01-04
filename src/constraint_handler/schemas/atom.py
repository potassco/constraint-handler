from __future__ import annotations

from collections import namedtuple
from typing import Any, NamedTuple

import clingo

import constraint_handler.schemas.expression as expression
import constraint_handler.schemas.statement as statement
from constraint_handler.schemas.expression import BaseType, constant
from constraint_handler.utils.common import PPEnum


class Error(NamedTuple):
    message: str


class FailIntegrity(NamedTuple):
    pass


class FromFacts(NamedTuple):
    pass


class BoolDomain(NamedTuple):
    pass


class FromList(NamedTuple):
    elements: list[expression.Expr]


type Domain = BoolDomain | FromFacts | FromList


class Variable_declare(NamedTuple):
    label: constant
    name: constant
    domain: Domain


class Variable_define(NamedTuple):
    label: constant
    name: constant
    value: expression.Expr


class Variable_domain(NamedTuple):
    name: constant
    value: expression.Expr


class Variable_declareOptional(NamedTuple):
    name: constant


type VariableAtom = Variable_declare | Variable_define | Variable_domain | Variable_declareOptional


class Set_declare(NamedTuple):
    label: constant
    name: constant


class Set_assign(NamedTuple):
    label: constant
    name: constant
    member: expression.Expr


class Set_value(NamedTuple):
    name: constant
    elt_type_: BaseType | clingo.Symbol
    elt_cst: constant


type SetAtom = Set_declare | Set_assign


class Multimap_declare(NamedTuple):
    label: constant
    name: constant


class Multimap_assign(NamedTuple):
    label: constant
    name: constant
    key: expression.Expr
    val: expression.Expr


class Multimap_value(NamedTuple):
    name: constant
    key_type_: BaseType | clingo.Symbol
    key_value: constant
    cst_type_: BaseType | clingo.Symbol
    cst_value: constant


type MultimapAtom = Multimap_declare | Multimap_assign


class Execution_declare(NamedTuple):
    label: constant
    name: constant
    body: statement.Stmt
    inputs_vars: list[constant]
    outputs_vars: list[constant]


class Execution_run(NamedTuple):
    label: constant
    name: constant


type ExecutionAtom = Execution_declare | Execution_run


class Optimize_maximizeSum(NamedTuple):
    label: constant
    value: expression.Expr
    id: constant


class Optimize_precision(NamedTuple):
    value: expression.Expr


type OptimizeAtom = Optimize_maximizeSum | Optimize_precision


class Preference_maximizeScore(NamedTuple):
    pass


class Preference_holds(NamedTuple):
    label: constant
    value: expression.Expr
    factor: int


class Preference_variableValue(NamedTuple):
    label: constant
    variable: constant
    value: expression.Expr
    factor: int


type PreferenceAtom = Preference_maximizeScore | Preference_holds | Preference_variableValue


class Preference_score(NamedTuple):
    score: int


Warning1 = namedtuple("warning", ["content"])
Warning1.__annotations__ = {"id": constant}


VariableWarning = PPEnum(
    "VariableWarning", ["emptyDomain", "multipleDeclarations", "multipleDefinitions", "undeclared"]
)


class Variable(NamedTuple):
    symbol: VariableWarning


class Warning(NamedTuple):
    id: Variable
    declarations: list[constant]
    info: Any


class Assign(NamedTuple):
    label: constant
    var: constant
    expr: expression.Expr


class Ensure(NamedTuple):
    label: constant
    expr: expression.Expr


class Value(NamedTuple):
    name: constant
    type_: BaseType | clingo.Symbol
    cst: constant  # ReducedExpr


class Evaluate(NamedTuple):
    operator: expression.Operator | expression.Variable
    args: list[expression.Expr]


class Evaluated(NamedTuple):
    name: expression.Operator
    expr: list[expression.Expr]
    type_: BaseType
    value: constant


type MainAtom = Assign | Ensure | Evaluate
type Atom = ExecutionAtom | MainAtom | MultimapAtom | OptimizeAtom | PreferenceAtom | SetAtom | VariableAtom
type ResultAtom = Value | Evaluated | Set_value | Multimap_value | Preference_score | Warning1 | Warning


Main_solverIdentifier = namedtuple("_main_solverIdentifier", ["id"])
Main_solverIdentifier.__annotations__ = {"id": constant}


class Propagator_variable_declare(Variable_declare):
    pass


class Propagator_variable_define(Variable_define):
    pass


class Propagator_variable_domain(Variable_domain):
    pass


class Propagator_variable_declareOptional(Variable_declareOptional):
    pass


class Propagator_assign(Assign):
    pass


class Propagator_ensure(Ensure):
    pass


class Propagator_set_declare(Set_declare):
    pass


class Propagator_set_assign(Set_assign):
    pass


class Propagator_multimap_declare(Multimap_declare):
    pass


class Propagator_multimap_assign(Multimap_assign):
    pass


class Propagator_optimize_maximizeSum(Optimize_maximizeSum):
    pass


class Propagator_execution_declare(Execution_declare):
    pass


class Propagator_execution_run(Execution_run):
    pass


class Propagator_evaluate(Evaluate):
    pass
