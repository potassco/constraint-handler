from __future__ import annotations

from typing import NamedTuple

from constraint_handler.schemas.expression import Expr, constant


class Assert(NamedTuple):
    expr: Expr


class Assign(NamedTuple):
    var: constant
    expr: Expr


class If(NamedTuple):
    cond: Expr
    then: Stmt
    else_: Stmt


class Noop(NamedTuple):
    pass


class Statement_python(NamedTuple):
    code: str


class Seq2(NamedTuple):
    fst: Stmt
    snd: Stmt


class While(NamedTuple):
    max_iterations: int
    cond: Expr
    body: Stmt


type Stmt = Assert | Assign | If | Noop | Statement_python | Seq2 | While
