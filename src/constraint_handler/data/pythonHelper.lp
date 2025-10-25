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

def pythonEvalExpr(clExpr,clArgs):
    # print("pythonEvalExpr",clExpr,clArgs)
    try:
        pArgs = myClorm.cltopy(clArgs,list[tuple[typing.Any,evaluator.ReducedExpr]])
        pExpr = myClorm.cltopy(clExpr,evaluator.Expr)
    except Exception as exn:
        print(f"pythonEvalExpr: error when converting {(clArgs,clExpr)}: {exn}.")
        return myClorm.pytocl(evaluator.Error(str(exn)))
    try:
        d = { var : evaluator.evaluate_expr(dict(),val) for (var,val) in pArgs }
        prettyArgs = "assuming " + ", ".join(f"{str(var)}={val}" for (var,val) in pArgs) + ", " if pArgs else ""
        pRes = evaluator.evaluate_expr(d,pExpr)
        # print(f"eval expr: {prettyArgs}{pExpr} = {pRes}")
        return myClorm.pytocl(evaluator.reducedExpr(pRes))
    except Exception as exn:
        # print(f"pythonEvalExpr: error when evaluating {pExpr} over {clArgs}:\n{exn}.")
        return myClorm.pytocl(evaluator.Error(str(exn)))


def pythonExecStmt(clCode,clEnv,clOuts):
    try:
        #print(clFn,clArgs)
        pCode = myClorm.cltopy(clCode,str)
        pEnv  = myClorm.cltopy(clEnv,list[tuple[str,evaluator.ReducedExpr]])
        pOuts = myClorm.cltopy(clOuts,list[str])
    except Exception as exn:
        print(f"pythonExecStmt: error when converting {(clCode,clEnv,clOuts)}: {exn}.")
        return myClorm.pytocl(evaluator.Error(str(exn)))
    try:
        globals = dict()
        locals = { x:evaluator.evaluate_expr(dict(),v) for (x,v) in pEnv }
        exec(pCode,globals,locals)
        results = [(x,locals[x]) for x in pOuts if x in locals]
        pResults = [(x,evaluator.Val(evaluator.get_baseType(v),v)) for (x,v) in results] + [True] # TODO incorrect for set results
        clResults = [myClorm.pytocl(r) for r in pResults]
        #print(pEnv,pCode,clResults)
        return clResults
    except Exception as exn:
        #print(f"pythonExecStmt: error in environment {pEnv} and output {pOuts} when evaluating\n{pCode}\nThe error was '{exn}'.")
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

#end.
