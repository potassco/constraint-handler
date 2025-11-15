#script(python)

import itertools
import operator
import typing

import clingo

import constraint_handler.myClorm as myClorm
import constraint_handler.evaluator as evaluator


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
    except Exception as exn:
        print(f"pythonEvalExpr: error when converting {(clArgs,clExpr)}: {exn}.")
        return myClorm.pytocl(evaluator.Error(str(exn)))
    try:
        d = { var : evaluator.evaluate_expr(val,dict()) for (var,val) in pArgs }
        prettyD = { str(var) : val for (var,val) in d.items() }
        pRes = evaluator.evaluate_expr(pExpr, d, evaluator.get_environment(pId))
        # print(f"eval expr: {pExpr} = {pRes} assuming {prettyD}")
        pRed = evaluator.reducedExpr(pRes)
        return myClorm.pytocl(pRed)
    except Exception as exn:
        # print(f"pythonEvalExpr: error when evaluating {pExpr} over {clArgs}:\n{exn}.")
        return myClorm.pytocl(evaluator.Error(str(exn)))


def pythonExec(clStmt,clEnv,clOuts,clId):
    try:
        pStmt = myClorm.cltopy(clStmt,evaluator.Stmt)
        pEnv  = myClorm.cltopy(clEnv,list[tuple[evaluator.constant,evaluator.ReducedExpr]])
        pOuts = myClorm.cltopy(clOuts,list[evaluator.constant])
        pId   = myClorm.cltopy(clId)
    except Exception as exn:
        print(f"pythonExec: error when converting {(clStmt,clEnv,clOuts)}: {exn}.")
        return myClorm.pytocl(evaluator.Error(str(exn)))
    try:
        pDict = { x:evaluator.evaluate_expr(v,dict()) for (x,v) in pEnv }
        locals = dict(pDict)
        evaluator.run_stmt(pStmt, locals, evaluator.get_environment(pId))
        results = [True]
        for x in pOuts:
            val = locals[x] if x in locals else None
            results.append((x,evaluator.reducedExpr(val))) # TODO incorrect for set results?
        return map(myClorm.pytocl,results)
    except evaluator.FailIntegrityExn:
        return myClorm.pytocl(evaluator.FailIntegrity())
    except Exception as exn:
        return myClorm.pytocl(evaluator.Error(str(exn)))


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
    # print("pythonEvalExpr",clName,clExpr,clArgs)
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
