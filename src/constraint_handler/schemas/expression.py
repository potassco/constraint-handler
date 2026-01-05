from __future__ import annotations

from enum import Enum
from typing import NamedTuple
import types

import clingo

import constraint_handler.multimap as multimap
import constraint_handler.myClorm as myClorm
import constraint_handler.set as myset
from constraint_handler.utils.common import PPEnum

BaseType = PPEnum("BaseType", ["int", "float", "str", "symbol", "bool", "none", "function", "multimap", "set"])
UnaryOperator = PPEnum("UnaryOperator", ["abs", "sqrt", "cos", "sin", "tan", "acos", "asin", "atan", "minus", "floor"])
LogicOperator = PPEnum("LogicOperator", ["conj", "disj", "ite", "leqv", "limp", "lnot", "lxor", "snot", "wnot"])
BinaryOperator = PPEnum(
    "BinaryOperator",
    ["add", "sub", "mult", "div", "fdiv", "pow", "leq", "lt", "geq", "gt"],
)
EqOperator = PPEnum("LogicOperator", ["eq", "neq"])
StringOperator = PPEnum("StringOperator", ["concat", "length"])
OtherOperator = PPEnum("OtherOperator", ["minus", "max", "min", "length"])


# ConditionalOperator = PPEnum("ConditionalOperator", ["default", "if"])
class ConditionalOperator(Enum):
    default = "default"
    IF = "if"
    hasValue = "hasValue"


class CustomOperator(NamedTuple):
    name: clingo.Symbol


class Python(NamedTuple):
    fn: str


Operator = (
    UnaryOperator
    | BinaryOperator
    | EqOperator
    | LogicOperator
    | StringOperator
    | multimap.Operator
    | myset.Operator
    | OtherOperator
    | ConditionalOperator
    | Python
)


constant = bool | float | int | str | types.NoneType | clingo.Symbol


class Val(NamedTuple):
    type_: BaseType | clingo.Symbol
    value: constant

    def __repr__(self):
        return f"Val({str(self.type_)},{str(self.value)})"


class Operation(NamedTuple):
    op: Operator | Variable | Lambda
    args: myClorm.HashableList[Expr]

    def __repr__(self):
        comma = ","
        return f"{self.op}({comma.join(str(arg) for arg in self.args)})"


class Variable(NamedTuple):
    arg: constant

    def __repr__(self):
        return f"{self.arg}"


class Lambda(NamedTuple):
    vars: myClorm.HashableList[clingo.Symbol]
    expr: Expr

    def __repr__(self):
        return f"Lambda({[str(x) for x in self.vars]},{str(self.expr)})"


type ReducedExpr = Val | frozenset[ReducedExpr] | tuple[ReducedExpr, ...]  # TODO handle Lambda
type Expr = Variable | Operation | Val | Lambda | frozenset[Expr] | tuple[Expr, ...]
