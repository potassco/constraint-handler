#script(python)

import itertools
import operator
import typing

import clingo

import constraint_handler.myClorm as myClorm
import constraint_handler.evaluator as evaluator
import constraint_handler.schemas.atom as atom
import constraint_handler.schemas.expression as expression
import constraint_handler.schemas.statement as statement
import constraint_handler.schemas.warning as warning
import constraint_handler.solver_environment as solver_environment


def pythonExpressionVariable(clExpr):
    # print("pythonExpressionVariable",clExpr)
    pExpr = myClorm.cltopy(clExpr,expression.Expr)
    pVars = list(evaluator.collectVars(pExpr))
    clVars = [myClorm.pytocl(var) for var in pVars]
    return clVars

def pythonEnumerateVariables(clExpr):
    pExpr = myClorm.cltopy(clExpr,expression.Expr)
    pVars = list(evaluator.collectVars(pExpr))
    result = [myClorm.pytocl(e) for e in enumerate(pVars)]
    result.append(clingo.Function("length",[clingo.Number(len(pVars))]))
    return result

 # TODO: dead?
def pythonBetaReduction(clExpr,clVars,clArgs):
    pVars = myClorm.cltopy(clVars)
    pArgs = myClorm.cltopy(clArgs,list[expression.Val])
    pExpr = myClorm.cltopy(clExpr,expression.Expr)
    if len(pVars) != len(pArgs):
        print(f"pythonBetaReduction: inconsistent argument lengths for {pExpr}: {pVars} = {pArgs}")
        return []
    d = { var : val for (var,val) in zip(pVars,pArgs) }
    #print(d)
    prettyArgs = ", ".join(f"{str(var)}={val}" for (var,val) in d.items())
    pRes = evaluator.beta_reduction(d,pExpr)
    #print(f"pythonEvalExprFromPairs2: {pExpr}({prettyArgs}) = {pRes}")
    return myClorm.pytocl(pRes)


def pythonEvalExpr(clExpr,clArgs,clId):
    # print("pythonEvalExpr",clExpr,clArgs)
    eval_error = warning.Expression(warning.ExpressionWarning.pythonError)
    try:
        pArgs = myClorm.cltopy(clArgs,list[tuple[typing.Any,expression.ReducedExpr]])
        pExpr = myClorm.cltopy(clExpr,expression.Expr)
        pId   = myClorm.cltopy(clId)
        globals = evaluator.get_environment(pId)
        results = []
        locals = dict()
        for (var,vexpr) in pArgs:
            val,errors = evaluator.evaluate_expr(vexpr,globals)
            locals[var] = val
            for error in errors:
                results.append(warning.Error(eval_error,repr(error)))
        prettyD = { str(var) : val for (var,val) in locals.items() }
        pRes,errors = evaluator.evaluate_expr(pExpr, globals, locals)
        for error in errors:
            results.append(warning.Error(eval_error,repr(error)))
        # print(f"eval expr: {pExpr} = {pRes} assuming {prettyD}\nerrors: {results}")
        results.append(evaluator.reducedExpr(pRes))
        return map(myClorm.pytocl,results)
    except myClorm.FailedInstantiationExn as exn:
        print(f"pythonEvalExpr: error when converting {(clArgs,clExpr)}: {repr(exn)}.")
        return myClorm.pytocl(warning.Error(eval_error,repr(exn)))
    except Exception as exn:
        print(f"pythonEvalExpr: uncaught exception {repr(exn)} in context {(clExpr,clArgs,clId)}")
        return myClorm.pytocl(warning.Error(eval_error,repr(exn)))


def pythonExec(clStmt,clEnv,clId):
    exec_error = warning.Statement(warning.StatementWarning.pythonError)
    try:
        pStmt = myClorm.cltopy(clStmt,statement.Stmt)
        pEnv  = myClorm.cltopy(clEnv,list[tuple[expression.constant,expression.ReducedExpr]])
        pId   = myClorm.cltopy(clId)
        globals = evaluator.get_environment(pId)
        results = []
        locals = dict()
        for (var,vexpr) in pEnv:
            val,errors = evaluator.evaluate_expr(vexpr,globals)
            locals[var] = val
            for error in errors:
                results.append(warning.Error(exec_error,repr(error)))
        # print((pStmt, globals, locals))
        errors = evaluator.evaluate_stmt(pStmt, globals, locals)
        for error in errors:
            results.append(warning.Error(exec_error,repr(error)))
        if not results:
            results.append(True)
        for (x,val) in locals.items():
            try:
                results.append((x,evaluator.reducedExpr(val)))
            except NotImplementedError:
                pass
        return map(myClorm.pytocl,results)
    except solver_environment.FailIntegrityExn:
        return myClorm.pytocl(atom.FailIntegrity())
    except myClorm.FailedInstantiationExn as exn:
        print(f"pythonExec: error when converting {(clStmt,clEnv,clId)}: {repr(exn)}.")
        return myClorm.pytocl(warning.Error(exec_error,str(exn)))
    except Exception as exn:
        print(f"pythonExec: uncaught exception {repr(exn)} in context {(clStmt,clEnv,clId)}")
        return myClorm.pytocl(warning.Error(exec_error,repr(exn)))


def pythonReversed(clExpr):
    pL = myClorm.cltopy(clExpr,list)
    pRL = list(reversed(pL))
    return myClorm.pytocl(pRL)

def pythonListElements(clExpr):
    pL = myClorm.cltopy(clExpr,list)
    return [myClorm.pytocl(e) for e in pL]


def pythonEnumerateElements(clExpr):
    pL = myClorm.cltopy(clExpr,list)
    return [myClorm.pytocl(e) for e in enumerate(pL)]

def pythonListLength(clExpr):
    pL = myClorm.cltopy(clExpr,list)
    return myClorm.pytocl(len(pL))


class Local(typing.NamedTuple):
    name: typing.Any
    var: expression.Variable


def pythonDebug(clExpr):
    #print("debug: ",clExpr)
    return clExpr

def pythonStop(clExpr):
    #print("stop: ",clExpr)
    pExpr = myClorm.cltopy(clExpr)
    if pExpr < -5:
        assert False
    return clExpr

def pythonTagVars(clExpr,clName):
    # print("pythonTagVars",clName,clExpr)
    pName = myClorm.cltopy(clName)
    pExpr = myClorm.cltopy(clExpr,expression.Expr)
    vars = evaluator.collectVars(pExpr)
    map = { var : Local(pName,var) for var in vars }
    pExp2 = evaluator.beta_reduction(map,pExpr)
    return myClorm.pytocl(pExp2)


def pythonInit(clX):
    pX = myClorm.cltopy(clX)
    print("init",pX)
    return []

#end.
