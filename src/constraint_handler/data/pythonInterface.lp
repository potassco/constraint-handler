#script (python)
from constraint_handler.performance import performance

@performance.route
def pythonIsExpr(clE):
    try:
        myClorm.cltopy(clE,expression.Expr)
        return myClorm.pytocl(True)
    except myClorm.FailedInstantiationExn:
        return myClorm.pytocl(False)

@performance.route
def pythonExpressionVariable(clExpr):
    try:
        pExpr = myClorm.cltopy(clExpr,expression.Expr)
        pVars = list(evaluator.collectVars(pExpr))
        clVars = [myClorm.pytocl(var) for var in pVars]
        return clVars
    except:
        return []

@performance.route
def pythonEnumerateVariables(clExpr):
    try:
        pExpr = myClorm.cltopy(clExpr,expression.Expr)
        pVars = list(evaluator.collectVars(pExpr))
        result = [myClorm.pytocl(e) for e in enumerate(pVars)]
        result.append(clingo.Function("length",[clingo.Number(len(pVars))]))
        return result
    except:
        return []

@performance.route
def pythonEnumerateExecutionVariables(clStmt,clIns):
    pStmt = myClorm.cltopy(clStmt,statement.Stmt)
    pIns = myClorm.cltopy(clIns,halt=False)
    pVars = list(evaluator.collectStmtVars(pStmt) | frozenset(pIns))
    result = [myClorm.pytocl(e) for e in enumerate(pVars)]
    result.append(clingo.Function("length",[clingo.Number(len(pVars))]))
    return result

 # TODO: dead?
@performance.route
def pythonBetaReduction(clExpr,clVars,clArgs):
    pVars = myClorm.cltopy(clVars,list)
    pArgs = myClorm.cltopy(clArgs,list[expression.ReducedExpr])
    pExpr = myClorm.cltopy(clExpr,expression.Expr)
    if len(pVars) != len(pArgs):
        print(f"pythonBetaReduction: inconsistent argument lengths for {pExpr}: {pVars} = {pArgs}")
        return []
    d = { var : val for (var,val) in zip(pVars,pArgs) }
    prettyArgs = ", ".join(f"{str(var)}={val}" for (var,val) in d.items())
    pRes = evaluator.beta_reduction(d,pExpr)
    return myClorm.pytocl(pRes)

@performance.route
def pythonEvalExpr(clExpr,clArgs,clId):
    try:
        pArgs = myClorm.cltopy(clArgs,list[tuple[typing.Any,expression.ReducedExpr]])
        pExpr = myClorm.cltopy(clExpr,expression.Expr)
        pId   = myClorm.cltopy(clId,list[expression.constant])
        globals = evaluator.get_environment(pId)
        results = []
        locals = dict()
        for (var,vexpr) in pArgs:
            val,errors = evaluator.evaluate_expr(vexpr,globals)
            locals[var] = val
            for (kind,msg) in errors:
                results.append(warning.Error(kind,msg))
        prettyD = { str(var) : val for (var,val) in locals.items() }
        pRes,errors = evaluator.evaluate_expr(pExpr, globals, locals)
        for (kind,msg) in errors:
            results.append(warning.Error(kind,msg))
        results.append(evaluator.reducedExpr(pRes))
        return [myClorm.pytocl(result) for result in results]
    except myClorm.FailedInstantiationExn as exn:
        kind = warning.Expression(warning.ExpressionWarning.pythonError)
        return myClorm.pytocl(warning.Error(kind,repr(exn)))
    except Exception as exn:
        kind = warning.Statement(warning.StatementWarning.syntaxError)
        kind = warning.Expression(warning.ExpressionWarning.pythonError)
        return myClorm.pytocl(warning.Error(kind,repr(exn)))

@performance.route
def pythonStatementVariables(clCode,clInTypes,clId):
    try:
        pCode = myClorm.cltopy(clCode,str)
        pInT  = myClorm.cltopy(clInTypes,list[tuple[expression.constant,type_.BaseType]])
        pId   = myClorm.cltopy(clId,list[expression.constant])
        globals = evaluator.get_environment(pId)
        tEnv  = defaultdict(set)
        for (var,t) in pInT:
            if isinstance(var,str):
                tEnv[var].add(t)
        results = []
        locals = dict()
        pyInputs = { x: frozenset((type_.py_type(t),)) for (x,t) in pInT }
        analysis = python_analysis.analyze_python_statement_types(pCode, globals, pyInputs)
        results = [(x,type_.ch_type(t)) for (x,ts) in analysis.name_types.items() for t in ts]
        return [myClorm.pytocl(result) for result in results]
    except myClorm.FailedInstantiationExn as exn:
        kind = warning.Statement(warning.StatementWarning.syntaxError)
        return myClorm.pytocl(warning.Error(kind,str(exn)))
    except Exception as exn:
        kind = warning.Statement(warning.StatementWarning.pythonError)
        return myClorm.pytocl(warning.Error(kind,repr(exn)))
#end.
