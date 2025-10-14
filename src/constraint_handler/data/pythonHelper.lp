#script(python)

import constraint_handler.myClorm as myClorm
import constraint_handler.evaluator as evaluator
import operator
import clingo


def pythonExpressionVariable(clExpr):
    print("pythonExpressionVariable",clExpr)
    pExpr = myClorm.cltopy(clExpr,evaluator.Expr)
    pVars = list(evaluator.collectVars(pExpr))
    clVars = [myClorm.pytocl(var) for var in pVars]
    return clVars


def pythonBetaReduction(clExpr,clVars,clArgs):
    pVars = myClorm.cltopy(clVars)
    pArgs = myClorm.cltopy(clArgs,list[evaluator.Val])
    #pPairs = myClorm.cltopy(clArgs,list)
    #pArgs = [evaluator.Val(pPairs[2*i],pPairs[2*i+1]) for i in range(int(len(pPairs)/2))]
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
    pArgs = myClorm.cltopy(clArgs)
    pExpr = myClorm.cltopy(clExpr,evaluator.Expr)
    d = { var : val for (var,val) in pArgs }
    prettyArgs = "assuming " + ", ".join(f"{str(var)}={val}" for (var,val) in pArgs) + ", " if pArgs else ""
    pRes = evaluator.evaluate_expr(d,pExpr)
    print(f"eval expr: {prettyArgs}{pExpr} = {pRes}")
    if pRes is None:
        return myClorm.pytocl(evaluator.Val(None,None))
    pType = evaluator.get_baseType(pRes)
    # print(f"gringo eval expr in {clExpr}: result = {pRes} with {clArgs}")
    # print(f"gringo eval expr in {clExpr}: result = {myClorm.pytocl((pType,pRes))}")
    if pType is not None:
        return myClorm.pytocl(evaluator.Val(pType,pRes))
    if isinstance(pRes,set):
        val = set(list(pRes))
        type_ = clingo.Function("set")
        return myClorm.pytocl(evaluator.Val(type_,val))


def pythonExecStmt(clCode,clEnv,clOuts):
    try:
        #print(clFn,clArgs)
        pCode = myClorm.cltopy(clCode,str)
        pEnv  = myClorm.cltopy(clEnv,list[tuple[str,evaluator.Val]])
        pOuts = myClorm.cltopy(clOuts,list[str])
    except Exception as exn:
        print(f"pythonExecStmt: error when converting {(clCode,clEnv,clOuts)}: {exn}.")
        return myClorm.pytocl(evaluator.Error(str(exn)))
    try:
        globals = dict()
        locals = { x:v.value for (x,v) in pEnv }
        exec(pCode,globals,locals)
        results = [(x,locals[x]) for x in pOuts if x in locals]
        pResults = [(x,evaluator.Val(evaluator.get_baseType(v),v)) for (x,v) in results] + [True]
        clResults = [myClorm.pytocl(r) for r in pResults]
        #print(pEnv,pCode,clResults)
        return clResults
    except Exception as exn:
        #print(f"pythonExecStmt: error in environment {pEnv} and output {pOuts} when evaluating\n{pCode}\nThe error was '{exn}'.")
        return myClorm.pytocl(evaluator.Error(str(exn)))

#end.
#script(python)

import itertools
import clingo

import constraint_handler.myClorm
import constraint_handler.evaluator

def pythonReversed(clExpr):
    pL = myClorm.cltopy(clExpr,list)
    pRL = list(reversed(pL))
    return myClorm.pytocl(pRL)

def pythonListElements(clExpr):
    pBatchSize = 1 #myClorm.cltopy(clBatchSize,int)
    pL = myClorm.cltopy(clExpr,list)
    return [myClorm.pytocl(e) for e in pL]


def pythonEnumerateElements(clExpr):
    pBatchSize = 1 #myClorm.cltopy(clBatchSize,int)
    pL = myClorm.cltopy(clExpr,list)
    return [myClorm.pytocl(e) for e in enumerate(pL)]

def pythonListLength(clExpr):
    pL = myClorm.cltopy(clExpr,list)
    return myClorm.pytocl(len(pL))

#end.

#script(python)

import typing
import constraint_handler.myClorm as myClorm
import constraint_handler.evaluator as evaluator


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
