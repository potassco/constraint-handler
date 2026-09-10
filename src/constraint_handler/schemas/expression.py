from __future__ import annotations

import types
import typing

import clingo

import constraint_handler.myClorm as myClorm
import constraint_handler.schemas.operators as operators
import constraint_handler.schemas.type_ as type_m
import constraint_handler.utils.common as common

Bad = common.Bad


class CustomOperator(typing.NamedTuple):
    name: clingo.Symbol


class Python(typing.NamedTuple):
    fn: str


class PythonExtract(typing.NamedTuple):
    stmt: str
    expr: str


Operator = (
    operators.ArithmeticOperator
    | operators.ComparisonOperator
    | operators.LogicOperator
    | operators.StringOperator
    | operators.MultimapOperator
    | operators.SetOperator
    | operators.ConditionalOperator
    | Python
    | PythonExtract
)


constant = bool | float | int | str | types.NoneType | clingo.Symbol


class Val(typing.NamedTuple):
    type_: type_m.BaseType | clingo.Symbol
    value: constant

    def __repr__(self):
        return f"Val({str(self.type_)},{str(self.value)})"


class Ref(typing.NamedTuple):
    type_: type_m.BaseType | clingo.Symbol
    value: constant

    def __repr__(self):
        return f"Ref({str(self.type_)},{str(self.value)})"


class Operation(typing.NamedTuple):
    op: Operator | Variable | Lambda
    args: myClorm.ImmutableList["Expr"]

    def __repr__(self):
        comma = ","
        return f"{self.op}({comma.join(str(arg) for arg in self.args)})"


class Variable(typing.NamedTuple):
    arg: constant

    def __repr__(self):
        return f"{self.arg}"


class Lambda(typing.NamedTuple):
    vars: myClorm.ImmutableList[clingo.Symbol]
    expr: "Expr"

    def __repr__(self):
        return f"Lambda({[str(x) for x in self.vars]},{str(self.expr)})"


type ReducedExpr = Bad | Val | Ref | frozenset[ReducedExpr] | tuple[ReducedExpr, ...]  # TODO handle Lambda
type Expr = Bad | Variable | Operation | Python | Val | Ref | Lambda | frozenset[Expr] | tuple[Expr, ...]


TRUE: typing.Final = Val(type_m.BaseType.bool, True)
FALSE: typing.Final = Val(type_m.BaseType.bool, False)
