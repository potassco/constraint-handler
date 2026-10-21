from __future__ import annotations

from typing import NamedTuple

import constraint_handler.schemas.core as core
import constraint_handler.schemas.expression as expression


class Share_value(NamedTuple):
    expr: expression.Expr


type Atom = (
    core.Bool_evaluate
    | core.Multimap_assign
    | core.Set_assign
    | core.Variable_assign
    | core.Variable_choice
    | core.Variable_declare
    | core.Variable_default
    | core.Variable_define
    | core.Variable_domain
    | Share_value
)


class Ch_solve(NamedTuple):
    declaration: Atom
    label: expression.constant
