%%%%%%%%%%%%%%%%% interface ensure/2 variable_define/3 evaluate/2
_ge_ensure(CNAME,E) :- _passed(sugar,ensure(CNAME,E)), engine(CNAME,ground).
_ge_assign(LBL,X,E) :- _passed(sugar,variable_define(LBL,X,E)), engine(LBL,ground).
_ge_set_assign(CNAME,X,E) :- _passed(sugar,set_assign(CNAME,X,E)), engine(CNAME,ground).
%%% TODO: handle set_baseDomain here?
_ge_set_declare(CNAME,X) :- _passed(sugar,set_declare(CNAME,X)), engine(CNAME,ground).
%%% TODO: make sure set assign doesn't get broken down across different engines
_ge_evaluate(CNAME,OP,ARGS) :- _passed(sugar,evaluate(CNAME,OP,ARGS)), engine(CNAME,ground).

:- _ge_ensure(CNAME,EXPR), not ge_result(EXPR,val(bool,true)), not ge_result(EXPR,bad).
ge_value(X,V) :- _ge_assign(CNAME,X,EXPR), ge_result(EXPR,V).

_se_assign(_internal,variable(X),val(T,V)) :- ge_value(X,val(T,V)), representation(T,extensional).
_se_assign(_internal,variable(X),bad) :- ge_value(X,bad).
_set_declare(_internal,variable(X)) :- ge_value(X,set(S)).
_set_assign(_internal,variable(X),VAL) :- ge_value(X,set(S)), VAL=@pythonListElements(S).
evaluated(OP,ARGS,V) :- _ge_evaluate(CNAME,OP,ARGS), ge_result(operation(OP,ARGS),V).

ge_expressionQuery(operation(OP,ARGS)) :- _ge_evaluate(CNAME,OP,ARGS).
ge_expressionQuery(EXPR) :- _ge_ensure(CNAME,EXPR).
ge_expressionQuery(EXPR) :- _ge_assign(CNAME,X,EXPR).

_ge_vQuery(X) :- ge_expressionQuery(EXPR), X=@pythonExpressionVariable(EXPR).

_direct_implode(variable(X)) :- _ge_vQuery(X), _se_value(variable(X),V).
ge_value(X,VAL) :- _ge_vQuery(X), _se_value(variable(X),val(T,V)), _direct_imploded(variable(X),VAL).


_ge_setAssignsAux(X,#inf,()) :- _ge_set_declare(CNAME,X).
_ge_setAssignsAux(X,F,(F,L)) :- _ge_setAssignsAux(X,E,L), _ge_set_assign(CNAME,X,F), E < F,
    0 = #count { G : _ge_set_assign(CNAME,X,G), E < G, G < F }.
_ge_setAssigns(X,L) :- _ge_setAssignsAux(X,E,L),
    0 = #count { G : _ge_set_assign(CNAME,X,G), E < G }.

_ge_assign(CNAME,X,set(L)) :- _ge_set_declare(CNAME,X), _ge_setAssigns(X,L).

_ge_enumeratedVariables(EXPR,R) :- ge_expressionQuery(EXPR), R=@pythonEnumerateVariables(EXPR).

_ge_mapAux(EXPR,N,()) :- _ge_enumeratedVariables(EXPR,length(N)).
_ge_mapAux(EXPR,I,((X,V),M)) :- _ge_mapAux(EXPR,I+1,M), _ge_enumeratedVariables(EXPR,(I,X)), ge_value(X,V).
_ge_mapped(EXPR,M) :- _ge_mapAux(EXPR,0,M).

_ge_eval_exec(EXPR,M,RES) :- _ge_mapped(EXPR,M), RES=@pythonEvalExpr(EXPR,M,ID), _main_solverIdentifier(ID).
ge_result(EXPR,V) :- _ge_eval_exec(EXPR,M,V), #false: V=error(KIND,MSG).
ge_result(EXPR,bad) :- _ge_eval_exec(EXPR,M,error(KIND,MSG)).
_warning(KIND,(),(EXPR,M,MSG)) :- _ge_eval_exec(EXPR,M,error(KIND,MSG)).
