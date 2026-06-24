import typing
from collections import defaultdict
from functools import cache

import clingo

import constraint_handler.evaluator as evaluator
import constraint_handler.myClorm as myClorm
import constraint_handler.schemas.expression as expression
import constraint_handler.schemas.internal as internal
import constraint_handler.schemas.type_ as type_
import constraint_handler.schemas.warning as warning
import constraint_handler.utils.python_statement_analysis as python_analysis


@cache
def pythonIsExpr(clE):
    try:
        myClorm.cltopy(clE, expression.Expr)
        return myClorm.pytocl(True)
    except myClorm.FailedInstantiationExn:
        return myClorm.pytocl(False)


@cache
def pythonNormalExpr(clE):
    try:
        pE = myClorm.cltopy(clE, expression.Expr)
        return myClorm.pytocl(pE)
    except myClorm.FailedInstantiationExn:
        return myClorm.pytocl(expression.Bad.bad)


@cache
def pythonExpressionVariable(clExpr):
    try:
        pExpr = myClorm.cltopy(clExpr, expression.Expr)
        pVars = list(evaluator.collectVars(pExpr))
        clVars = sorted([myClorm.pytocl(var) for var in pVars])
        return clVars
    except:
        return []


@cache
def pythonEnumerateVariables(clExpr):
    try:
        pExpr = myClorm.cltopy(clExpr, expression.Expr)
        pVars = list(evaluator.collectVars(pExpr))
        subresult = sorted(myClorm.pytocl(v) for v in pVars)
        result = [clingo.Function("", [clingo.Number(i), e]) for (i, e) in enumerate(subresult)]
        result.append(clingo.Function("length", [clingo.Number(len(pVars))]))
        return result
    except:
        return []


@cache
def pythonBetaReduction(clExpr, clVars, clArgs):
    pVars = myClorm.cltopy(clVars, list)
    pArgs = myClorm.cltopy(clArgs, list[expression.ReducedExpr])
    pExpr = myClorm.cltopy(clExpr, expression.Expr)
    if len(pVars) != len(pArgs):
        print(f"pythonBetaReduction: inconsistent argument lengths for {pExpr}: {pVars} = {pArgs}")
        return []
    d = {var: val for (var, val) in zip(pVars, pArgs)}
    prettyArgs = ", ".join(f"{str(var)}={val}" for (var, val) in d.items())
    pRes = evaluator.beta_reduction(d, pExpr)
    return myClorm.pytocl(internal.Valid(pRes))


@cache
def pythonEvalExpr(clExpr, clArgs, clId):
    try:
        pArgs = myClorm.cltopy(clArgs, list[tuple[typing.Any, expression.ReducedExpr]])
        pExpr = myClorm.cltopy(clExpr, expression.Expr)
        pGlobId = myClorm.cltopy(clId, list[expression.constant])
        results = []
        locals = dict()
        for var, vexpr in pArgs:
            val, errors = evaluator.evaluate_expr(vexpr, pGlobId)
            locals[var] = val
            for kind, msg in errors:
                results.append(warning.Error(kind, msg))
        prettyD = {str(var): val for (var, val) in locals.items()}
        pRes, errors = evaluator.evaluate_expr(pExpr, pGlobId, locals)
        for kind, msg in errors:
            results.append(warning.Error(kind, msg))
        pVal, errors = evaluator.reducedExpr(pRes)
        for kind, msg in errors:
            results.append(warning.Error(kind, msg))
        results.append(internal.Valid(pVal))
        return [myClorm.pytocl(result) for result in results]
    except myClorm.FailedInstantiationExn as exn:
        kind = warning.Expression(warning.ExpressionWarning.pythonError)
        return myClorm.pytocl(warning.Error(kind, repr(exn)))
    except Exception as exn:
        kind = warning.Expression(warning.ExpressionWarning.pythonError)
        return myClorm.pytocl(warning.Error(kind, repr(exn)))


@cache
def pythonStatementVariables(clCode, clInTypes, clId):
    try:
        pCode = myClorm.cltopy(clCode, str)
        pInT = myClorm.cltopy(clInTypes, list[tuple[expression.constant, type_.BaseType]])
        pId = myClorm.cltopy(clId, list[expression.constant])
        globals = evaluator.get_environment(pId)
        tEnv = defaultdict(set)
        for var, t in pInT:
            if isinstance(var, str):
                tEnv[var].add(t)
        results = []
        pyInputs = {x: frozenset((type_.py_type(t),)) for (x, t) in pInT}
        analysis = python_analysis.analyze_python_statement_types(pCode, globals, pyInputs)
        for x, ts in analysis.name_types.items():
            results.append(internal.Valid(x))
        return sorted([myClorm.pytocl(result) for result in results])
    except myClorm.FailedInstantiationExn as exn:
        kind = warning.Statement(warning.StatementWarning.syntaxError)
        return myClorm.pytocl(warning.Error(kind, str(exn)))
    except Exception as exn:
        kind = warning.Statement(warning.StatementWarning.pythonError)
        return myClorm.pytocl(warning.Error(kind, repr(exn)))


# @cache
def pythonTypeExtract(clStmt, clExpr, clArgs, clId):
    try:
        pStmt = myClorm.cltopy(clStmt, str)
        pExpr = myClorm.cltopy(clExpr, str)
        if pExpr == "__succeeds":
            return myClorm.pytocl(internal.Valid(type_.BaseType.bool))
        pArgs = myClorm.cltopy(clArgs, list[tuple[str, type_.BaseType]])
        overallExpr = expression.Operation(expression.PythonExtract(pStmt, pExpr), pArgs)
        pGlobId = myClorm.cltopy(clId, list[expression.constant])
        combined = f"{pStmt}\n__ch_expr = {pExpr}"
        locals = dict()
        locals = defaultdict(set)  # pArgs)
        for v, t in pArgs:
            locals[v].add(type_.py_type(t))
        pyInputs = {x: frozenset(ts) for (x, ts) in locals.items()}
        globals = evaluator.get_environment(pGlobId)
        analysis = python_analysis.analyze_python_statement_types(combined, globals, pyInputs)
        pts = analysis.name_types.get("__ch_expr", None)
        results = [
            warning.Error(warning.Type(warning.TypeWarning.notSupported), (_witness, _reason))
            for _witness, _reason in analysis.unsupported_events
        ]

        if pts is None:
            if not analysis.unsupported_events:
                results.append(warning.Error(warning.Type(warning.TypeWarning.notSupported), overallExpr))
            results.append(internal.Valid(type_.OtherType.top))
        elif len(pts) == 0:
            results.append(internal.Valid(type_.OtherType.bot))
        else:
            for pt in pts:
                cht, errs = type_.ch_type(pt)
                results.append(internal.Valid(cht))
                for err in errs:
                    results.append(warning.Error(err, overallExpr))
        return sorted(map(myClorm.pytocl, results))
    except myClorm.FailedInstantiationExn as exn:
        kind = warning.Expression(warning.ExpressionWarning.pythonError)
        return myClorm.pytocl(warning.Error(kind, repr(exn)))
    except Exception as exn:
        kind = warning.Statement(warning.StatementWarning.syntaxError)
        return myClorm.pytocl(warning.Error(kind, repr(exn)))
