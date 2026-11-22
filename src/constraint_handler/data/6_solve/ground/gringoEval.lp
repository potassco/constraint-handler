_expression(ground,(E;C)) :- _passed(ground,LBL,variable_assign(X,E,C)).
_expression(ground,(E;C)) :- _passed(ground,LBL,variable_choice(X,E,C)).
_expression(ground,C) :- _passed(ground,LBL,variable_declare(X,D,C)).
_expression(ground,(E;C)) :- _passed(ground,LBL,variable_default(X,E,C,P)).
_expression(ground,(E;C)) :- _passed(ground,LBL,variable_define(X,E,C)).
_expression(ground,(E;C)) :- _passed(ground,LBL,variable_domain(X,E,C)).
_expression(ground,E) :- _passed(ground,LBL,share_value(E)).
_expression(ground,(E;C)) :- _passed(ground,LBL,set_assign(X,E,C)).

_variable(ground,X) :- _expression(ground,EXPR), X=@pythonExpressionVariable(EXPR).
_se_value(variable(X),V) :- _passed(ground,LBL,variable_define(X,E,C)), _se_value(C,val(bool,true)), _se_value(E,V).
_se_value(variable(X),ref(set,variable(X))) :- _passed(ground,LBL,variable_declare(X,set,C)), _se_value(C,val(bool,true)).
_set_candidate(variable(X),V) :- _passed(ground,LBL,set_assign(X,E,C)), _se_value(C,val(bool,true)), _se_value(E,V).
_set_candidate(variable(X),bad) :- _passed(ground,LBL,set_assign(X,variable(Y),C)), _se_value(C,val(bool,true)), not _se_value(variable(Y),_).

_ge_eval_expression(E) :- _expression(ground,E), #false : E=variable(X).
_direct_implode(V) :- _variable(ground,X), _se_value(variable(X),V), #false : V=ref(set,E), _ge_eval_expression(E).
_direct_imploded(ref(set,E),set(L)) :- _ge_eval_exec(E,M,valid(set(L))).

_ge_enumeratedVariables(EXPR,R) :- _expression(ground,EXPR), R=@pythonEnumerateVariables(EXPR).
_ge_mapAux(EXPR,N,()) :- _ge_enumeratedVariables(EXPR,length(N)).
_ge_mapAux(EXPR,I,((X,V),M)) :- _ge_mapAux(EXPR,I+1,M), _ge_enumeratedVariables(EXPR,(I,X)), _se_value(variable(X),V), V=(bad;val(T,W)).
_ge_mapAux(EXPR,I,((X,RV),M)) :- _ge_mapAux(EXPR,I+1,M), _ge_enumeratedVariables(EXPR,(I,X)), _se_value(variable(X),V), V!=bad, #false : V=val(T,W); _direct_imploded(V,RV).
_ge_mapAux(EXPR,I,((X,bad),M)) :- _ge_mapAux(EXPR,I+1,M), _ge_enumeratedVariables(EXPR,(I,X)), not _se_value(variable(X),_).
_ge_mapped(EXPR,M) :- _ge_mapAux(EXPR,0,M).

_ge_eval_exec(EXPR,M,RES) :- _ge_eval_expression(EXPR), _ge_mapped(EXPR,M), RES=@pythonEvalExpr(EXPR,M,ID), _main_solverIdentifiers(ID).
_direct_explode(V) :- _ge_eval_exec(EXPR,M,valid(V)).
_se_value(EXPR,V) :- _ge_eval_exec(EXPR,M,valid(V)), V=(bad;val(T,W)).
_se_value(EXPR,V) :- _ge_eval_exec(EXPR,M,valid(RV)), _expression_tupleLength(implode,RV,N), _direct_exploded(RV,V).
_se_value(EXPR,bad) :- _ge_eval_exec(EXPR,M,error(KIND,MSG)).
_se_value(EXPR,ref(set,EXPR)) :- _ge_eval_exec(EXPR,M,valid(set(L))).
_set_contains(EXPR,V) :- _ge_eval_exec(EXPR,M,valid(set(L))), RV=@pythonListElements(L), _direct_exploded(RV,V).
_warning(KIND,(),(EXPR,M,MSG)) :- _ge_eval_exec(EXPR,M,error(KIND,MSG)).
