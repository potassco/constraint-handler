%ge_value(X,val(T,V)) :- engine(CNAME,ground), assign(CNAME,X,EXPR), ge_result(EXPR,T,V).
%ge_value(X,val(T,V)) :- ge_vQuery(X), value(X,T,V), representation(T,extensional).
ge_value(X,T,V) :- engine(CNAME,ground), assign(CNAME,X,EXPR), ge_result(EXPR,T,V).
ge_value(X,T,V) :- ge_vQuery(X), value(X,T,V), representation(T,extensional).
ge_value(X,T,V) :- assign(CNAME,X,EXPR), ge_result(EXPR,T,V).

value(X,T,V) :- ge_value(X,T,V), representation(T,extensional).
value(X,set,V) :- ge_value(X,set,V).
%set_value(X,T,V) :- ge_value(X,set,V), representation(T,extensional). % TODO: explode set
evaluated(OP,ARGS,T,V) :- evaluate(OP,ARGS), EXPR=operation(OP,ARGS), ge_result(E,T,V). % TODO ???? E=EXPR?

ge_expressionQuery(EXPR) :- _main_defaultEngine(ground), evaluate(OP,ARGS), EXPR=operation(OP,ARGS).
ge_expressionQuery(EXPR) :- engine(CNAME,ground), ensure(CNAME,EXPR).
ge_expressionQuery(EXPR) :- engine(CNAME,ground), assign(CNAME,X,EXPR).
ge_expressionQuery(EXPR) :- engine(CNAME,ground), set_assign(CNAME,X,EXPR).

involvedVars(EXPR,@pythonExpressionVariable(EXPR)) :- ge_expressionQuery(EXPR).
ge_vQuery(X) :- involvedVars(EXPR,X).

ge_value(X,none,none) :- ge_vQuery(X), not assign(_,X,_), not multimap_assign(_,X,_,_) , not set_assign(_,X,_).


ge_set_declare(X) :- set_declare(CNAME,X), engine(CNAME,ground).
ge_set_assign(X,E) :- set_assign(CNAME,X,E), engine(CNAME,ground).

ge_indexSetAssign(X,#inf,-1) :- ge_set_declare(X).
ge_indexSetAssign(X,F,I+1) :- ge_indexSetAssign(X,E,I), ge_set_assign(X,F), E < F,
   0 = #count { G : ge_set_assign(X,G), E < G, G < F }.
ge_nbSetAssigns(X,N) :- ge_set_declare(X),
  N = #count { E : ge_set_assign(X,E) }.

ge_indexSetValue(X,0,()) :- ge_set_declare(X).
ge_indexSetValue(X,I+1,(V,L)) :- ge_indexSetValue(X,I,L), ge_indexSetAssign(X,E,I), ge_result(E,T,V), T != none.
ge_indexSetValue(X,I+1,L) :- ge_indexSetValue(X,I,L), ge_indexSetAssign(X,E,I), ge_result(E,none,V).
ge_value(X,set,set(L)) :- ge_indexSetValue(X,I,L), ge_nbSetAssigns(X,I).

ge_indexVar(EXPR,#inf,-1) :- ge_expressionQuery(EXPR).
ge_indexVar(EXPR,Y,I+1) :- ge_indexVar(EXPR,X,I), involvedVars(EXPR,Y), X < Y,
  0 = #count { Z : involvedVars(EXPR,Z), X < Z, Z < Y }.
ge_nbVars(EXPR,N) :- ge_expressionQuery(EXPR),
  N = #count { Y : involvedVars(EXPR,Y) }.


ge_mapAux(EXPR,0,()) :- ge_expressionQuery(EXPR).
ge_mapAux(EXPR,I+1,((X,VX),M)) :- ge_mapAux(EXPR,I,M), ge_indexVar(EXPR,X,I), ge_value(X,TX,VX).
ge_mapped(EXPR,M) :- ge_mapAux(EXPR,I,M), ge_nbVars(EXPR,I).


ge_result(EXPR,TYPE,V) :- ge_mapped(EXPR,M), val(TYPE,V)=@pythonEvalExpr(EXPR,M).
