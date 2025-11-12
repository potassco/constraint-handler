from __future__ import annotations

import functools
import math
import operator
from enum import Enum
from typing import NamedTuple
from collections import namedtuple

import clingo

shared_environment = { "math": __import__("math") }
solver_environment = dict()

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

MultimapOperator = PPEnum("MultimapOperator", ["find", "isin", "multimapMake"])


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
    | LogicOperator
    | SetOperator
    | StringOperator
    | MultimapOperator
    | OtherOperator
    | ConditionalOperator
    | Python
)


constant = bool | float | int | str | clingo.Symbol


class Val(NamedTuple):
    type_: BaseType | clingo.Symbol
    value: constant


class Error(NamedTuple):
    message: str


class Operation(NamedTuple):
    op: Operator | Variable
    args: list[Expr]

    def __repr__(self):
        comma = ", "
        return f"{self.op}({comma.join(str(arg) for arg in self.args)})"


class Variable(NamedTuple):
    arg: constant

    def __repr__(self):
        return f"{self.arg}"


class Lambda(NamedTuple):
    vars: list[clingo.Symbol]
    expr: Expr


type ReducedExpr = type(None) | Val | tuple[ReducedExpr, ...] | frozenset[ReducedExpr]  # TODO handle Lambda
type Expr = Variable | Operation | type(None) | Val | Lambda | tuple[Expr, ...] | frozenset[Expr]


class Assign(NamedTuple):
    var: constant
    expr: Expr


class If(NamedTuple):
    cond: Expr
    then: Stmt
    else_: Stmt


class Noop(NamedTuple):
    pass


PythonStmt = namedtuple("Python",["code", "in_vars", "out_vars"])
PythonStmt.__annotations__ = { "code": str, "in_vars": list[constant], "out_vars": list[constant] }
#class PythonStmt(NamedTuple):
#    code: str
#    in_vars: list[clingo.Symbol]
#    out_vars: list[clingo.Symbol]


class Seq2(NamedTuple):
    fst: Stmt
    snd: Stmt


class While(NamedTuple):
    max_iterations: int
    cond: Expr
    body: Stmt


type Stmt = Assign | If | Noop | PythonStmt | Seq2 | While


class SetDeclare(NamedTuple):
    pass


class SetMember(NamedTuple):
    set: frozenset
    value: optConstant


def collectVars(expr) -> set[clingo.Symbol]:
    match expr:
        case Operation(Variable(ov), args):
            return frozenset.union(*(collectVars(e) for e in args + [ov]))
        case Operation(o, args):
            return frozenset.union(*(collectVars(e) for e in args)) if args else frozenset()
        case Variable(a):
            return frozenset({a})
        case Val(t, v):
            return frozenset()
        case Lambda(vars, body):
            return collectVars(body) - frozenset(vars)
        case tuple(args):
            return frozenset.union(*(collectVars(e) for e in args)) if args else frozenset()
        case set(args) | frozenset(args):
            return frozenset.union(*(collectVars(e) for e in args)) if args else frozenset()
        case _:
            print("collectVars", expr)
            assert False


def get_baseType(v):
    if isinstance(v, float):
        return BaseType.float
    elif isinstance(v, str):
        return BaseType.str
    elif isinstance(v, bool):
        return BaseType.bool
    elif isinstance(v, int):
        return BaseType.int
    elif isinstance(v, frozenset):
        return BaseType.set
    elif isinstance(v, clingo.Symbol):
        return BaseType.symbol
    else:
        return None


def reducedExpr(v):
    if isinstance(v, float):
        return Val(BaseType.float, v)
    elif isinstance(v, str):
        return Val(BaseType.str, v)
    elif isinstance(v, bool):
        return Val(BaseType.bool, v)
    elif isinstance(v, int):
        return Val(BaseType.int, v)
    elif isinstance(v, clingo.Symbol):
        return Val(BaseType.symbol, v)
    elif isinstance(v, type(None)):
        return None
    elif isinstance(v, frozenset) or isinstance(v, set):
        return frozenset({reducedExpr(x) for x in v})
    elif isinstance(v, dict):
        raise NotImplementedError("reducedExpr is not implemented for", dict, v)
    else:
        raise NotImplementedError("reducedExpr is not implemented for", v)


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
        case UnaryOperator.abs:
            return abs(val)
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
        case _:
            raise NotImplementedError("evaluate_unop", o)


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
        case _:
            raise NotImplementedError("logic_operator", o)


class HashableDict(dict):
    def __hash__(self):
        return hash(frozenset(self.items()))


def evaluate_multimap_operator(o, args):
    if None in args:
        return None
    match o:
        case MultimapOperator.isin:
            assert len(args) == 2
            return args[0] in args[1]
        case MultimapOperator.find:
            assert len(args) == 2
            return args[1][args[0]] if args[0] in args[1] else None
        case MultimapOperator.multimapMake:
            d = dict()
            for key, value in args:
                if key not in d:
                    d[key] = {value}
                else:
                    d[key].add(value)
            # make sure that singular items are not wrapped in a set?
            # TODO: Is this desired?
            hd = HashableDict()
            for key, value in d.items():
                if len(value) == 1:
                    hd[key] = value.pop()
                else:
                    hd[key] = frozenset(value)
            return hd

            # return HashableDict({key: value for (key, value) in args})
        case _:
            raise NotImplementedError("multimap_operator", o)


def set_fold(f, s, start):
    # print("fold", f, s, start)
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
            return frozenset(args[0].intersection(*args[1:]))
        case SetOperator.subset:
            return args[0].issubset(args[1])
        case SetOperator.fold:
            return set_fold(args[0], args[1], args[2])
        case _:
            raise NotImplementedError("set_operator", o)


def evaluate_string_operator(o, args):
    if None in args:
        return None
    match o:
        case StringOperator.length:
            assert len(args) == 1
            return len(args[0])
        case StringOperator.concat:
            return "".join(args)
        case _:
            raise NotImplementedError("string operator", o)


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
            raise NotImplementedError("binary operator", o)


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
        case _:
            raise NotImplementedError("conditional operator", o)


def evaluate_python_operator(fn, args, globals=None):
    # globals = dict()
    # locals = dict()
    # call = eval(fn,globals,locals)
    try:
        globals = globals if globals else dict()
        call = eval(fn,globals)
        result = call(*args)
    except Exception as exn:
        print(exn)
        raise exn
    return result


def evaluate_operator(symbols, o, args, globals=None):
    match o:
        case Python(fn):
            return evaluate_python_operator(fn, args, globals)
        case Lambda(vars, expr):
            if len(vars) != len(args):
                print(f"evaluate_operator inconsistent parameters and argument lengths for {o}")
                assert False
            symbols2 = dict(symbols)
            for v, e in zip(vars, args):
                symbols2[v] = e
            return evaluate_expr(expr, symbols2, globals)
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


def evaluate_lambda(symbols, vars, args, body, globals=None):
    # print("evaluate_lambda",symbols,vars,args,body)
    d = dict(symbols)
    return evaluate_expr(body, d, globals)


def evaluate_expr(expr, symbols, globals=None):
    match expr:
        case Operation(Variable(ov), eargs):
            assert False  # TODO: handle variable operator
        case Operation(o, eargs):
            args = [evaluate_expr(a, symbols, globals) for a in eargs]
            return evaluate_operator(symbols, o, args, globals)
        case Variable(a):
            if a in symbols:
                return symbols[a]
            else:
                return None
        case Val(type_, val):
            return val
        case Lambda(vars, body):
            return lambda **args: evaluate_lambda(symbols, vars, args, body, globals)
            assert False
            # TODO
        case tuple(eargs):
            args = tuple(evaluate_expr(a, symbols, globals) for a in eargs)
            return args
        case set(eargs) | frozenset(eargs):
            args = frozenset(evaluate_expr(a, symbols, globals) for a in eargs)
            return args
        case None:
            return None
        case _:
            print(expr)
            assert False


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
        case tuple(eargs):
            args = tuple(beta_reduction(symbols, e) for e in eargs)
            return args
        case Operator:
            return expr


type Stmt = Assign | If | Noop | PythonStmt | Seq2 | While


def run_python_stmt(code, symbols, invs, outvs, globals=None):
    try:
        globals = globals if globals else dict()
        locals = dict()
        for x in invs:
            locals[x] = symbols[x] if x in symbols else None
        exec(code,globals,locals)
        for x in outvs:
            symbols[x] = locals[x] if x in locals else None
        return True
    except Exception as exn:
        return Error(str(exn))


def run_stmt(stmt, symbols, globals=None):
    match stmt:
        case Assign(var, expr):
            symbols[var] = evaluate_expr(expr, symbols, globals) #TODO eval?
        case If(cond, stmt1, stmt2):
            if evaluate_expr(cond, symbols, globals): #TODO eval?
                run_stmt(stmt1, symbols, globals)
            else:
                run_stmt(stmt2, symbols, globals)
        case Noop():
            pass
        case PythonStmt(code, invs, outvs):
            run_python_stmt(code, symbols, invs, outvs, globals)
        case Seq2(stmt1, stmt2):
            run_stmt(stmt1, symbols, globals)
            run_stmt(stmt2, symbols, globals)
        case While(maxiter, cond, body):
            iter = 0
            while evaluate_expr(cond, symbols, globals) and iter < maxiter:
                iter += 1
                run_stmt(body, symbols, globals)
        case _:
            print(stmt)
            assert False

def get_environment(identifier):
    global shared_environment
    global solver_environment
    globs = dict(shared_environment)
    if identifier is not None:
        if identifier in solver_environment:
            globs.update(solver_environment[identifier])
        else:
            print(f"undeclared globals for {identifier}")
    return globs

