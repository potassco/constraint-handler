from __future__ import annotations

import functools
import math
import operator
from enum import Enum
from typing import NamedTuple

import clingo

# import myPropagators as mp


class PPEnum(Enum):
    def __str__(self):
        return self.name


BaseType = Enum("BaseType", ["int", "float", "str", "symbol", "bool"])
UnaryOperator = PPEnum("UnaryOperator", ["abs", "sqrt", "cos", "sin", "acos", "asin"])
LogicOperator = PPEnum("LogicOperator", ["conj", "disj", "ite", "leqv", "limp", "lnot", "lxor"])
BinaryOperator = PPEnum(
    "BinaryOperator",
    [
        "add",
        "mult",
        "div",
        "eq",
        "neq",
        "leq",
        "lt",
        "geq",
        "gt",
        "isin",
        "notin",
        "union",
        "inter",
    ],
)
OtherOperator = PPEnum("OtherOperator", ["minus", "max", "min", "makeSet", "length"])

noPredConstant = bool | float | int | str | clingo.Symbol
ConstantList = list[noPredConstant]

noPredOperator = UnaryOperator | BinaryOperator | LogicOperator | OtherOperator | str


class Bool(NamedTuple):
    value: bool


class Int(NamedTuple):
    value: int


class Str(NamedTuple):
    value: str


class Symbol(NamedTuple):
    value: clingo.Symbol


class Constant(NamedTuple):
    # value: noPredConstant
    value: Bool | Int | Symbol | float | Str


class Operation(NamedTuple):
    op: Operator
    args: list[Expr]

    def __repr__(self):
        comma = ", "
        return f"{self.op}({comma.join(str(arg) for arg in self.args)})"


class Variable(NamedTuple):
    arg: clingo.Symbol

    def __repr__(self):
        return f"{self.arg}"


class Python(NamedTuple):
    fn: Expr


Expr = Constant | Variable | Operation
Operator = UnaryOperator | BinaryOperator | LogicOperator | OtherOperator | Python


def collectVars(expr):
    match expr:
        case Operation(Python(f), args):
            return collectVars(f) | set.union(*(collectVars(e) for e in args))
        case Operation(o, args):
            return set.union(*(collectVars(e) for e in args))
        case Variable(a):
            return {a}
        case Constant(val):
            return set()


def fromPair(t, r):
    match t:
        case BaseType.float:
            return float(r)
        case BaseType.int:
            return int(r)
        case BaseType.string:
            return str(r)
        case BaseType.bool:
            return bool(r)
        case BaseType.symbol:
            return r


def toPair(pRes):
    (t, r) = None, pRes
    if isinstance(pRes, float):
        t = BaseType.float
        # r = str(pRes)
    elif isinstance(pRes, str):
        t = BaseType.string
    elif isinstance(pRes, int):
        t = BaseType.int
    else:
        print(pRes)
        assert False
    return (t, r)


def evaluate_constant(c):
    match c:
        case Bool(b):
            return b
        case Int(i):
            return i
        case float(f):
            return f
        case Str(s):
            return s
        case Symbol(s):
            return s


def evaluate_unop(o, val):
    match o:
        case UnaryOperator.sqrt:
            return math.sqrt(val)
        case UnaryOperator.cos:
            return math.cos(val)
        case UnaryOperator.sin:
            return math.sin(val)
        case UnaryOperator.acos:
            return math.acos(val)
        case UnaryOperator.asin:
            return math.asin(val)

def evaluate_logic_operator(o, args):
    match o:
        case LogicOperator.conj:
            return all(args)
        case LogicOperator.disj:
            return any(args)
        case LogicOperator.ite:
            assert len(args) == 3
            return args[1] if args[0] else args[2]
        case LogicOperator.leqv:
            return not functools.reduce(operator.xor, args)
        case LogicOperator.limp:
            assert len(args) == 2
            return not args[0] or args[1]
        case LogicOperator.lnot:
            assert len(args) == 1
            return not args[0]
        case LogicOperator.lxor:
            return functools.reduce(operator.xor, args)

def evaluate_binop(o, lval, rval):
    # print(o,l,r,lval,rval)
    match o:
        case BinaryOperator.add:
            return lval + rval
        case BinaryOperator.mult:
            return lval * rval
        case BinaryOperator.div:
            return lval / rval
        case BinaryOperator.eq:
            return lval == rval
        case BinaryOperator.neq:
            return lval != rval
        case BinaryOperator.leq:
            return lval <= rval
        case BinaryOperator.lt:
            return lval < rval
        case BinaryOperator.geq:
            return lval >= rval
        case BinaryOperator.gt:
            return lval > rval
        case BinaryOperator.isin:
            return lval in rval
        case BinaryOperator.notin:
            return lval not in rval


def evaluate_operator(symbols, o, args):
    match o:
        case str(fn):
            call = eval(fn)
            return call(*args)
        case Python(efn):
            fn = evaluate_expr(symbols, efn)
            call = eval(fn)
            # print(f"{fn}{tuple(vals)} = {}")
            return call(*args)
        case LogicOperator(o):
            return evaluate_logic_operator(o, args)
        case OtherOperator.minus:
            assert len(args)
            if len(args) == 1:
                return -args[0]
            else:
                return args[0] - sum(args[1:])
        case OtherOperator.max:
            assert len(args)
            return max(args)
        case OtherOperator.min:
            assert len(args)
            return min(args)
        case o:
            if len(args) == 1:
                return evaluate_unop(o, args[0])
            elif len(args) == 2:
                return evaluate_binop(o, args[0], args[1])
            else:
                print("evaluate_operator.py: undefined {o}")
                assert False


def evaluate_expr(symbols, expr):
    # print("evaluate_expr",symbols,expr)
    match expr:
        case Operation(o, eargs):
            args = [evaluate_expr(symbols, a) for a in eargs]
            return evaluate_operator(symbols, o, args)
        case Variable(a):
            if a in symbols:
                return symbols[a]
            else:
                print(a, symbols)
                print(f"variable {a} is undefined")
                assert False
                raise UnboundVariable
            assert a in self.symbols
            p = self.symbols[a]
            if p.defined:
                return p.assigned
            else:
                raise UnboundVariable
        case Constant(val):
            return evaluate_constant(val)
