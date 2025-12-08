from __future__ import annotations

import functools
import importlib
import math
import operator
from collections import namedtuple
from enum import Enum
from typing import NamedTuple

import clingo

import constraint_handler.myClorm as myClorm
from constraint_handler.solver_environment import FailIntegrityExn

shared_environment = {
    "math": importlib.import_module("math"),
    "solver_environment": importlib.import_module("constraint_handler.solver_environment"),
}
solver_environment = dict()


class PPEnum(Enum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name

    def __str__(self):
        return self.name


BaseType = PPEnum("BaseType", ["int", "float", "str", "symbol", "bool", "none", "function", "multimap", "set"])
UnaryOperator = PPEnum("UnaryOperator", ["abs", "sqrt", "cos", "sin", "tan", "acos", "asin", "atan", "minus", "floor"])
LogicOperator = PPEnum("LogicOperator", ["conj", "disj", "ite", "leqv", "limp", "lnot", "lxor", "snot", "wnot"])
BinaryOperator = PPEnum(
    "BinaryOperator",
    ["add", "sub", "mult", "div", "fdiv", "pow", "leq", "lt", "geq", "gt"],
)
EqOperator = PPEnum("LogicOperator", ["eq", "neq"])
SetOperator = PPEnum("SetOperator", ["makeSet", "isin", "notin", "union", "inter", "subset", "set_fold"])
StringOperator = PPEnum("StringOperator", ["concat", "length"])
OtherOperator = PPEnum("OtherOperator", ["minus", "max", "min", "length"])

MultimapOperator = PPEnum("MultimapOperator", ["find", "isin", "multimapMake", "multimap_fold"])


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
    | SetOperator
    | StringOperator
    | MultimapOperator
    | OtherOperator
    | ConditionalOperator
    | Python
)


constant = bool | float | int | str | type(None) | clingo.Symbol


class Val(NamedTuple):
    type_: BaseType | clingo.Symbol
    value: constant

    def __repr__(self):
        return f"Val({str(self.type_)},{str(self.value)})"


class Error(NamedTuple):
    message: str


class FailIntegrity(NamedTuple):
    pass


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


type ReducedExpr = Val | tuple[ReducedExpr, ...] | frozenset[ReducedExpr]  # TODO handle Lambda
type Expr = Variable | Operation | Val | Lambda | tuple[Expr, ...] | frozenset[Expr]


class Set_declare(NamedTuple):
    label: constant
    name: constant


class Set_assign(NamedTuple):
    label: constant
    name: constant
    member: Expr


class Multimap_declare(NamedTuple):
    label: constant
    name: constant


class Multimap_assign(NamedTuple):
    label: constant
    name: constant
    key: Expr
    val: Expr


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


class Execution_declare(NamedTuple):
    label: constant
    name: constant
    body: Stmt
    inputs_vars: list[constant]
    outputs_vars: list[constant]


class Execution_run(NamedTuple):
    label: constant
    name: constant


class FromFacts(NamedTuple):
    pass


class BoolType(NamedTuple):
    pass


class FromList(NamedTuple):
    elements: list[Expr]


type Domain = BoolType | FromFacts | FromList


class Variable_declare(NamedTuple):
    label: constant
    name: constant
    domain: Domain


class Variable_define(NamedTuple):
    label: constant
    name: constant
    value: Expr


class Variable_domain(NamedTuple):
    name: constant
    value: Expr


class Variable_declareOptional(NamedTuple):
    name: constant


class Optimize_maximizeSum(NamedTuple):
    label: constant
    value: Expr
    id: constant


class Optimize_precision(NamedTuple):
    value: Expr


class Value(NamedTuple):
    name: constant
    type_: BaseType | clingo.Symbol
    cst: constant  # ReducedExpr


class Set_value(NamedTuple):
    name: constant
    elt_type_: BaseType | clingo.Symbol
    elt_cst: constant


class Multimap_value(NamedTuple):
    name: constant
    key_type_: BaseType | clingo.Symbol
    key_value: constant
    cst_type_: BaseType | clingo.Symbol
    cst_value: constant


class Warning(NamedTuple):
    content: constant


# class SetMember(NamedTuple):
#     set: frozenset
#     value: optConstant


type SetAtom = Set_declare | Set_assign
type MultimapAtom = Multimap_declare | Multimap_assign
type ExecutionAtom = Execution_declare | Execution_run
type VariableAtom = Variable_declare | Variable_define | Variable_domain
type OptimizeAtom = Optimize_maximizeSum | Optimize_precision
type Atom = ExecutionAtom | MultimapAtom | OptimizeAtom | SetAtom | VariableAtom
type ResultAtom = Value | Set_value | Multimap_value | Warning


AssignAtom = namedtuple("Assign", ["label", "var", "expr"])
AssignAtom.__annotations__ = {"label": constant, "var": constant, "expr": Expr}


class Ensure(NamedTuple):
    label: constant
    expr: Expr


class Evaluate(NamedTuple):
    operator: Operator | Variable
    args: list[Expr]


Main_solverIdentifier = namedtuple("_main_solverIdentifier", ["id"])
Main_solverIdentifier.__annotations__ = {"id": constant}


class Propagator_variable_declare(Variable_declare):
    pass


class Propagator_variable_define(Variable_define):
    pass


class Propagator_variable_domain(Variable_domain):
    pass


class Propagator_variable_declareOptional(Variable_declareOptional):
    pass


class Propagator_assign(AssignAtom):
    pass


class Propagator_ensure(Ensure):
    pass


class Propagator_set_declare(Set_declare):
    pass


class Propagator_set_assign(Set_assign):
    pass


class Propagator_multimap_declare(Multimap_declare):
    pass


class Propagator_multimap_assign(Multimap_assign):
    pass


class Propagator_optimize_maximizeSum(Optimize_maximizeSum):
    pass


class Propagator_execution_declare(Execution_declare):
    pass


class Propagator_execution_run(Execution_run):
    pass


def collectVars(expr) -> set[clingo.Symbol]:
    match expr:
        case Operation(eo, eargs):
            ov = collectVars(eo) if not isinstance(eo, Operator) else frozenset()
            av = frozenset.union(*(collectVars(e) for e in eargs)) if eargs else frozenset()
            return ov | av
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
        return Val(BaseType.none, None)
    elif isinstance(v, frozenset) or isinstance(v, set):
        return frozenset({reducedExpr(x) for x in v})
    elif isinstance(v, dict):
        raise NotImplementedError(f"reducedExpr is not implemented for {dict} {v}")
    elif isinstance(v, Lambda):
        return v
    else:
        raise NotImplementedError(f"reducedExpr is not implemented for {v}")


class HashableDict(dict):
    def __hash__(self):
        return hash(frozenset(self.items()))

    def __repr__(self):
        kv = ", ".join(f"{str(k)}:{str(v)}" for k, v in self.items())
        return f"{{{kv}}}"


def multimap_fold(f, m, start):
    accu = start
    for key in m:
        value = m[key]
        accu = f(value, accu)
        # accu = f((key, value), accu)
    return accu


def set_fold(f, s, start):
    # print("fold", f, s, start)
    accu = start
    for e in s:
        accu = f(e, accu)
    return accu


class Evaluator:
    def __init__(self, globals=None, locals=None):
        self.globals = globals if globals else dict()
        self.locals = locals if locals else dict()
        self.errors = []

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

    def multimap_operator(self, o, args):
        if None in args:
            return None
        match o:
            case MultimapOperator.isin:
                assert len(args) == 2
                return args[0] in args[1]
            case MultimapOperator.find:
                assert len(args) == 2
                return args[1][args[0]] if args[0] in args[1] else None
            case MultimapOperator.multimap_fold:
                o = lambda *aaa: self.operator(args[0], aaa)  # TODO: check
                return multimap_fold(o, args[1], args[2])
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
                self.errors.append(NotImplementedError(f"multimap_operator {o}"))
                return None

    def set_operator(self, o, args):
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
            case SetOperator.set_fold:
                o = lambda *aaa: self.operator(args[0], aaa)
                return set_fold(o, args[1], args[2])
            case _:
                self.errors.append(NotImplementedError(f"set_operator {o}"))
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
            case Python(fn):
                return self.python_operator(fn, args)
            case Lambda(vars, expr):
                if len(vars) != len(args):
                    self.errors.append(f"evaluate_operator inconsistent parameters and argument lengths for {o}")
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
            case MultimapOperator():
                return self.multimap_operator(o, args)
            case SetOperator():
                return self.set_operator(o, args)
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
                if len(args) == 1:
                    return self.unop(o, args[0])
                elif len(args) == 2:
                    return self.binop(o, args[0], args[1])
                else:
                    self.errors.append(NotImplementedError(f"operator {o}"))
                    return None

    def expr(self, expr):
        match expr:
            case Operation(eo, eargs):
                args = [self.expr(a) for a in eargs]
                o = self.expr(eo)
                return self.operator(o, args)
            case Variable(a):
                if a in self.locals:
                    return self.locals[a]  # TODO : and globals?
                else:
                    self.errors.append(NameError(f"variable {a} undefined"))
                    return None
            case Val(type_, val):
                return val
            case Lambda(vars, body):
                nsymbols = {x: v for x, v in self.locals.items() if x not in vars}
                nglobals = dict(self.globals) if self.globals is not None else None
                if self.globals is not None:
                    for x in vars:
                        if x in nglobals:
                            del nglobals[x]
                return Lambda(vars, beta_reduction(nsymbols, body))
            case o if isinstance(o, Operator):
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
            case Assert(expr):
                condition = self.expr(expr)
                if condition != True:
                    raise FailIntegrityExn
            case Assign(var, expr):
                self.locals[var] = self.expr(expr)  # TODO eval?
            case If(cond, stmt1, stmt2):
                if self.expr(cond):
                    self.stmt(stmt1)
                else:
                    self.stmt(stmt2)
            case Noop():
                pass
            case Statement_python(code):
                self.stmt_python(code)
            case Seq2(stmt1, stmt2):
                self.stmt(stmt1)
                self.stmt(stmt2)
            case While(maxiter, cond, body):
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
        case Operation(eo, eargs):
            o = beta_reduction(symbols, eo)
            args = myClorm.HashableList([beta_reduction(symbols, e) for e in eargs])
            return Operation(o, args)
        case Variable(a):
            if a in symbols:
                return symbols[a]
            else:
                return expr
        case Val(type_, val):
            return expr
        case Lambda(vars, body):
            nsymbols = {x: v for x, v in symbols.items() if x not in vars}
            return Lambda(vars, beta_reduction(nsymbols, body))
        case o if isinstance(o, Operator):
            return expr
        case tuple(eargs):
            args = tuple(beta_reduction(symbols, e) for e in eargs)
            return args
        case _:
            print("beta_reduction", expr, symbols, type(expr))
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
