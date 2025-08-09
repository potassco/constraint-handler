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
