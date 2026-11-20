_expression(ground,(E;C)) :- _passed(ground,LBL,variable_assign(X,E,C)).
_expression(ground,(E;C)) :- _passed(ground,LBL,variable_choice(X,E,C)).
_expression(ground,C) :- _passed(ground,LBL,variable_declare(X,D,C)).
_expression(ground,(E;C)) :- _passed(ground,LBL,variable_default(X,E,C,P)).
_expression(ground,(E;C)) :- _passed(ground,LBL,variable_define(X,E,C)).
_expression(ground,(E;C)) :- _passed(ground,LBL,variable_domain(X,E,C)).
_expression(ground,E) :- _passed(ground,LBL,share_value(E)).
_expression(ground,(E;C)) :- _passed(ground,LBL,set_assign(X,E,C)).

_variable(ground,X) :- _expression(ground,EXPR), X=@pythonExpressionVariable(EXPR).
_se_value(variable(X),V) :- _passed(ground,LBL,variable_define(X,E,C)), _ge_value(C,val(bool,true)), _se_value(E,V).
_se_value(variable(X),ref(set,variable(X))) :- _passed(ground,LBL,variable_declare(X,set,C)), _ge_value(C,val(bool,true)).
_set_contains(variable(X),V) :- _passed(ground,LBL,set_assign(X,E,C)), _ge_value(C,val(bool,true)), _ge_value(E,V).

_ge_value(variable(X),val(T,V)) :- _variable(ground,X), _se_value(variable(X),val(T,V)).
_ge_value(variable(X),bad) :- _variable(ground,X), _se_value(variable(X),bad).
_ge_value(variable(X),RV) :- _variable(ground,X), _se_value(variable(X),V), V!=bad, #false : V=val(T,W); _ge_reduced(V,RV).
_ge_value(variable(X),bad) :- _variable(ground,X), not _se_value(variable(X),_).

_ge_eval_expression(E) :- _expression(ground,E), #false : E=variable(X).
_ge_expand(V) :- _variable(ground,X), _se_value(variable(X),V).
_ge_expand(V) :- _ge_expand(ref(set,R)), not _ge_eval_expression(R), _set_contains(R,V).
_ge_expand(V) :- _ge_tuple(T,_,ARGS), V=@pythonListElements(ARGS).
_ge_tuple(T,N,ARGS) :- _ge_expand(T), (function,(),N,ARGS)=@pythonReify(T).
_ge_reduced(V,V) :- _ge_expand(V), #false : V=ref(T,R); not _ge_tuple(V,_,_).

_set_makeIndex(R) :- _ge_expand(ref(set,R)), not _ge_eval_expression(R).
_ge_set_list(R,0,()) :- _ge_expand(ref(set,R)), not _ge_eval_expression(R).
_ge_set_list(R,I+1,(RV,L)) :- _ge_set_list(R,I,L), _set_index(R,I,V), _ge_reduced(V,RV).
_ge_reduced(ref(set,R),set(L)) :- _ge_set_list(R,I,L), _set_lastIndex(R,I).
_ge_reduced(ref(set,E),set(L)) :- _ge_eval_exec(E,M,valid(set(L))).

_ge_tuple_list(T,N,()) :- _ge_tuple(T,N,ARGS).
_ge_tuple_list(T,I,(RV,L)) :- _ge_tuple_list(T,I+1,L), _ge_tuple(T,_,ARGS), (I,V)=@pythonEnumerateElements(ARGS), _ge_reduced(V,RV).
_ge_reduced(T,RV) :- _ge_tuple_list(T,0,L), RV=@pythonReflect(function,(),L).

_ge_enumeratedVariables(EXPR,R) :- _expression(ground,EXPR), R=@pythonEnumerateVariables(EXPR).
_ge_mapAux(EXPR,N,()) :- _ge_enumeratedVariables(EXPR,length(N)).
_ge_mapAux(EXPR,I,((X,V),M)) :- _ge_mapAux(EXPR,I+1,M), _ge_enumeratedVariables(EXPR,(I,X)), _ge_value(variable(X),V).
_ge_mapped(EXPR,M) :- _ge_mapAux(EXPR,0,M).

_ge_eval_exec(EXPR,M,RES) :- _ge_eval_expression(EXPR), _ge_mapped(EXPR,M), RES=@pythonEvalExpr(EXPR,M,ID), _main_solverIdentifiers(ID).
_ge_value(EXPR,V) :- _ge_eval_exec(EXPR,M,valid(V)).
_ge_value(EXPR,bad) :- _ge_eval_exec(EXPR,M,error(KIND,MSG)).
_se_value(EXPR,V) :- _ge_eval_exec(EXPR,M,valid(V)), #false : V=set(L).
_se_value(EXPR,bad) :- _ge_eval_exec(EXPR,M,error(KIND,MSG)).
_se_value(EXPR,ref(set,EXPR)) :- _ge_eval_exec(EXPR,M,valid(set(L))).
_set_contains(EXPR,V) :- _ge_eval_exec(EXPR,M,valid(set(L))), V=@pythonListElements(L).
_shared_value(EXPR,bad) :- _passed(ground,LBL,share_value(EXPR)), _ge_value(EXPR,bad).
_warning(KIND,(),(EXPR,M,MSG)) :- _ge_eval_exec(EXPR,M,error(KIND,MSG)).
