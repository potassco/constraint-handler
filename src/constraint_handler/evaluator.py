from __future__ import annotations

import functools
import math
import operator
from enum import Enum
from typing import NamedTuple

import clingo

# import myPropagators as mp


class PPEnum(Enum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name

    def __str__(self):
        return self.name


BaseType = PPEnum("BaseType", ["int", "float", "str", "symbol", "bool", "function", "multimap", "set"])
UnaryOperator = PPEnum("UnaryOperator", ["abs", "sqrt", "cos", "sin", "tan", "acos", "asin", "atan", "minus", "floor"])
LogicOperator = PPEnum("LogicOperator", ["conj", "disj", "ite", "leqv", "limp", "lnot", "lxor", "snot", "wnot"])
BinaryOperator = PPEnum(
    "BinaryOperator",
    ["add", "sub", "mult", "div", "fdiv", "pow", "eq", "neq", "leq", "lt", "geq", "gt"],
)
SetOperator = PPEnum("SetOperator", ["makeSet", "isin", "notin", "union", "inter", "subset", "fold"])
StringOperator = PPEnum("StringOperator", ["concat", "length"])
OtherOperator = PPEnum("OtherOperator", ["minus", "max", "min", "length"])

MultimapOperator = PPEnum("MultimapOperator", ["find", "multimapMake"])


# ConditionalOperator = PPEnum("ConditionalOperator", ["default", "if"])
class ConditionalOperator(Enum):
    default = "default"
    IF = "if"
    hasValue = "hasValue"


noPredConstant = bool | float | int | str | clingo.Symbol
ConstantList = list[noPredConstant]


class CustomOperator(NamedTuple):
    name: clingo.Symbol


class Python(NamedTuple):
    fn: str


Operator = (
    UnaryOperator
    | BinaryOperator
    | LogicOperator
    | SetOperator
    | StringOperator
    | MultimapOperator
    | OtherOperator
    | ConditionalOperator
    | Python
)


class Set(NamedTuple):
    value: list[constant]


constant = bool | float | int | str | Set | clingo.Symbol
optConstant = type(None) | constant
ConstantList = list[optConstant]


class Val(NamedTuple):
    type_: BaseType | clingo.Symbol
    value: bool | int | float | str | set | clingo.Symbol


class Error(NamedTuple):
    message: str


class Operation(NamedTuple):
    op: Operator | Variable
    args: list[Expr]

    def __repr__(self):
        comma = ", "
        return f"{self.op}({comma.join(str(arg) for arg in self.args)})"


class Variable(NamedTuple):
    arg: clingo.Symbol

    def __repr__(self):
        return f"{self.arg}"


class Lambda(NamedTuple):
    vars: list[clingo.Symbol]
    expr: Expr


Expr = Variable | Operation | Val | Lambda


class SetDeclare(NamedTuple):
    pass


class SetAssign(NamedTuple):
    type_: BaseType | clingo.Symbol
    value: bool | int | float | str | clingo.Symbol


def collectVars(expr) -> set[clingo.Symbol]:
    match expr:
        case Operation(Variable(ov), args):
            return frozenset.union(*(collectVars(e) for e in args + [ov]))
        case Operation(o, args):
            return frozenset.union(*(collectVars(e) for e in args))
        case Variable(a):
            return frozenset({a})
        case Val(t, v):
            return frozenset()
        case Lambda(vars, body):
            return collectVars(body) - frozenset(vars)


def get_baseType(v):
    if isinstance(v, float):
        return BaseType.float
    elif isinstance(v, str):
        return BaseType.str
    elif isinstance(v, bool):
        return BaseType.bool
    elif isinstance(v, int):
        return BaseType.int
    elif isinstance(v, set):
        return BaseType.set
    elif isinstance(v, clingo.Symbol):
        return BaseType.symbol
    else:
        return None


def evaluate_unop(o, val):
    match o:
        case UnaryOperator.sqrt:
            return math.sqrt(val)
        case UnaryOperator.cos:
            return math.cos(val)
        case UnaryOperator.sin:
            return math.sin(val)
        case UnaryOperator.tan:
            return math.tan(val)
        case UnaryOperator.acos:
            return math.acos(val)
        case UnaryOperator.asin:
            return math.asin(val)
        case UnaryOperator.atan:
            return math.atan(val)
        case UnaryOperator.minus:
            return -val
        case UnaryOperator.floor:
            return math.floor(val)
        case UnaryOperator.abs:
            return abs(val)
        case _:
            print("unknown operator", o, val)
            assert False


def evaluate_logic_operator(o, args):
    match o:
        case LogicOperator.conj:
            if False in args:
                return False
            elif None in args:
                return None
            else:
                return True
        case LogicOperator.disj:
            if True in args:
                return True
            elif None in args:
                return None
            else:
                return False
        case LogicOperator.ite:
            assert len(args) == 3
            if args[0] is None:
                return None
            return args[1] if args[0] else args[2]
        case LogicOperator.leqv:
            if None in args:
                return None
            return not functools.reduce(operator.xor, args)
        case LogicOperator.limp:
            assert len(args) == 2
            return args[1] if args[0] else True
        case LogicOperator.lnot:
            assert len(args) == 1
            if None in args:
                return None
            return not args[0]
        case LogicOperator.lxor:
            if None in args:
                return None
            return functools.reduce(operator.xor, args)
        case LogicOperator.snot:
            assert len(args) == 1
            if None in args:
                return False
            return not args[0]
        case LogicOperator.wnot:
            assert len(args) == 1
            if None in args:
                return True
            return not args[0]


class HashableDict(dict):
    def __hash__(self):
        return hash(frozenset(self.items()))


def evaluate_multimap_operator(o, args):
    match o:
        case MultimapOperator.find:
            assert len(args) == 2
            return args[1][args[0]]
        case MultimapOperator.multimapMake:
            pairs = [(args[2 * i], args[2 * i + 1]) for i in range(int(len(args) / 2))]
            return HashableDict({key: value for (key, value) in pairs})


def set_fold(f, s, start):
    print("fold", f, s, start)
    accu = start
    for e in s:
        accu = f(e, accu)
    return accu


def evaluate_set_operator(o, args):
    if None in args:
        return None
    match o:
        case SetOperator.makeSet:
            return frozenset(args)
        case SetOperator.isin:
            return args[0] in args[1]
        case SetOperator.notin:
            return args[0] not in args[1]
        case SetOperator.union:
            return frozenset().union(*args)
        case SetOperator.inter:
            return args[0].intersection(*args[1:])
        case SetOperator.subset:
            return args[0].issubset(args[1])
        case SetOperator.fold:
            return set_fold(args[0], args[1], args[2])


def evaluate_string_operator(o, args):
    if None in args:
        return None
    match o:
        case StringOperator.length:
            assert len(args) == 1
            return len(args[0])
        case StringOperator.concat:
            return "".join(args)


def evaluate_binop(o, lval, rval):
    if lval is None or rval is None:
        return None
    # print(o,lval,rval)
    match o:
        case BinaryOperator.add:
            return lval + rval
        case BinaryOperator.sub:
            return lval - rval
        case BinaryOperator.mult:
            return lval * rval
        case BinaryOperator.div:
            return lval // rval
        case BinaryOperator.fdiv:
            return lval / rval
        case BinaryOperator.pow:
            return lval ** rval  # fmt: skip
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
        case _:
            print("unknown operator", o, lval, rval)
            assert False


def evaluate_conditional_operator(o, args):
    match o:
        case ConditionalOperator.default:
            if args[0] is not None:
                return args[0]
            else:
                return args[1]
        case ConditionalOperator.IF:
            if args[0] == True:
                return args[1]
            else:
                return None
        case ConditionalOperator.hasValue:
            return args[0] is not None


def evaluate_operator(symbols, o, args):
    match o:
        case str(fn):
            call = eval(fn)
            return call(*args)
        case Python(fn):
            call = eval(fn)
            # print(f"{fn}{tuple(vals)} = {}")
            return call(*args)
        case Lambda(vars, expr):
            if len(vars) != len(args):
                print(f"evaluate_operator inconsistent parameters and argument lengths for {o}")
                assert False
            symbols2 = dict(symbols)
            for v, e in zip(vars, args):
                symbols2[v] = e
            return evaluate_expr(symbols2, expr)
        case LogicOperator():
            return evaluate_logic_operator(o, args)
        case MultimapOperator():
            return evaluate_multimap_operator(o, args)
        case SetOperator():
            return evaluate_set_operator(o, args)
        case StringOperator():
            return evaluate_string_operator(o, args)
        case ConditionalOperator():
            return evaluate_conditional_operator(o, args)
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
                print(f"evaluate_operator.py: undefined {o}")
                assert False


def evaluate_lambda(symbols, vars, args, body):
    # print("evaluate_lambda",symbols,vars,args,body)
    d = dict(symbols)
    return evaluate_expr(d, body)


def evaluate_expr(symbols, expr):
    match expr:
        case Operation(Variable(ov), eargs):
            assert False  # TODO: handle variable operator
        case Operation(o, eargs):
            args = [evaluate_expr(symbols, a) for a in eargs]
            return evaluate_operator(symbols, o, args)
        case Variable(a):
            if a in symbols:
                return symbols[a]
            else:
                return None
        case Val(type_, val):
            return val
        case Lambda(vars, body):
            return lambda **args: evaluate_lambda(symbols, vars, args, body)
            assert False
            # TODO


def beta_reduction(symbols, expr):
    match expr:
        case Operation(eo, eargs):
            o = beta_reduction(symbols, eo)
            args = [beta_reduction(symbols, e) for e in eargs]
            return Operation(o, args)
        case Variable(a):
            if a in symbols:
                return symbols[a]
            else:
                return expr
        case Val(type_, val):
            return expr
        case Lambda(vars, body):
            return expr  # TODO should we do replacements inside body?
        case Operator:
            return expr
