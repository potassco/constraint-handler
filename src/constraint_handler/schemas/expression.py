from __future__ import annotations

import types
import typing
from enum import Enum

import clingo

import constraint_handler.logic as logic
import constraint_handler.multimap as multimap
import constraint_handler.myClorm as myClorm
import constraint_handler.set as myset
import constraint_handler.utils.common as common

BaseType = common.PPEnum("BaseType", ["int", "float", "str", "symbol", "bool", "none", "function", "multimap", "set"])

UnaryOperator = common.PPEnum(
    "UnaryOperator", ["abs", "sqrt", "cos", "sin", "tan", "acos", "asin", "atan", "minus", "floor", "ceil"]
)
BinaryOperator = common.PPEnum(
    "BinaryOperator",
    ["add", "sub", "mult", "div", "fdiv", "pow", "leq", "lt", "geq", "gt"],
)
EqOperator = common.PPEnum("EqOperator", ["eq", "neq"])
StringOperator = common.PPEnum("StringOperator", ["concat", "length"])
OtherOperator = common.PPEnum("OtherOperator", ["max", "min", "length"])


Bad = common.Bad

# ConditionalOperator = PPEnum("ConditionalOperator", ["default", "if"])
class ConditionalOperator(Enum):
    default = "default"
    IF = "if"
    hasValue = "hasValue"


class CustomOperator(typing.NamedTuple):
    name: clingo.Symbol


class Python(typing.NamedTuple):
    fn: str


Operator = (
    UnaryOperator
    | BinaryOperator
    | EqOperator
    | logic.Operator
    | StringOperator
    | multimap.Operator
    | myset.Operator
    | OtherOperator
    | ConditionalOperator
    | Python
)


constant = bool | float | int | str | types.NoneType | clingo.Symbol


class Val(typing.NamedTuple):
    type_: BaseType | clingo.Symbol
    value: constant

    def __repr__(self):
        return f"Val({str(self.type_)},{str(self.value)})"


class Operation(typing.NamedTuple):
    op: Operator | Variable | Lambda
    args: myClorm.HashableList[Expr]

    def __repr__(self):
        comma = ","
        return f"{self.op}({comma.join(str(arg) for arg in self.args)})"


class Variable(typing.NamedTuple):
    arg: constant

    def __repr__(self):
        return f"{self.arg}"


class Lambda(typing.NamedTuple):
    vars: myClorm.HashableList[clingo.Symbol]
    expr: Expr

    def __repr__(self):
        return f"Lambda({[str(x) for x in self.vars]},{str(self.expr)})"


type ReducedExpr = Bad | Val | frozenset[ReducedExpr] | tuple[ReducedExpr, ...]  # TODO handle Lambda
type Expr = Bad | Variable | Operation | Val | Lambda | frozenset[Expr] | tuple[Expr, ...]
