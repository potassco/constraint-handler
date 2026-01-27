from __future__ import annotations

import functools
import importlib
import math
import operator

import clingo

import constraint_handler.multimap as multimap
import constraint_handler.myClorm as myClorm
import constraint_handler.schemas.expression as expression
import constraint_handler.schemas.statement as statement
import constraint_handler.set as myset
from constraint_handler.schemas.expression import (
    BaseType,
    BinaryOperator,
    ConditionalOperator,
    EqOperator,
    LogicOperator,
    OtherOperator,
    StringOperator,
    UnaryOperator,
)
from constraint_handler.solver_environment import FailIntegrityExn

_shared_environment = {
    "math": importlib.import_module("math"),
    "solver_environment": importlib.import_module("constraint_handler.solver_environment"),
}
_solver_environment = dict()


def collectVars(expr) -> frozenset[clingo.Symbol]:
    match expr:
        case expression.Operation(eo, eargs):
            ov = collectVars(eo) if not isinstance(eo, expression.Operator) else frozenset()
            av = frozenset.union(*(collectVars(e) for e in eargs)) if eargs else frozenset()
            return ov | av
        case expression.Variable(a):
            return frozenset({a})
        case expression.Val(t, v):
            return frozenset()
        case expression.Lambda(vars, body):
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
    elif isinstance(v, multimap.HashableDict):
        return BaseType.multimap
    elif isinstance(v, clingo.Symbol):
        return BaseType.symbol
    else:
        return None


def reducedExpr(v):
    if isinstance(v, float):
        return expression.Val(BaseType.float, v)
    elif isinstance(v, str):
        return expression.Val(BaseType.str, v)
    elif isinstance(v, bool):
        return expression.Val(BaseType.bool, v)
    elif isinstance(v, int):
        return expression.Val(BaseType.int, v)
    elif isinstance(v, clingo.Symbol):
        return expression.Val(BaseType.symbol, v)
    elif isinstance(v, type(None)):
        return expression.Val(BaseType.none, None)
    elif isinstance(v, frozenset) or isinstance(v, set):
        return frozenset({reducedExpr(x) for x in v})
    elif isinstance(v, dict):
        raise NotImplementedError(f"reducedExpr is not implemented for {dict} {v}")
    elif isinstance(v, expression.Lambda):
        return v
    else:
        raise NotImplementedError(f"reducedExpr is not implemented for {v}")


class Evaluator:
    def __init__(self, globals=None, locals=None):
        self.globals = globals if globals is not None else dict()
        self.locals = locals if locals is not None else dict()
        self.errors = []
        self.multimap = multimap.Evaluator(self.errors)
        self.set = myset.Evaluator(self.errors)

    def unop(self, o, val):
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
                self.errors.append(NotImplementedError(f"unop {o}"))
                return None

    def logic_operator(self, o, args):
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
                self.errors.append(NotImplementedError(f"logic_operator {o}"))
                return None

    def string_operator(self, o, args):
        if None in args:
            return None
        match o:
            case StringOperator.length:
                if len(args) != 1:
                    self.errors.append(TypeError(f"len takes one argument ({len(args)} were given)"))
                    return None
                return len(args[0])
            case StringOperator.concat:
                return "".join(args)
            case _:
                self.errors.append(NotImplementedError(f"string operator {o}"))
                return None

    def binop(self, o, lval, rval):
        if lval is None or rval is None:
            return None
        match o:
            case BinaryOperator.add:
                return lval + rval
            case BinaryOperator.sub:
                return lval - rval
            case BinaryOperator.mult:
                return lval * rval
            case BinaryOperator.div:
                if rval == 0:
                    self.errors.append(ZeroDivisionError())
                    return None
                return lval // rval
            case BinaryOperator.fdiv:
                if rval == 0:
                    self.errors.append(ZeroDivisionError())
                    return None
                return lval / rval
            case BinaryOperator.pow:
                return lval ** rval  # fmt: skip
            case BinaryOperator.leq:
                return lval <= rval
            case BinaryOperator.lt:
                return lval < rval
            case BinaryOperator.geq:
                return lval >= rval
            case BinaryOperator.gt:
                return lval > rval
            case _:
                self.errors.append(NotImplementedError(f"binary operator {o}"))
                return None

    def eq_operator(self, o, lval, rval):
        match o:
            case EqOperator.eq:
                return lval == rval
            case EqOperator.neq:
                return lval != rval
            case _:
                self.errors.append(NotImplementedError(f"equality operator {o}"))
                return None

    def conditional_operator(self, o, args):
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
                self.errors.append(NotImplementedError(f"conditional operator {o}"))
                return None

    def python_operator(self, fn, args):
        try:
            call = eval(fn, self.globals, self.locals)
            result = call(*args)
        except Exception as exn:
            self.errors.append(exn)
            return None
        return result

    def operator(self, o, args):
        match o:
            case expression.Python(fn):
                return self.python_operator(fn, args)
            case expression.Lambda(vars, expr):
                if len(vars) != len(args):
                    self.errors.append(
                        ValueError(f"evaluate_operator inconsistent parameters and argument lengths for {o}")
                    )
                    return None
                locals = dict(self.locals)
                for v, e in zip(vars, args):
                    locals[v] = e
                env = Evaluator(self.globals, locals)
                return env.expr(expr)
            case EqOperator():
                if len(args) == 2:
                    return self.eq_operator(o, args[0], args[1])
                else:
                    assert False  # TODO
            case LogicOperator():
                return self.logic_operator(o, args)
            case multimap.Operator():
                return self.multimap.operator(o, args)
            case myset.Operator():
                return self.set.operator(o, args)
            case StringOperator():
                return self.string_operator(o, args)
            case ConditionalOperator():
                return self.conditional_operator(o, args)
            case OtherOperator.minus:
                assert len(args)  # TODO error loggin
                if len(args) == 1:
                    return -args[0]
                else:
                    return args[0] - sum(args[1:])
            case OtherOperator.max:
                assert len(args)  # TODO
                return max(args)
            case OtherOperator.min:
                assert len(args)
                return min(args)
            case o:
                foldable = {BinaryOperator.add: sum, BinaryOperator.mult: math.prod}

                if o in foldable:
                    # This makes it possible to use `add` for strings.
                    if len(args) > 0 and isinstance(args[0], str) and o == BinaryOperator.add:
                        return "".join(args)

                    return foldable[o](args)

                if len(args) == 1:
                    return self.unop(o, args[0])
                elif len(args) == 2:
                    return self.binop(o, args[0], args[1])
                else:
                    self.errors.append(NotImplementedError(f"operator {o}"))
                    return None

    def expr(self, expr):
        match expr:
            case expression.Operation(eo, eargs):
                args = [self.expr(a) for a in eargs]
                o = self.expr(eo)
                return self.operator(o, args)
            case expression.Variable(a):
                if a in self.locals:
                    return self.locals[a]  # TODO : and globals?
                else:
                    self.errors.append(NameError(f"variable {a} undefined"))
                    return None
            case expression.Val(type_, val):
                return val
            case expression.Lambda(vars, body):
                nsymbols = {x: v for x, v in self.locals.items() if x not in vars}
                nglobals = dict(self.globals) if self.globals is not None else None
                if self.globals is not None:
                    for x in vars:
                        if x in nglobals:
                            del nglobals[x]
                return expression.Lambda(vars, beta_reduction(nsymbols, body))
            case o if isinstance(o, expression.Operator):
                return expr
            case tuple(eargs):
                args = tuple(self.expr(a) for a in eargs)
                return args
            case set(eargs) | frozenset(eargs):
                args = frozenset(self.expr(a) for a in eargs)
                return args
            case None:
                return None
            case _:
                self.errors.append(NotImplementedError(f"expr {expr}"))
                return None

    def stmt_python(self, code):
        try:
            exec(code, self.globals, self.locals)
        except FailIntegrityExn:
            raise
        except Exception as exn:
            self.errors.append(exn)

    def stmt(self, stmt):
        match stmt:
            case statement.Assert(expr):
                condition = self.expr(expr)
                if condition != True:
                    raise FailIntegrityExn
            case statement.Assign(var, expr):
                self.locals[var] = self.expr(expr)  # TODO eval?
            case statement.If(cond, stmt1, stmt2):
                if self.expr(cond):
                    self.stmt(stmt1)
                else:
                    self.stmt(stmt2)
            case statement.Noop():
                pass
            case statement.Statement_python(code):
                self.stmt_python(code)
            case statement.Seq2(stmt1, stmt2):
                self.stmt(stmt1)
                self.stmt(stmt2)
            case statement.While(maxiter, cond, body):
                iter = 0
                while self.expr(cond) and iter < maxiter:
                    iter += 1
                    self.stmt(body)
            case _:
                self.errors.append(NotImplementedError(f"stmt {stmt}"))


def evaluate_expr(expr, globals=None, locals=None):
    env = Evaluator(globals, locals)
    result = env.expr(expr)
    return result, env.errors


def evaluate_stmt(stmt, globals=None, locals=None):
    env = Evaluator(globals, locals)
    env.stmt(stmt)
    return env.errors


def beta_reduction(symbols, expr):
    match expr:
        case expression.Operation(eo, eargs):
            o = beta_reduction(symbols, eo)
            args = myClorm.HashableList([beta_reduction(symbols, e) for e in eargs])
            return expression.Operation(o, args)
        case expression.Variable(a):
            if a in symbols:
                return symbols[a]
            else:
                return expr
        case expression.Val(type_, val):
            return expr
        case expression.Lambda(vars, body):
            nsymbols = {x: v for x, v in symbols.items() if x not in vars}
            return expression.Lambda(vars, beta_reduction(nsymbols, body))
        case o if isinstance(o, expression.Operator):
            return expr
        case tuple(eargs):
            args = tuple(beta_reduction(symbols, e) for e in eargs)
            return args
        case _:
            print("beta_reduction", expr, symbols, type(expr))
            assert False


def get_environment(identifier):
    global _shared_environment
    global _solver_environment
    globs = dict(_shared_environment)
    if identifier is not None:
        if identifier in _solver_environment:
            globs.update(_solver_environment[identifier])
        else:
            print(f"undeclared globals for {identifier}")
    return globs
