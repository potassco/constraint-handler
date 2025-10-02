#script(python)

import constraint_handler.myClorm as myClorm
import constraint_handler.evaluator as evaluator

def pythonCollectVars(clExpr):
    # print("pythonCollectVars",clExpr)
    pExpr = myClorm.cltopy(clExpr,evaluator.Expr)
    pVars = list(evaluator.collectVars(pExpr))
    clVars = myClorm.pytocl(pVars)
    return clVars

def pythonBetaReduction(clExpr,clVars,clArgs):
    # print("pythonBetaReduction",clExpr,clVars,clArgs)
    pVars = myClorm.cltopy(clVars)
    pArgs = myClorm.cltopy(clArgs,list[evaluator.Expr])
    pExpr = myClorm.cltopy(clExpr,evaluator.Expr)
    if len(pVars) != len(pArgs):
        print(f"pythonBetaReduction: inconsistent argument lengths for {pExpr}: {pVars} = {pArgs}")
        return []
    #print(f"pythonBetaReduction: consistent argument lengths for {pExpr}: {pVars} = {pArgs}")
    d = { var : val for (var,val) in zip(pVars,pArgs) }
    prettyArgs = ", ".join(f"{str(var)}={val}" for (var,val) in d.items())
    pRes = evaluator.beta_reduction(d,pExpr)
    #print(f"pythonBetaReduction: {pExpr}({prettyArgs}) = {pRes}")
    #assert False
    return myClorm.pytocl(pRes)

def pythonMergeTypes2(clArgs):
    pArgs = myClorm.cltopy(clArgs,list)
    skipped = [(pArgs[2*i],pArgs[2*i+1]) for i in range(int(len(pArgs)/2))]
    return myClorm.pytocl(skipped)

def pythonBetaReduction2(clExpr,clVars,clArgs):
    pVars = myClorm.cltopy(clVars)
    pArgs = myClorm.cltopy(clArgs,list[tuple[evaluator.BaseType,bool | int | float | str | clingo.Symbol]])
    pExpr = myClorm.cltopy(clExpr,evaluator.Expr)
    if len(pVars) != len(pArgs):
        print(f"pythonEvalExprFromPairs2: inconsistent argument lengths for {pExpr}: {pVars} = {pArgs}")
        return []
    d = { var : evaluator.Val(t,val) for (var,(t,val)) in zip(pVars,pArgs) }
    #print(d)
    prettyArgs = ", ".join(f"{str(var)}={val}" for (var,val) in d.items())
    pRes = evaluator.beta_reduction(d,pExpr)
    #print(f"pythonEvalExprFromPairs2: {pExpr}({prettyArgs}) = {pRes}")
    return myClorm.pytocl(pRes)

def pythonEvalExpr(clName,clExpr,clArgs):
    # print("pythonEvalExpr",clName,clExpr,clArgs)
    pName = myClorm.cltopy(clName)
    pArgs = myClorm.cltopy(clArgs)
    pExpr = myClorm.cltopy(clExpr,evaluator.Expr)
    d = { var : val for (var,val) in pArgs }
    prettyArgs = "assuming " + ", ".join(f"{str(var)}={val}" for (var,val) in pArgs) + ", " if pArgs else ""
    pRes = evaluator.evaluate_expr(d,pExpr)
    # print(f"eval expr in {pName}: {prettyArgs}{pExpr} = {pRes}")
    if pRes is None:
        return []
    pType = evaluator.get_baseType(pRes)
    # print(f"gringo eval expr in {clExpr}: result = {pRes} with {clArgs}")
    # print(f"gringo eval expr in {clExpr}: result = {myClorm.pytocl((pType,pRes))}")
    if pType is not None:
        return myClorm.pytocl((pType,pRes))
#end.
#script(python)

import constraint_handler.myClorm
import operator
import clingo
import constraint_handler.evaluator as evaluator

def getFn(clFn):
    cFn = myClorm.cltopy(clFn)
    pFn = None
    if cFn.type == clingo.SymbolType.String:
        pFn = eval(cFn.str)
    elif cFn.type == clingo.SymbolType.Function and cFn.name == "str":
        pFn = eval(cFn.arguments[0].str)
    else:
        print(f"python call isn't a str {cFn}")
    return pFn


pairList = list[tuple[evaluator.BaseType,evaluator.noPredConstant]]

def pythonEvalOperator(clFn,clArgs):
    try:
        #print(clFn,clArgs)
        pArgs = myClorm.cltopy(clArgs,list[evaluator.noPredConstant])
        pFn = myClorm.cltopy(clFn,evaluator.noPredOperator)
        pRes = evaluator.evaluate_operator(dict(),pFn,pArgs)
        pType = evaluator.get_baseType(pRes)
        if pRes is None:
            return []
        if pType is None:
            print("float.lp unsupported type",pRes)
            return []
        return myClorm.pytocl((pType,pRes))
    except Exception as exn:
        print(f"Python error when evaluating {pFn} on {pArgs}: {exn}.")
        return []

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

def pythonMergeTypes(clArgs):
    pArgs = myClorm.cltopy(clArgs,list)
    skipped = [pArgs[2*i+1] for i in range(int(len(pArgs)/2))]
    return myClorm.pytocl(skipped)

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

def pythonListElements(clExpr,clBatchSize = clingo.Number(1)):
    pBatchSize = myClorm.cltopy(clBatchSize,int)
    pL = myClorm.cltopy(clExpr,list)
    if pBatchSize == 1:
        pGroups = pL
    else:
        pGroups = itertools_batched(pL,pBatchSize)
    return [myClorm.pytocl(e) for e in pGroups]


def pythonEnumerateElements(clExpr,clBatchSize = clingo.Number(1)):
    pBatchSize = myClorm.cltopy(clBatchSize,int)
    pL = myClorm.cltopy(clExpr,list)
    if pBatchSize == 1:
        pGroups = pL
    else:
        pGroups = itertools_batched(pL,pBatchSize)
    return [myClorm.pytocl(e) for e in enumerate(pGroups)]

def pythonListLength(clExpr):
    pL = myClorm.cltopy(clExpr,list)
    return myClorm.pytocl(len(pL))

# https://docs.python.org/3/library/itertools.html#itertools.batched
def prepython12_itertools_batched(iterable, n, *, strict=False):
    # batched('ABCDEFG', 3) → ABC DEF G
    if n < 1:
        raise ValueError('n must be at least one')
    iterator = iter(iterable)
    while batch := tuple(itertools.islice(iterator, n)):
        if strict and len(batch) != n:
            raise ValueError('batched(): incomplete batch')
        yield batch

itertools_batched = itertools.batched if hasattr(itertools,'batched') else prepython12_itertools_batched

#end.
