from __future__ import annotations

from typing import NamedTuple

import constraint_handler.schemas.expression as expression


class Evaluate(NamedTuple):
    ref: expression.Expr
    expr: expression.Expr


class Variable_interface(NamedTuple):
    variable: expression.constant


type Atom = Evaluate | Variable_interface


class Ch_post(NamedTuple):
    declaration: Atom
    label: expression.constant
