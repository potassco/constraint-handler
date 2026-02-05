from __future__ import annotations

import typing

import constraint_handler.schemas.expression as expression


class Assert(typing.NamedTuple):
    expr: expression.Expr


class Assign(typing.NamedTuple):
    var: expression.constant
    expr: expression.Expr


class If(typing.NamedTuple):
    cond: expression.Expr
    then: Stmt
    else_: Stmt


class Noop(typing.NamedTuple):
    pass


class Statement_python(typing.NamedTuple):
    code: str


class Seq2(typing.NamedTuple):
    fst: Stmt
    snd: Stmt


class While(typing.NamedTuple):
    max_iterations: int
    cond: expression.Expr
    body: Stmt


type Stmt = Assert | Assign | If | Noop | Statement_python | Seq2 | While
