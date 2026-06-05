from __future__ import annotations

import importlib
from functools import cache

import clingo

import constraint_handler.arithmetic as arithmetic
import constraint_handler.logic as logic
import constraint_handler.multimap as multimap
import constraint_handler.myClorm as myClorm
import constraint_handler.schemas.expression as expression
import constraint_handler.schemas.statement as statement
import constraint_handler.schemas.warning as warning
import constraint_handler.set as myset
import constraint_handler.solver_environment as solver_environment
import constraint_handler.utils.python_statement_analysis as python_analysis
from constraint_handler.schemas.expression import (
    ConditionalOperator,
    EqOperator,
    OtherOperator,
    StringOperator,
)
from constraint_handler.schemas.type_ import BaseType

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
        case expression.Python(code):
            return frozenset()
        case expression.PythonExtract(stmt, eval_expr):
            return frozenset()
            # return frozenset.union(*(collectVars(e) for (_,e) in vars)) if vars else frozenset()
        case tuple(args):
            return frozenset.union(*(collectVars(e) for e in args)) if args else frozenset()
        case set(args) | frozenset(args):
            return frozenset.union(*(collectVars(e) for e in args)) if args else frozenset()
        case expression.Bad.bad:
            return frozenset()
        case _:
            print("collectVars", expr)
            assert False


def collectStmtVars(stmt) -> frozenset[clingo.Symbol]:
    match stmt:
        case statement.Assert(_):
            return frozenset()
        case statement.Assign(a, _):
            return frozenset({a})
        case statement.If(_, t, e):
            return collectStmtVars(t) | collectStmtVars(e)
        case statement.Noop():
            return frozenset()
        case statement.Statement_python(code):
            analysis = python_analysis.analyze_python_statement_types(code, {}, {})
            return frozenset(analysis.name_types)
        case statement.Seq2(l, r):
            return collectStmtVars(l) | collectStmtVars(r)
        case _:
            print("collectStmtVars", stmt)
            assert False


def get_baseType(v):
    if isinstance(v, float):
        return BaseType.float
    elif isinstance(v, str):
        return BaseType.string
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
    elif v is None:
        return BaseType.none
    else:
        raise NotImplementedError(f"get_baseType is not implemented for {v}")


def reducedExpr(v):
    if isinstance(v, float):
        return expression.Val(BaseType.float, v)
    elif isinstance(v, str):
        return expression.Val(BaseType.string, v)
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
    elif isinstance(v, expression.Bad):
        return v
    elif isinstance(v, tuple):
        return tuple(reducedExpr(x) for x in v)
    else:
        raise NotImplementedError(f"reducedExpr is not implemented for {v}")


class Evaluator:
    def __init__(self, globals=None, locals=None):
        self.globals = globals if globals is not None else dict()
        self.locals = locals if locals is not None else dict()
        self.errors = []
        self.arithmetic = arithmetic.Evaluator(Evaluator, self.errors)
        self.logic = logic.Evaluator(Evaluator, self.errors)
        self.multimap = multimap.Evaluator(Evaluator, self.errors)
        self.set = myset.Evaluator(Evaluator, self.errors)

    def string_operator(self, o, args):
        match o:
            case StringOperator.length:
                if len(args) != 1:
                    self.errors.append(
                        (
                            warning.Expression(warning.ExpressionWarning.syntaxError),
                            f"len takes one argument ({len(args)} were given)",
                        )
                    )
                    return expression.Bad.bad
                return len(args[0])
            case StringOperator.concat:
                return "".join(args)
            case _:
                self.errors.append(
                    (warning.Expression(warning.ExpressionWarning.notImplemented), f"string operator {o}")
                )
                return expression.Bad.bad

    def eq_operator(self, o, lval, rval):
        match o:
            case EqOperator.eq:
                return lval == rval
            case EqOperator.neq:
                return lval != rval
            case _:
                self.errors.append(
                    (warning.Expression(warning.ExpressionWarning.notImplemented), f"equality operator {o}")
                )
                return expression.Bad.bad

    def conditional_operator(self, o, args):
        match o:
            case ConditionalOperator.default:
                if args[0] is not None:
                    return args[0]
                else:
                    return args[1]
            case ConditionalOperator.IF:
                if args[0] is expression.Bad.bad:
                    return expression.Bad.bad
                elif args[0] == True:
                    return args[1]
                else:
                    return None
            case ConditionalOperator.hasValue:
                return args[0] is not None
            case _:
                self.errors.append(
                    (warning.Expression(warning.ExpressionWarning.notImplemented), f"conditional operator {o}")
                )
                return expression.Bad.bad

    def python_operator(self, fn, args):
        try:
            call = eval(fn, self.globals, self.locals)
            result = call(*args)
        except Exception as exn:
            kind = warning.Expression(warning.ExpressionWarning.pythonError)
            self.errors.append((kind, repr(exn)))
            return None
        return result

    def pythonExtract_operator(self, stmt: str, expr_code: str, vars_mapping: list):
        binding_error_count = len(self.errors)
        locals_env = {name: val for name, val in vars_mapping}
        if len(self.errors) > binding_error_count or any(value == expression.Bad.bad for value in locals_env.values()):
            return expression.Bad.bad

        nested = Evaluator(self.globals, locals_env)
        try:
            nested.stmt_python(stmt)
            __succeeds = True
        except solver_environment.FailIntegrityExn:
            __succeeds = False
        # print(f"05-12 hello\nsucc {__succeeds}\n{stmt}\n{expr_code}\nerrors {nested.errors}")
        self.errors.extend(nested.errors)
        if nested.errors:
            return expression.Bad.bad
        elif expr_code == "__succeeds":
            return __succeeds
        else:
            try:
                return eval(get_compiled_eval(expr_code), nested.globals, nested.locals)
            except Exception as exn:
                kind = warning.Expression(warning.ExpressionWarning.pythonError)
                self.errors.append((kind, repr(exn)))
                return expression.Bad.bad

    def operator(self, o, args):
        match o:
            case expression.Bad.bad:
                return o
            case expression.Python(fn):
                return self.python_operator(fn, args)
            case expression.PythonExtract(stmt, expr):
                return self.pythonExtract_operator(stmt, expr, args)
            case expression.Lambda(vars, expr):
                if len(vars) != len(args):
                    self.errors.append(
                        (
                            warning.Expression(warning.ExpressionWarning.syntaxError),
                            ValueError(f"evaluate_operator inconsistent parameters and argument lengths for {o}"),
                        )
                    )
                    return expression.Bad.bad
                locals = dict(self.locals)
                for v, e in zip(vars, args):
                    locals[v] = e
                env = Evaluator(self.globals, locals)
                return env.expr(expr)
            case EqOperator():
                if len(args) == 2:
                    return self.eq_operator(o, args[0], args[1])
                else:
                    self.errors.append(
                        (
                            warning.Expression(warning.ExpressionWarning.syntaxError),
                            ValueError(f"eq takes two arguments, not {args}"),
                        )
                    )
                    return expression.Bad.bad
            case arithmetic.Operator():
                return self.arithmetic.operator(o, args)
            case logic.Operator():
                return self.logic.operator(o, args)
            case multimap.Operator():
                return self.multimap.operator(o, args)
            case myset.Operator():
                return self.set.operator(o, args)
            case StringOperator():
                return self.string_operator(o, args)
            case ConditionalOperator():
                return self.conditional_operator(o, args)
            case OtherOperator.max:
                assert len(args)  # TODO
                return max(args)
            case OtherOperator.min:
                assert len(args)
                return min(args)
            case _:
                if callable(o):
                    return o(*args)
                else:
                    print(o, type(o))
                    self.errors.append((warning.Expression(warning.ExpressionWarning.notImplemented), f"operator {o}"))
                    return expression.Bad.bad

    def expr(self, expr):
        match expr:
            case expression.Operation(eo, eargs):
                args = [self.expr(a) for a in eargs]
                o = self.expr(eo)

                recoverable = [
                    logic.Operator.conj,
                    logic.Operator.disj,
                    logic.Operator.limp,
                    logic.Operator.ite,
                    ConditionalOperator.IF,
                    ConditionalOperator.default,
                    arithmetic.Operator.pow,
                ]

                if expression.Bad.bad == eo or (expression.Bad.bad in args and o not in recoverable):
                    return expression.Bad.bad
                return self.operator(o, args)
            case expression.Variable(a):
                if a in self.locals:
                    return self.locals[a]  # TODO : and globals?
                else:
                    self.errors.append((warning.Variable(warning.VariableWarning.undeclared), f"{a}"))
                    return expression.Bad.bad
            case expression.Python(code):
                try:
                    result = eval(get_compiled_eval(code), self.globals, self.locals)
                    return result
                except Exception as exn:
                    kind = warning.Expression(warning.ExpressionWarning.pythonError)
                    self.errors.append((kind, repr(exn)))
                    return expression.Bad.bad
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
            case expression.Bad.bad:
                return expr
            case _:
                self.errors.append(
                    (warning.Expression(warning.ExpressionWarning.notImplemented), NotImplementedError(f"expr {expr}"))
                )
                return expression.Bad.bad

    def stmt_python(self, code):
        try:
            exec(get_compiled_exec(code), self.globals, self.locals)
        except solver_environment.FailIntegrityExn:
            raise
        except Exception as exn:
            kind = warning.Statement(warning.StatementWarning.pythonError)
            self.errors.append((kind, repr(exn)))

    def stmt(self, stmt):
        match stmt:
            case statement.Assert(expr):
                condition = self.expr(expr)
                if condition == expression.Bad.bad:
                    assert self.errors
                    return
                if condition != True:
                    raise solver_environment.FailIntegrityExn
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
            case _:
                self.errors.append((warning.Statement(warning.StatementWarning.notImplemented), f"{stmt}"))


def evaluate_expr(expr, globals=None, locals=None):
    env = Evaluator(globals, locals)
    try:
        result = env.expr(expr)
        # print("05-12 goodbye",expr,env.errors)
    except Exception as exn:
        env.errors.append((warning.Expression(warning.ExpressionWarning.evaluatorError), repr(exn)))
        return expression.Bad.bad, env.errors
    return result, env.errors


def evaluate_stmt(stmt, globals=None, locals=None):
    env = Evaluator(globals, locals)
    try:
        env.stmt(stmt)
    except solver_environment.FailIntegrityExn:
        raise solver_environment.FailIntegrityExn
    except Exception as exn:
        kind = warning.Statement(warning.StatementWarning.evaluatorError)
        env.errors.append((kind, repr(exn)))
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
        # case expression.PythonExtract(vars, stmt, eval_expr):
        #     nvars = [(a,beta_reduction(symbols, e)) for (a,e) in vars]
        #     return expression.PythonExtract(nvars, stmt, eval_expr)
        case o if isinstance(o, expression.Operator):
            return expr
        case tuple(eargs):
            args = tuple(beta_reduction(symbols, e) for e in eargs)
            return args
        case expression.Bad.bad:
            return expr
        case _:
            print("beta_reduction", expr, symbols, type(expr))
            assert False


def get_environment(identifiers):
    global _shared_environment
    global _solver_environment
    globs = dict(_shared_environment)
    for identifier in identifiers:
        if identifier in _solver_environment:
            globs.update(_solver_environment[identifier])
        else:
            print(f"undeclared globals for {identifier}")
    return globs


@cache
def get_compiled_eval(code: str):
    return compile(code, "<string>", "eval")


@cache
def get_compiled_exec(code: str):
    return compile(code, "<string>", "exec")
