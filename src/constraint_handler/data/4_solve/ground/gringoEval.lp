_expression(ground,E) :- _passed(ground,LBL,bool_evaluate(E)).
_expression(ground,E) :- _passed(ground,LBL,ensure(E)).
_expression(ground,E) :- _passed(ground,LBL,evaluate(OP,ARGS)), E=operation(OP,ARGS).
_expression(ground,E) :- _passed(ground,LBL,variable_define(X,E)).
_expression(ground,E) :- _passed(ground,LBL,variable_define(X,E)).
_expression(ground,E) :- _passed(ground,LBL,variable_domain(X,E)).
_expression(ground,E) :- _passed(ground,LBL,optimize_component(E,PREC,ID,P)).
_expression(ground,PREC) :- _passed(ground,LBL,optimize_component(E,PREC,ID,P)).
_expression(ground,E) :- _passed(ground,LBL,preference_holds(E,K)).

%%%%%%%%%%%%%%%%% interface ensure/2 variable_define/3 evaluate/2
_ge_assign(LBL,X,E) :- _passed(ground,LBL,variable_define(X,E)).

_ge_set_assign(LBL,X,E) :- _passed(ground,LBL,set_assign(X,E)).
{ _ge_set_assign(LBL,X,E) } :- _passed(ground,LBL,set_baseDomain(X,E)).
:- _passed(ground,LBL,set_baseDomain(X,E)), evaluated(set_isin,(E,(variable(X),())),val(bool,true)), not _ge_set_assign(LBL,X,E).
_ge_set_declare(LBL,X) :- _passed(ground,LBL,variable_declare(X,set)).
%%% TODO: make sure set assign doesn't get broken down across different engines

ge_value(X,V) :- _ge_assign(LBL,X,EXPR), ge_result(EXPR,V).

_expression(ground,EXPR) :- _ge_assign(LBL,X,EXPR).

%_ge_nonImploded(X) :- ge_value(X,set(S)).
%_ge_nonImploded(X) :- ge_value(X,multimap(M)).

_se_assign(_internal,variable(X),T) :- ge_value(X,T), true=@pythonIsTuple(T).
%_se_assign(_internal,variable(X),val(T,V)) :- ge_value(X,val(T,V)).
_se_value(variable(X),val(T,V)) :- ge_value(X,val(T,V)).
_se_assign(_internal,variable(X),bad) :- ge_value(X,bad).
_set_declare(_internal,variable(X)) :- ge_value(X,set(S)).
_set_assign(_internal,variable(X),VAL) :- ge_value(X,set(S)), VAL=@pythonListElements(S).
_se_value(operation(OP,ARGS),V) :- ge_result(operation(OP,ARGS),V).
_se_value(val(T,V),val(T,V)) :- _expression(ground,val(T,V)).

%_se_assign(_internal,variable(X),T) :- ge_value(X,T), true=@pythonIsTuple(T).
_se_value(variable(X),T) :- ge_value(X,T), true=@pythonIsTuple(T). % TODO: fragile and probably incorrect!

_variable(ground,X) :- _expression(ground,EXPR), X=@pythonExpressionVariable(EXPR).
%_direct_implode(variable(X)) :- _expression(ground,EXPR), X=@pythonExpressionVariable(EXPR).

_direct_implode(variable(X)) :- _variable(ground,X), _se_value(variable(X),V).
ge_value(X,VAL) :- _variable(ground,X), _se_value(variable(X),val(T,V)), _direct_imploded(variable(X),VAL).


_ge_setAssignsAux(X,#inf,()) :- _ge_set_declare(CNAME,X).
_ge_setAssignsAux(X,F,(F,L)) :- _ge_setAssignsAux(X,E,L), _ge_set_assign(CNAME,X,F), E < F,
    0 = #count { G : _ge_set_assign(CNAME,X,G), E < G, G < F }.
_ge_setAssigns(X,L) :- _ge_setAssignsAux(X,E,L),
    0 = #count { G : _ge_set_assign(CNAME,X,G), E < G }.

_ge_assign(CNAME,X,set(L)) :- _ge_set_declare(CNAME,X), _ge_setAssigns(X,L).

_ge_enumeratedVariables(EXPR,R) :- _expression(ground,EXPR), R=@pythonEnumerateVariables(EXPR).

_ge_mapAux(EXPR,N,()) :- _ge_enumeratedVariables(EXPR,length(N)).
_ge_mapAux(EXPR,I,((X,V),M)) :- _ge_mapAux(EXPR,I+1,M), _ge_enumeratedVariables(EXPR,(I,X)), ge_value(X,V).
%_ge_mapAux(EXPR,I,((X,V),M)) :- _ge_mapAux(EXPR,I+1,M), _ge_enumeratedVariables(EXPR,(I,X)), _direct_imploded(variable(X),V).
_ge_mapped(EXPR,M) :- _ge_mapAux(EXPR,0,M).

_ge_eval_exec(EXPR,M,RES) :- _ge_mapped(EXPR,M), RES=@pythonEvalExpr(EXPR,M,ID), _main_solverIdentifiers(ID).
ge_result(EXPR,V) :- _ge_eval_exec(EXPR,M,V), #false: V=error(KIND,MSG).
ge_result(EXPR,bad) :- _ge_eval_exec(EXPR,M,error(KIND,MSG)).
_warning(KIND,(),(EXPR,M,MSG)) :- _ge_eval_exec(EXPR,M,error(KIND,MSG)).
