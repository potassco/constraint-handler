%%%%%%%%%%%%%%%%% interface ensure/2 assign/3 evaluate/2
_ge_ensure(CNAME,E) :- engine(CNAME,ground), ensure(CNAME,E).
_ge_assign(CNAME,X,E) :- engine(CNAME,ground), assign(CNAME,X,E).
_ge_set_assign(CNAME,X,E) :- engine(CNAME,ground), set_assign(CNAME,X,E).
_ge_set_declare(CNAME,X) :- engine(CNAME,ground), set_declare(CNAME,X).
%%% TODO: make sure set assign doesn't get broken down across different engines

:- _ge_ensure(CNAME,EXPR), not ge_result(EXPR,val(bool,true)).
ge_value(X,V) :- _ge_assign(CNAME,X,EXPR), ge_result(EXPR,V).
ge_value(X,val(T,V)) :- ge_vQuery(X), value(X,val(T,V)), representation(T,extensional).

value(X,val(T,V)) :- ge_value(X,val(T,V)), representation(T,extensional).
value(X,val(set,V)) :- ge_value(X,V), V=set(S).
set_value(X,VAL) :- ge_value(X,VS), VS=set(S), VAL=@pythonListElements(S).
evaluated(OP,ARGS,T,V) :- evaluate(OP,ARGS), EXPR=operation(OP,ARGS), ge_result(EXPR,val(T,V)).

ge_expressionQuery(EXPR) :- _main_defaultEngine(ground), evaluate(OP,ARGS), EXPR=operation(OP,ARGS).
ge_expressionQuery(EXPR) :- _ge_ensure(CNAME,EXPR).
ge_expressionQuery(EXPR) :- _ge_assign(CNAME,X,EXPR).


involvedVars(EXPR,@pythonExpressionVariable(EXPR)) :- ge_expressionQuery(EXPR).
ge_vQuery(X) :- involvedVars(EXPR,X).

_direct_implode(val(T,V)) :- ge_vQuery(X), eValue(variable(X),T,V).
ge_value(X,VAL) :- ge_vQuery(X), E=variable(X), eValue(E,T,V), _direct_imploded(E,VAL).


_ge_setAssignsAux(X,#inf,()) :- _ge_set_declare(CNAME,X).
_ge_setAssignsAux(X,F,K) :- _ge_setAssignsAux(X,E,L), _ge_set_assign(CNAME,X,F), E < F,
    0 = #count { G : _ge_set_assign(CNAME,X,G), E < G, G < F },
K = (F,L).
_ge_setAssigns(X,L) :- _ge_setAssignsAux(X,E,L),
    0 = #count { G : _ge_set_assign(CNAME,X,G), E < G }.

_ge_assign(CNAME,X,EXPR) :- _ge_set_declare(CNAME,X), _ge_setAssigns(X,L), EXPR=set(L).

ge_indexVar(EXPR,#inf,-1) :- ge_expressionQuery(EXPR).
ge_indexVar(EXPR,Y,I+1) :- ge_indexVar(EXPR,X,I), involvedVars(EXPR,Y), X < Y,
  0 = #count { Z : involvedVars(EXPR,Z), X < Z, Z < Y }.
ge_nbVars(EXPR,N) :- ge_expressionQuery(EXPR),
  N = #count { Y : involvedVars(EXPR,Y) }.


ge_mapAux(EXPR,0,()) :- ge_expressionQuery(EXPR).
ge_mapAux(EXPR,I+1,((X,V),M)) :- ge_mapAux(EXPR,I,M), ge_indexVar(EXPR,X,I), ge_value(X,V).
ge_mapped(EXPR,M) :- ge_mapAux(EXPR,I,M), ge_nbVars(EXPR,I).

_ge_eval_exec(EXPR,M,RES) :- ge_mapped(EXPR,M), RES=@pythonEvalExpr(EXPR,M,ID), _main_solverIdentifier(ID).
ge_result(EXPR,V) :- _ge_eval_exec(EXPR,M,V), #false: V=error(_).
warning((EXPR,M,MSG)) :- _ge_eval_exec(EXPR,M,error(MSG)).
