#script(python)

import itertools
import operator
import typing

from collections import defaultdict

import clingo

import constraint_handler.myClorm as myClorm
import constraint_handler.evaluator as evaluator
import constraint_handler.schemas.atom as atom
import constraint_handler.schemas.expression as expression
import constraint_handler.schemas.statement as statement
import constraint_handler.schemas.warning as warning
import constraint_handler.solver_environment as solver_environment
import constraint_handler.utils.python_statement_analysis as python_analysis


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
    pVars = myClorm.cltopy(clVars,list)
    pArgs = myClorm.cltopy(clArgs,list[expression.ReducedExpr])
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
    eval_error = warning.Expression(warning.ExpressionWarning.pythonError)
    try:
        pArgs = myClorm.cltopy(clArgs,list[tuple[typing.Any,expression.ReducedExpr]])
        pExpr = myClorm.cltopy(clExpr,expression.Expr)
        pId   = myClorm.cltopy(clId,int | None)
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
        # print(f"pythonEvalExpr: error when converting {(clArgs,clExpr)}: {repr(exn)}.")
        return myClorm.pytocl(warning.Error(eval_error,repr(exn)))
    except Exception as exn:
        # print(f"pythonEvalExpr: uncaught exception {repr(exn)} in context {(clExpr,clArgs,clId)}")
        return myClorm.pytocl(warning.Error(eval_error,repr(exn)))


def pythonExec(clStmt,clEnv,clId):
    exec_error = warning.Statement(warning.StatementWarning.pythonError)
    try:
        pStmt = myClorm.cltopy(clStmt,statement.Stmt)
        pEnv  = myClorm.cltopy(clEnv,list[tuple[expression.constant,expression.ReducedExpr]])
        pId   = myClorm.cltopy(clId,int | None)
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
                results.append((x,expression.Python(repr(val))))
        return map(myClorm.pytocl,results)
    except solver_environment.FailIntegrityExn:
        return myClorm.pytocl(atom.FailIntegrity())
    except myClorm.FailedInstantiationExn as exn:
        print(f"pythonExec: error when converting {(clStmt,clEnv,clId)}: {repr(exn)}.")
        return myClorm.pytocl(warning.Error(exec_error,str(exn)))
    except Exception as exn:
        print(f"pythonExec: uncaught exception {repr(exn)} in context {(clStmt,clEnv,clId)}")
        return myClorm.pytocl(warning.Error(exec_error,repr(exn)))


def pythonListElements(clL):
    try:
        return myClorm.cltopy(clL,list[clingo.Symbol])
    except myClorm.FailedInstantiationExn:
        return []

def pythonReversedList(clL):
    pL = pythonListElements(clL)
    return myClorm.pytocl(list(reversed(pL)))

def pythonEnumerateElements(clL):
    pL = pythonListElements(clL)
    return [myClorm.pytocl(e) for e in enumerate(pL)]

def pythonListLength(clL):
    pL = pythonListElements(clL)
    return myClorm.pytocl(len(pL))


def pythonIsList(clL):
    try:
        myClorm.cltopy(clL,list)
        return myClorm.pytocl(True)
    except myClorm.FailedInstantiationExn:
        return myClorm.pytocl(False)

def pythonIsString(clS):
    return myClorm.pytocl(clS.type == clingo.SymbolType.String)

def pythonIsTuple(clT):
    return myClorm.pytocl(clT.type == clingo.SymbolType.Function and clT.name == "" and (len(clT.arguments) != 2 or clT.arguments[1] != clingo.Function("")))

def pythonIsExpr(clE):
    try:
        myClorm.cltopy(clE,expression.Expr)
        return myClorm.pytocl(True)
    except myClorm.FailedInstantiationExn:
        return myClorm.pytocl(False)

def pythonTupleElements(clT):
    if clT.type == clingo.SymbolType.Function and clT.name == "":
        return clT.arguments
    else:
        return []

def pythonStringLength(clStr):
    pStr = myClorm.cltopy(clStr,str)
    return myClorm.pytocl(len(pStr))

def pythonStringAdd(clStr1,clStr2):
    pStr1 = myClorm.cltopy(clStr1,str)
    pStr2 = myClorm.cltopy(clStr2,str)
    return myClorm.pytocl(pStr1+pStr2)

def pythonDebug(clExpr):
    #print("debug: ",clExpr)
    return clExpr

def pythonStop(clExpr):
    #print("stop: ",clExpr)
    pExpr = myClorm.cltopy(clExpr,int)
    if pExpr < -5:
        assert False
    return clExpr


def pythonScopeToString(clS,clVar):
    try:
        l = myClorm.cltopy(clS,list)
        prg = str(l[-1])
        var = str(clVar)
        uid = "".join(str(a) for a in reversed(l[:-1]))
        name = f"{prg}_{var}_{uid}"
        return myClorm.pytocl(name)
    except myClorm.FailedInstantiationExn:
        return clS
        #return myClorm.pytocl(False)

class Local(typing.NamedTuple):
    name: typing.Any
    var: expression.Variable

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

def pythonReify(term):
    if term.type == clingo.SymbolType.Function:
        symb = clingo.symbol.Function(term.name)
        n = len(term.arguments)
        return myClorm.pytocl((clingo.symbol.Function("function"),symb,n,term.arguments))
    elif term.type == clingo.SymbolType.Number:
        return myClorm.pytocl((clingo.symbol.Function("number"),term,0,()))
    else:
        return myClorm.pytocl((clingo.symbol.Function("string"),term,0,()))

def pythonReflect(kind,term,args):
    if kind == clingo.symbol.Function("function") and term.type == clingo.SymbolType.Function:
        name = term.name
        arguments = myClorm.cltopy(args,list)
        return clingo.Function(name,arguments)
    elif kind == clingo.symbol.Function("number"):
        return term
    elif kind == clingo.symbol.Function("string"):
        return term
    else:
        print("pythonHelper.pythonReflect",(kind,term,args),"is not a valid term")
        return []

def pythonStatementVariables(clCode,clInTypes,clId):
    exec_error = warning.Statement(warning.StatementWarning.pythonError)
    try:
        pCode = myClorm.cltopy(clCode,str)
        pInT  = myClorm.cltopy(clInTypes,list[tuple[expression.constant,python_analysis.TypeInfo]])
        pId   = myClorm.cltopy(clId,int | None)
        globals = evaluator.get_environment(pId)
        tEnv  = defaultdict(set)
        for (var,t) in pInT:
            if isinstance(var,str):
                tEnv[var].add(t)
        results = []
        locals = dict()
        analysis = python_analysis.analyze_python_statement_types(pCode) #, locals)
        # print(analysis)
        return map(myClorm.pytocl,analysis.name_types.items())
        #names = [myClorm.pytocl((var,types)) for var,types in analysis.name_types.items()]
        # return names
        # if not results:
        #     results.append(True)
        # for (x,val) in locals.items():
        #     try:
        #         results.append((x,evaluator.reducedExpr(val)))
        #     except NotImplementedError:
        #         results.append((x,expression.Python(repr(val))))
        # return map(myClorm.pytocl,results)
    # except solver_environment.FailIntegrityExn:
    #     return myClorm.pytocl(atom.FailIntegrity())
    except myClorm.FailedInstantiationExn as exn:
        print(f"pythonExec: error when converting {(clCode,clInTypes,clId)}: {repr(exn)}.")
        return myClorm.pytocl(warning.Error(exec_error,str(exn)))
    except Exception as exn:
        print(f"pythonExec: uncaught exception {repr(exn)} in context {(clCode,clInTypes,clId)}")
        return myClorm.pytocl(warning.Error(exec_error,repr(exn)))
#end.
