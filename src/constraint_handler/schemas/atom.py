from __future__ import annotations

from collections import namedtuple
from typing import NamedTuple

import constraint_handler.schemas.expression as expression
import constraint_handler.schemas.statement as statement
import constraint_handler.schemas.warning as warning


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
    label: expression.constant
    name: expression.constant
    domain: Domain


class Variable_define(NamedTuple):
    label: expression.constant
    name: expression.constant
    value: expression.Expr


class Variable_domain(NamedTuple):
    name: expression.constant
    value: expression.Expr


class Variable_declareOptional(NamedTuple):
    name: expression.constant


type VariableAtom = Variable_declare | Variable_define | Variable_domain | Variable_declareOptional


class Set_declare(NamedTuple):
    label: expression.constant
    name: expression.constant


class Set_assign(NamedTuple):
    label: expression.constant
    name: expression.constant
    member: expression.Expr


class Set_value(NamedTuple):
    name: expression.constant
    elt: expression.Val


type SetAtom = Set_declare | Set_assign


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
    key: expression.Val
    cst: expression.Val


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


class Assign(NamedTuple):
    label: expression.constant
    var: expression.constant
    expr: expression.Expr


class Ensure(NamedTuple):
    label: expression.constant
    expr: expression.Expr


class Value(NamedTuple):
    name: expression.constant
    val: expression.Val

    def __repr__(self):
        return f"Value({str(self.name)},{str(self.val)})"


class Evaluate(NamedTuple):
    operator: expression.Operator | expression.Variable
    args: list[expression.Expr]


class Evaluated(NamedTuple):
    name: expression.Operator
    expr: list[expression.Expr]
    type_: expression.BaseType
    value: expression.constant


type MainAtom = Assign | Ensure | Evaluate
type Atom = ExecutionAtom | MainAtom | MultimapAtom | OptimizeAtom | PreferenceAtom | SetAtom | VariableAtom
type ResultAtom = Value | Evaluated | Set_value | Multimap_value | Preference_score | warning.Warning


Main_solverIdentifier = namedtuple("_main_solverIdentifier", ["id"])
Main_solverIdentifier.__annotations__ = {"id": expression.constant}


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


class Propagator_forbid_warning(warning.Forbid_warning):
    pass
