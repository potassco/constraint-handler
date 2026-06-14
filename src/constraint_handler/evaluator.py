from __future__ import annotations

import importlib
from functools import cache

import clingo

import constraint_handler.arithmetic as arithmetic
import constraint_handler.logic as logic
import constraint_handler.multimap as multimap
import constraint_handler.myClorm as myClorm
import constraint_handler.schemas.atom as atom
import constraint_handler.schemas.expression as expression
import constraint_handler.schemas.operators as operators
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


NO_ERRORS: tuple[tuple[warning.Kind, str], ...] = ()


def exprs(eargs, globals_env, locals_env):
    values, errors = [], []
    for arg in eargs:
        arg_result = expr(arg, globals_env, locals_env)
        values.append(arg_result.value)
        errors.extend(arg_result.errors)
    return (values, tuple(errors))


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


def reducedExprAux(v):
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
        return frozenset({reducedExprAux(x) for x in v})
    elif isinstance(v, dict):
        raise NotImplementedError(f"reducedExpr is not implemented for {dict} {v}")
    elif isinstance(v, expression.Lambda):
        return v
    elif isinstance(v, expression.Bad):
        return v
    elif isinstance(v, tuple):
        return tuple(reducedExprAux(x) for x in v)
    else:
        raise NotImplementedError(f"reducedExpr is not implemented for {v}")


def reducedExpr(v):
    try:
        result = reducedExprAux(v)
        return (result, [])
    except NotImplementedError as exn:
        warn = warning.Expression(warning.ExpressionWarning.notImplemented)
        return (expression.Bad.bad, ((warn, repr(exn)),))


def string_operator(o, args):
    match o:
        case StringOperator.length:
            if len(args) != 1:
                return atom.EvalResult(
                    expression.Bad.bad,
                    (
                        (
                            warning.Expression(warning.ExpressionWarning.syntaxError),
                            f"len takes one argument ({len(args)} were given)",
                        ),
                    ),
                )
            return atom.EvalResult(len(args[0]), NO_ERRORS)
        case StringOperator.concat:
            return atom.EvalResult("".join(args), NO_ERRORS)
        case _:
            return atom.EvalResult(
                expression.Bad.bad,
                ((warning.Expression(warning.ExpressionWarning.notImplemented), f"string operator {o}"),),
            )


def eq_operator(o, lval, rval):
    match o:
        case EqOperator.eq:
            return atom.EvalResult(lval == rval, NO_ERRORS)
        case EqOperator.neq:
            return atom.EvalResult(lval != rval, NO_ERRORS)
        case _:
            return atom.EvalResult(
                expression.Bad.bad,
                ((warning.Expression(warning.ExpressionWarning.notImplemented), f"equality operator {o}"),),
            )


def conditional_operator(o, args):
    match o:
        case ConditionalOperator.default:
            return atom.EvalResult(args[0] if args[0] is not None else args[1], NO_ERRORS)
        case ConditionalOperator.IF:
            if args[0] is expression.Bad.bad:
                return atom.EvalResult(expression.Bad.bad, NO_ERRORS)
            if args[0] is True:
                return atom.EvalResult(args[1], NO_ERRORS)
            return atom.EvalResult(None, NO_ERRORS)
        case ConditionalOperator.hasValue:
            return atom.EvalResult(args[0] is not None, NO_ERRORS)
        case _:
            return atom.EvalResult(
                expression.Bad.bad,
                ((warning.Expression(warning.ExpressionWarning.notImplemented), f"conditional operator {o}"),),
            )


def python_operator(fn, args, globals_env, locals_env):
    try:
        call = eval(fn, globals_env, locals_env)
        return atom.EvalResult(call(*args), NO_ERRORS)
    except Exception as exn:
        kind = warning.Expression(warning.ExpressionWarning.pythonError)
        return atom.EvalResult(None, ((kind, repr(exn)),))


def pythonExtract_operator(stmt: str, expr_code: str, vars_mapping: list, globals_env):
    locals_env = {name: val for name, val in vars_mapping}
    if any(value == expression.Bad.bad for value in locals_env.values()):
        return atom.EvalResult(expression.Bad.bad, NO_ERRORS)

    nested_globals = dict(globals_env)
    nested_locals = dict(locals_env)
    try:
        exec(get_compiled_exec(stmt), nested_globals, nested_locals)
        succeeds = True
    except solver_environment.FailIntegrityExn:
        succeeds = False
    except Exception as exn:
        kind = warning.Expression(warning.ExpressionWarning.pythonError)
        return atom.EvalResult(expression.Bad.bad, ((kind, repr(exn)),))

    if expr_code == "__succeeds":
        return atom.EvalResult(succeeds, NO_ERRORS)

    try:
        return atom.EvalResult(
            eval(get_compiled_eval(expr_code), nested_globals, nested_locals),
            NO_ERRORS,
        )
    except Exception as exn:
        kind = warning.Expression(warning.ExpressionWarning.pythonError)
        return atom.EvalResult(expression.Bad.bad, ((kind, repr(exn)),))


def operator(o, args, globals_env, locals_env):
    def apply_nested_operator(inner_o, inner_args):
        return operator(inner_o, inner_args, globals_env, locals_env)

    match o:
        case expression.Bad.bad:
            return atom.EvalResult(o, NO_ERRORS)
        case expression.Python(fn):
            return python_operator(fn, args, globals_env, locals_env)
        case expression.PythonExtract(stmt, e):
            return pythonExtract_operator(stmt, e, args, globals_env)
        case expression.Lambda(vars, expr_body):
            if len(vars) != len(args):
                return atom.EvalResult(
                    expression.Bad.bad,
                    (
                        (
                            warning.Expression(warning.ExpressionWarning.syntaxError),
                            f"evaluate_operator inconsistent parameters and argument lengths for {o}",
                        ),
                    ),
                )
            nested_locals = dict(locals_env)
            for var, value in zip(vars, args):
                nested_locals[var] = value
            return expr(expr_body, globals_env, nested_locals)
        case EqOperator():
            if len(args) != 2:
                return atom.EvalResult(
                    expression.Bad.bad,
                    (
                        (
                            warning.Expression(warning.ExpressionWarning.syntaxError),
                            f"eq takes two arguments, not {args}",
                        ),
                    ),
                )
            return eq_operator(o, args[0], args[1])
        case operators.ArithmeticOperator():
            # iargs = (0 if arg is False or arg is None else 1 if arg is True else arg for arg in args)
            # return arithmetic.evaluate_operator(o, list(iargs))
            return arithmetic.evaluate_operator(o, args)
        case operators.LogicOperator():
            return logic.evaluate_operator(o, args)
        case operators.MultimapOperator():
            return multimap.evaluate_operator(o, args, apply_operator=apply_nested_operator)
        case operators.SetOperator():
            return myset.evaluate_operator(o, args, apply_operator=apply_nested_operator)
        case StringOperator():
            return string_operator(o, args)
        case ConditionalOperator():
            return conditional_operator(o, args)
        case OtherOperator.max:
            assert len(args)  # TODO
            return atom.EvalResult(max(args), NO_ERRORS)
        case OtherOperator.min:
            assert len(args)
            return atom.EvalResult(min(args), NO_ERRORS)
        case _:
            if callable(o):
                return atom.EvalResult(o(*args), NO_ERRORS)
            print(o, type(o))
            return atom.EvalResult(
                expression.Bad.bad,
                ((warning.Expression(warning.ExpressionWarning.notImplemented), f"operator {o}"),),
            )


def expr(expr_, globals_env, locals_env):
    match expr_:
        case expression.Operation(eo, eargs):
            args, args_errors = exprs(eargs, globals_env, locals_env)
            op_result = expr(eo, globals_env, locals_env)
            o = op_result.value

            recoverable = [
                operators.LogicOperator.conj,
                operators.LogicOperator.disj,
                operators.LogicOperator.limp,
                operators.LogicOperator.ite,
                ConditionalOperator.IF,
                ConditionalOperator.default,
                operators.ArithmeticOperator.pow,
            ]

            if expression.Bad.bad == eo or (expression.Bad.bad in args and o not in recoverable):
                return atom.EvalResult(expression.Bad.bad, op_result.errors + args_errors)

            applied = operator(o, args, globals_env, locals_env)
            return atom.EvalResult(applied.value, op_result.errors + args_errors + applied.errors)
        case expression.Variable(a):
            if a in locals_env:
                return atom.EvalResult(locals_env[a], NO_ERRORS)
            return atom.EvalResult(
                expression.Bad.bad,
                ((warning.Variable(warning.VariableWarning.undeclared), f"{a}"),),
            )
        case expression.Python(code):
            try:
                return atom.EvalResult(eval(get_compiled_eval(code), globals_env, locals_env), NO_ERRORS)
            except Exception as exn:
                kind = warning.Expression(warning.ExpressionWarning.pythonError)
                return atom.EvalResult(expression.Bad.bad, ((kind, repr(exn)),))
        case expression.Val(type_, val):
            return atom.EvalResult(val, NO_ERRORS)
        case expression.Lambda(vars, body):
            nsymbols = {x: v for x, v in locals_env.items() if x not in vars}
            return atom.EvalResult(expression.Lambda(vars, beta_reduction(nsymbols, body)), NO_ERRORS)
        case o if isinstance(o, expression.Operator):
            return atom.EvalResult(expr_, NO_ERRORS)
        case tuple(eargs):
            values, errors = exprs(eargs, globals_env, locals_env)
            return atom.EvalResult(tuple(values), errors)
        case set(eargs) | frozenset(eargs):
            values, errors = exprs(eargs, globals_env, locals_env)
            return atom.EvalResult(frozenset(values), errors)
        case None:
            return atom.EvalResult(None, NO_ERRORS)
        case expression.Bad.bad:
            return atom.EvalResult(expr_, NO_ERRORS)
        case _:
            return atom.EvalResult(
                expression.Bad.bad,
                ((warning.Expression(warning.ExpressionWarning.notImplemented), f"expr {expr_}"),),
            )


def stmt_python(code, globals_env, locals_env, errors):
    try:
        exec(get_compiled_exec(code), globals_env, locals_env)
    except solver_environment.FailIntegrityExn:
        raise
    except Exception as exn:
        kind = warning.Statement(warning.StatementWarning.pythonError)
        errors.append((kind, repr(exn)))


def stmt(stmt_, globals_env, locals_env, errors):
    match stmt_:
        case statement.Assert(e):
            evaluated = expr(e, globals_env, locals_env)
            errors.extend(evaluated.errors)
            condition = evaluated.value
            if condition == expression.Bad.bad:
                return
            if condition != True:
                raise solver_environment.FailIntegrityExn
        case statement.Assign(var, e):
            evaluated = expr(e, globals_env, locals_env)
            errors.extend(evaluated.errors)
            locals_env[var] = evaluated.value
        case statement.If(cond, stmt1, stmt2):
            evaluated = expr(cond, globals_env, locals_env)
            errors.extend(evaluated.errors)
            if evaluated.value:
                stmt(stmt1, globals_env, locals_env, errors)
            else:
                stmt(stmt2, globals_env, locals_env, errors)
        case statement.Noop():
            return
        case statement.Statement_python(code):
            stmt_python(code, globals_env, locals_env, errors)
        case statement.Seq2(stmt1, stmt2):
            stmt(stmt1, globals_env, locals_env, errors)
            stmt(stmt2, globals_env, locals_env, errors)
        case _:
            errors.append((warning.Statement(warning.StatementWarning.notImplemented), f"{stmt_}"))


def evaluate_expr(e, globals=None, locals=None):
    globs = globals if globals is not None else dict()
    locs = locals if locals is not None else dict()

    try:
        result = expr(e, globs, locs)
    except Exception as exn:
        return expression.Bad.bad, [(warning.Expression(warning.ExpressionWarning.evaluatorError), repr(exn))]
    return result.value, list(result.errors)


def evaluate_stmt(s, globals=None, locals=None):
    globs = globals if globals is not None else dict()
    locs = locals if locals is not None else dict()
    errors = []
    try:
        stmt(s, globs, locs, errors)
    except solver_environment.FailIntegrityExn:
        raise
    except Exception as exn:
        kind = warning.Statement(warning.StatementWarning.evaluatorError)
        errors.append((kind, repr(exn)))
    return errors


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
