#script(python)

import itertools
import operator
import typing

import clingo

import constraint_handler.myClorm as myClorm
import constraint_handler.evaluator as evaluator
from constraint_handler.solver_environment import FailIntegrityExn


def pythonExpressionVariable(clExpr):
    # print("pythonExpressionVariable",clExpr)
    pExpr = myClorm.cltopy(clExpr,evaluator.Expr)
    pVars = list(evaluator.collectVars(pExpr))
    clVars = [myClorm.pytocl(var) for var in pVars]
    return clVars

 # TODO: dead?
def pythonBetaReduction(clExpr,clVars,clArgs):
    pVars = myClorm.cltopy(clVars)
    pArgs = myClorm.cltopy(clArgs,list[evaluator.Val])
    pExpr = myClorm.cltopy(clExpr,evaluator.Expr)
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
    try:
        pArgs = myClorm.cltopy(clArgs,list[tuple[typing.Any,evaluator.ReducedExpr]])
        pExpr = myClorm.cltopy(clExpr,evaluator.Expr)
        pId   = myClorm.cltopy(clId)
        globals = evaluator.get_environment(pId)
        results = []
        locals = dict()
        for (var,vexpr) in pArgs:
            val,errors = evaluator.evaluate_expr(vexpr,globals)
            locals[var] = val
            for error in errors:
                results.append(evaluator.Error(repr(error)))
        prettyD = { str(var) : val for (var,val) in locals.items() }
        pRes,errors = evaluator.evaluate_expr(pExpr, globals, locals)
        for error in errors:
            results.append(evaluator.Error(repr(error)))
        # print(f"eval expr: {pExpr} = {pRes} assuming {prettyD}\nerrors: {results}")
        results.append(evaluator.reducedExpr(pRes))
        return map(myClorm.pytocl,results)
    except myClorm.FailedInstantiationExn as exn:
        print(f"pythonEvalExpr: error when converting {(clArgs,clExpr)}: {repr(exn)}.")
        return myClorm.pytocl(evaluator.Error(repr(exn)))
    except Exception as exn:
        print(f"pythonEvalExpr: uncaught exception {repr(exn)} in context {(clExpr,clArgs,clId)}")
        return myClorm.pytocl(evaluator.Error(repr(exn)))


def pythonExec(clStmt,clEnv,clId):
    try:
        pStmt = myClorm.cltopy(clStmt,evaluator.Stmt)
        pEnv  = myClorm.cltopy(clEnv,list[tuple[evaluator.constant,evaluator.ReducedExpr]])
        pId   = myClorm.cltopy(clId)
        globals = evaluator.get_environment(pId)
        results = []
        locals = dict()
        for (var,vexpr) in pEnv:
            val,errors = evaluator.evaluate_expr(vexpr,globals)
            locals[var] = val
            for error in errors:
                results.append(evaluator.Error(repr(error)))
        # print((pStmt, globals, locals))
        errors = evaluator.evaluate_stmt(pStmt, globals, locals)
        for error in errors:
            results.append(evaluator.Error(repr(error)))
        if not results:
            results.append(True)
        for (x,val) in locals.items():
            try:
                results.append((x,evaluator.reducedExpr(val)))
            except NotImplementedError:
                pass
        return map(myClorm.pytocl,results)
    except FailIntegrityExn:
        return myClorm.pytocl(evaluator.FailIntegrity())
    except myClorm.FailedInstantiationExn as exn:
        print(f"pythonExec: error when converting {(clStmt,clEnv,clId)}: {repr(exn)}.")
        return myClorm.pytocl(evaluator.Error(str(exn)))
    except Exception as exn:
        print(f"pythonExec: uncaught exception {repr(exn)} in context {(clStmt,clEnv,clId)}")
        return myClorm.pytocl(evaluator.Error(repr(exn)))


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
    var: evaluator.Variable


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
    pExpr = myClorm.cltopy(clExpr,evaluator.Expr)
    vars = evaluator.collectVars(pExpr)
    map = { var : Local(pName,var) for var in vars }
    pExp2 = evaluator.beta_reduction(map,pExpr)
    return myClorm.pytocl(pExp2)


def pythonInit(clX):
    pX = myClorm.cltopy(clX)
    print("init",pX)
    return []

#end.
