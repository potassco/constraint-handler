groundingEnsure(CNAME,EXPR) :- ensure(CNAME,EXPR), engine(CNAME,ground).
groundingAssign(CNAME,VAR,EXPR) :- assign(CNAME,VAR,EXPR), engine(CNAME,ground).

involvedVars(CNAME,EXPR,@pythonCollectVars(EXPR)) :- groundingEnsure(CNAME,EXPR).
involvedVars(CNAME,EXPR,@pythonCollectVars(EXPR)) :- groundingAssign(CNAME,X,EXPR).

revMapAux(LNAME,VARS,()) :- involvedVars(CNAME,EXPR,VARS), LNAME=VARS.
revMapAux(LNAME,VARS,((VAR,VAL),VALS)) :- revMapAux(LNAME,(VAR,VARS),VALS), value(variable(VAR),T,VAL).
mapped(LNAME,VS) :- revMapAux(LNAME,(),VS).

result(CNAME,TYPE,VAL) :- involvedVars(CNAME,EXPR,VARS), mapped(VARS,VS), (TYPE,VAL)=@pythonEvalExpr(CNAME,EXPR,VS).

:- groundingEnsure(CNAME,EXPR), result(CNAME,bool,false).
value(variable(X),T,V) :- groundingAssign(CNAME,X,EXPR), result(CNAME,T,V).

%:- evaluateAssign(CNAME,X,E), engine(CNAME,ground).

%#show value/3.
%#show evaluateCons/3.
%#show revMapAux/3.
%#show result2/4.
%#show mapped/2.
%#show result/3.
%#show involvedVars/3.

#script(python)

import constraint_handler.myClorm
import constraint_handler.evaluator as evaluator

def pythonCollectVars(clExpr):
    #print(clExpr)
    pExpr = myClorm.cltopy(clExpr,evaluator.Expr)
    #print(pExpr)
    pVars = list(evaluator.collectVars(pExpr))
    clVars = myClorm.pytocl(pVars)
    #print(clExpr,pExpr,clVars)
    return clVars

def pythonEvalExpr(clName,clExpr,clArgs):
    pName = myClorm.cltopy(clName)
    pArgs = myClorm.cltopy(clArgs)
    pExpr = myClorm.cltopy(clExpr,evaluator.Expr)
    d = { var : val for (var,val) in pArgs }
    prettyArgs = "assuming " + ", ".join(f"{str(var)}={val}" for (var,val) in pArgs) + ", " if pArgs else ""
    pRes = evaluator.evaluate_expr(d,pExpr)
    st = evaluator.toPair(pRes)
    print(f"eval expr in {pName}: {prettyArgs}{pExpr} = {pRes}")
    #print(f"eval expr in {clExpr}: result = {pRes}")
    return myClorm.pytocl(st)
#end.
