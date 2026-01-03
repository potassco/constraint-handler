from __future__ import annotations

from collections import namedtuple
from typing import NamedTuple

import clingo

import constraint_handler.schemas.expression as expression
import constraint_handler.schemas.statement as statement
from constraint_handler.schemas.expression import BaseType, constant


class Error(NamedTuple):
    message: str


class FailIntegrity(NamedTuple):
    pass


class Set_declare(NamedTuple):
    label: constant
    name: constant


class Set_assign(NamedTuple):
    label: constant
    name: constant
    member: expression.Expr


class Multimap_declare(NamedTuple):
    label: constant
    name: constant


class Multimap_assign(NamedTuple):
    label: constant
    name: constant
    key: expression.Expr
    val: expression.Expr


class Execution_declare(NamedTuple):
    label: constant
    name: constant
    body: statement.Stmt
    inputs_vars: list[constant]
    outputs_vars: list[constant]


class Execution_run(NamedTuple):
    label: constant
    name: constant


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


class Optimize_maximizeSum(NamedTuple):
    label: constant
    value: expression.Expr
    id: constant


class Optimize_precision(NamedTuple):
    value: expression.Expr


class Value(NamedTuple):
    name: constant
    type_: BaseType | clingo.Symbol
    cst: constant  # ReducedExpr


class Set_value(NamedTuple):
    name: constant
    elt_type_: BaseType | clingo.Symbol
    elt_cst: constant


class Multimap_value(NamedTuple):
    name: constant
    key_type_: BaseType | clingo.Symbol
    key_value: constant
    cst_type_: BaseType | clingo.Symbol
    cst_value: constant


class Warning(NamedTuple):
    content: constant


type SetAtom = Set_declare | Set_assign
type MultimapAtom = Multimap_declare | Multimap_assign
type ExecutionAtom = Execution_declare | Execution_run
type VariableAtom = Variable_declare | Variable_define | Variable_domain
type OptimizeAtom = Optimize_maximizeSum | Optimize_precision
type Atom = ExecutionAtom | MultimapAtom | OptimizeAtom | SetAtom | VariableAtom
type ResultAtom = Value | Set_value | Multimap_value | Warning


class Assign(NamedTuple):
    label: constant
    var: constant
    expr: expression.Expr


# AssignAtom = namedtuple("Assign", ["label", "var", "expr"])
# AssignAtom.__annotations__ = {"label": constant, "var": constant, "expr": expression.Expr}


class Ensure(NamedTuple):
    label: constant
    expr: expression.Expr


class Evaluate(NamedTuple):
    operator: expression.Operator | expression.Variable
    args: list[expression.Expr]


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
