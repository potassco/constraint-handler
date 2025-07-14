groundingEnsure(CNAME,EXPR) :- ensure(CNAME,EXPR), engine(CNAME,ground).
groundingAssign(CNAME,X,EXPR) :- assign(CNAME,X,EXPR), engine(CNAME,ground).

involvedVars(CNAME,EXPR,@pythonCollectVars(EXPR)) :- groundingEnsure(CNAME,EXPR).
involvedVars(CNAME,EXPR,@pythonCollectVars(EXPR)) :- groundingAssign(CNAME,X,EXPR).

revMapAux(LNAME,XS,()) :- involvedVars(CNAME,EXPR,XS), LNAME=XS.
revMapAux(LNAME,XS,((X,V),VS)) :- revMapAux(LNAME,(X,XS),VS), eValue(variable(X),T,V).
revMapAux(LNAME,XS,VS) :- revMapAux(LNAME,(X,XS),VS), not conditional_hasValue(variable(X)).
mapped(LNAME,VS) :- revMapAux(LNAME,(),VS).

result(CNAME,EXPR,TYPE,V) :- involvedVars(CNAME,EXPR,XS), mapped(XS,VS), (TYPE,V)=@pythonEvalExpr(CNAME,EXPR,VS).

:- groundingEnsure(CNAME,EXPR), result(CNAME,EXPR,bool,false).
eValue(variable(X),T,V) :- groundingAssign(CNAME,X,EXPR), result(CNAME,EXPR,T,V).

#script(python)

import constraint_handler.myClorm as myClorm
import constraint_handler.evaluator as evaluator

def pythonCollectVars(clExpr):
    #print(clExpr)
    pExpr = myClorm.cltopy(clExpr,evaluator.Expr)
    #print(pExpr)
    pVars = list(evaluator.collectVars(pExpr))
    clVars = myClorm.pytocl(pVars)
    #print("collect vars",clExpr,pExpr,clVars)
    return clVars

def pythonEvalExpr(clName,clExpr,clArgs):
    pName = myClorm.cltopy(clName)
    pArgs = myClorm.cltopy(clArgs)
    pExpr = myClorm.cltopy(clExpr,evaluator.Expr)
    d = { var : val for (var,val) in pArgs }
    prettyArgs = "assuming " + ", ".join(f"{str(var)}={val}" for (var,val) in pArgs) + ", " if pArgs else ""
    pRes = evaluator.evaluate_expr(d,pExpr)
    #print(f"eval expr in {pName}: {prettyArgs}{pExpr} = {pRes}")
    if pRes is None:
        return []
    pType = evaluator.get_baseType(pRes)
    #print(f"gringo eval expr in {clExpr}: result = {pRes} with {clArgs}")
    if pType is not None:
        return myClorm.pytocl((pType,pRes))
#end.
