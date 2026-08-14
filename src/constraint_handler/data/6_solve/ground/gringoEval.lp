_expression(ground,E) :- _passed(ground,LBL,variable_assign(X,E)).
_expression(ground,E) :- _passed(ground,LBL,variable_define(X,E)).
_expression(ground,(E;C)) :- _passed(ground,LBL,variable_default(X,E,C,P)).
_expression(ground,E) :- _passed(ground,LBL,variable_domain(X,E)).
_expression(ground,E) :- _passed(ground,LBL,share_value(E)).

%%%%%%%%%%%%%%%%% interface ensure/2 variable_define/3 evaluate/2
_ge_assign(X,E) :- _passed(ground,LBL,variable_define(X,E)).

_ge_set_assign(LBL,X,E) :- _passed(ground,LBL,set_assign(X,E)).
{ _ge_set_assign(LBL,X,E) } :- _passed(ground,LBL,set_baseDomain(X,E)).
:- _passed(ground,LBL,set_baseDomain(X,E)), _shared_value(operation(set_isin,(E,(variable(X),()))),val(bool,true)), not _ge_set_assign(LBL,X,E).
_ge_set_declare(LBL,X) :- _passed(ground,LBL,variable_declare(X,set)).
%%% TODO: make sure set assign doesn't get broken down across different engines

ge_value(X,V) :- _ge_assign(X,EXPR), ge_result(EXPR,V).

_expression(ground,EXPR) :- _ge_assign(X,EXPR).

%_ge_nonImploded(X) :- ge_value(X,set(S)).
%_ge_nonImploded(X) :- ge_value(X,multimap(M)).

_se_value(variable(X),val(T,V)) :- ge_value(X,val(T,V)).
_se_value(variable(X),bad) :- ge_value(X,bad).
_se_value(variable(X),ref(set,variable(X))) :- ge_value(X,set(S)).
_set_assign(variable(X),VAL) :- ge_value(X,set(S)), VAL=@pythonListElements(S).
_se_value(operation(OP,ARGS),V) :- ge_result(operation(OP,ARGS),V).
_se_value(val(T,V),val(T,V)) :- _expression(ground,val(T,V)).

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

_ge_assign(X,set(L)) :- _ge_set_declare(CNAME,X), _ge_setAssigns(X,L).

_ge_enumeratedVariables(EXPR,R) :- _expression(ground,EXPR), R=@pythonEnumerateVariables(EXPR).

_ge_mapAux(EXPR,N,()) :- _ge_enumeratedVariables(EXPR,length(N)).
_ge_mapAux(EXPR,I,((X,V),M)) :- _ge_mapAux(EXPR,I+1,M), _ge_enumeratedVariables(EXPR,(I,X)), ge_value(X,V).
%_ge_mapAux(EXPR,I,((X,V),M)) :- _ge_mapAux(EXPR,I+1,M), _ge_enumeratedVariables(EXPR,(I,X)), _direct_imploded(variable(X),V).
_ge_mapped(EXPR,M) :- _ge_mapAux(EXPR,0,M).

_ge_eval_exec(EXPR,M,RES) :- _ge_mapped(EXPR,M), RES=@pythonEvalExpr(EXPR,M,ID), _main_solverIdentifiers(ID).
ge_result(EXPR,V) :- _ge_eval_exec(EXPR,M,valid(V)).
ge_result(EXPR,bad) :- _ge_eval_exec(EXPR,M,error(KIND,MSG)).
_warning(KIND,(),(EXPR,M,MSG)) :- _ge_eval_exec(EXPR,M,error(KIND,MSG)).
