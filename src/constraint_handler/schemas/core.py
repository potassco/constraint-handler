from __future__ import annotations

from typing import NamedTuple

import clingo

import constraint_handler.schemas.domain as domain  # fmt: skip
import constraint_handler.schemas.expression as expression


class Variable_assign(NamedTuple):
    name: expression.constant
    value: expression.Expr


class Variable_choice(NamedTuple):
    name: expression.constant
    value: expression.Expr


class Variable_declare(NamedTuple):
    name: expression.constant
    domain: domain.Domain


class Variable_define(NamedTuple):
    name: expression.constant
    value: expression.Expr


class Variable_default(NamedTuple):
    name: expression.constant
    value: expression.Expr
    condition: expression.Expr
    priority: expression.constant


class Variable_domain(NamedTuple):
    name: expression.constant
    value: expression.Expr


class Bool_evaluate(NamedTuple):
    expr: expression.Expr


class Set_assign(NamedTuple):
    name: expression.constant
    member: expression.Expr


class Set_baseDomain(NamedTuple):
    name: expression.constant
    value: expression.Expr


class Multimap_assign(NamedTuple):
    name: expression.constant
    key: expression.Expr
    val: expression.Expr


class Optimize_component(NamedTuple):
    value: expression.Expr
    precision: expression.Expr
    id: expression.constant
    priority: expression.constant


class Preference_maximizeScore(NamedTuple):
    pass


class Preference_holds(NamedTuple):
    value: expression.Expr
    factor: int


type PreferenceAtom = Preference_maximizeScore | Preference_holds


class Ensure(NamedTuple):
    expr: expression.Expr


class Evaluate(NamedTuple):
    expr: expression.Expr


type Atom = Bool_evaluate | Ensure | Evaluate | Multimap_assign | Optimize_component | PreferenceAtom | Set_assign | Set_baseDomain | Variable_assign | Variable_choice | Variable_declare | Variable_default | Variable_define | Variable_domain


class Core_ch(NamedTuple):
    declaration: Atom
    label: expression.constant
