%%%%%%%%%%%%%%%%% interface ensure/2 assign/3 evaluate/2
_ge_ensure(CNAME,E) :- engine(CNAME,ground), ensure(CNAME,E).
_ge_assign(CNAME,X,E) :- engine(CNAME,ground), assign(CNAME,X,E).
_ge_set_assign(CNAME,X,E) :- engine(CNAME,ground), set_assign(CNAME,X,E).
_ge_set_declare(CNAME,X) :- engine(CNAME,ground), set_declare(CNAME,X).
%%% TODO: make sure set assign doesn't get broken down across different engines
_ge_evaluate(_ge_all,OP,ARGS) :- evaluate(OP,ARGS), _main_defaultEngine(ground).

:- _ge_ensure(CNAME,EXPR), not ge_result(EXPR,val(bool,true)), not ge_result(EXPR,bad).
ge_value(X,V) :- _ge_assign(CNAME,X,EXPR), ge_result(EXPR,V).
ge_value(X,val(T,V)) :- _ge_vQuery(X), value(X,val(T,V)), representation(T,extensional).
ge_value(X,V) :- _ge_vQuery(X), value(X,val(set,V)), V=set(S).

value(X,val(T,V)) :- ge_value(X,val(T,V)), representation(T,extensional).
value(X,val(set,V)) :- ge_value(X,V), V=set(S).
set_value(X,VAL) :- ge_value(X,VS), VS=set(S), VAL=@pythonListElements(S).
evaluated(OP,ARGS,V) :- _ge_evaluate(CNAME,OP,ARGS), EXPR=operation(OP,ARGS), ge_result(EXPR,V).

%ge_expressionQuery(EXPR) :- _main_defaultEngine(ground), evaluate(OP,ARGS), EXPR=operation(OP,ARGS).
ge_expressionQuery(EXPR) :- _ge_evaluate(CNAME,OP,ARGS), EXPR=operation(OP,ARGS).
ge_expressionQuery(EXPR) :- _ge_ensure(CNAME,EXPR).
ge_expressionQuery(EXPR) :- _ge_assign(CNAME,X,EXPR).

_ge_vQuery(X) :- ge_expressionQuery(EXPR), X=@pythonExpressionVariable(EXPR).

_direct_implode(V) :- _ge_vQuery(X), _se_value(variable(X),V).
ge_value(X,VAL) :- _ge_vQuery(X), E=variable(X), _se_value(E,val(T,V)), _direct_imploded(E,VAL).


_ge_setAssignsAux(X,#inf,()) :- _ge_set_declare(CNAME,X).
_ge_setAssignsAux(X,F,K) :- _ge_setAssignsAux(X,E,L), _ge_set_assign(CNAME,X,F), E < F,
    0 = #count { G : _ge_set_assign(CNAME,X,G), E < G, G < F },
K = (F,L).
_ge_setAssigns(X,L) :- _ge_setAssignsAux(X,E,L),
    0 = #count { G : _ge_set_assign(CNAME,X,G), E < G }.

_ge_assign(CNAME,X,EXPR) :- _ge_set_declare(CNAME,X), _ge_setAssigns(X,L), EXPR=set(L).

_ge_enumeratedVariables(EXPR,R) :- ge_expressionQuery(EXPR), R=@pythonEnumerateVariables(EXPR).

_ge_mapAux(EXPR,N,()) :- _ge_enumeratedVariables(EXPR,length(N)).
_ge_mapAux(EXPR,I,((X,V),M)) :- _ge_mapAux(EXPR,I+1,M), _ge_enumeratedVariables(EXPR,(I,X)), ge_value(X,V).
_ge_mapped(EXPR,M) :- _ge_mapAux(EXPR,0,M).

_ge_eval_exec(EXPR,M,RES) :- _ge_mapped(EXPR,M), RES=@pythonEvalExpr(EXPR,M,ID), _main_solverIdentifier(ID).
ge_result(EXPR,V) :- _ge_eval_exec(EXPR,M,V), #false: V=error(_,_).
_warning(KIND,(),(EXPR,M,MSG)) :- _ge_eval_exec(EXPR,M,error(KIND,MSG)).
