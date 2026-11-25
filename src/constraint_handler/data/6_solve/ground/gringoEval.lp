_expression(ground,(E;C)) :- _passed(ground,LBL,variable_assign(X,E,C)).
_expression(ground,(E;C)) :- _passed(ground,LBL,variable_choice(X,E,C)).
_expression(ground,C) :- _passed(ground,LBL,variable_declare(X,D,C)).
_expression(ground,(E;C)) :- _passed(ground,LBL,variable_default(X,E,C,P)).
_expression(ground,(E;C)) :- _passed(ground,LBL,variable_define(X,E,C)).
_expression(ground,(E;C)) :- _passed(ground,LBL,variable_domain(X,E,C)).
_expression(ground,(E;C)) :- _passed(ground,LBL,variable_element(X,E,C)).
_expression(ground,E) :- _passed(ground,LBL,share_value(E)).
_expression(ground,(E;C)) :- _passed(ground,LBL,set_assign(X,E,C)).

_variable(ground,X) :- _expression(ground,EXPR), X=@pythonExpressionVariable(EXPR).
_se_value(variable(X),V) :- _passed(ground,LBL,variable_define(X,E,C)), _se_value(C,val(bool,true)), _se_value(E,V).
_se_value(variable(X),ref(set,variable(X))) :- _passed(ground,LBL,variable_declare(X,set,C)), _se_value(C,val(bool,true)).
_set_candidate(variable(X),V) :- _passed(ground,LBL,set_assign(X,E,C)), _se_value(C,val(bool,true)), _se_value(E,V).
_set_candidate(variable(X),bad) :- _passed(ground,LBL,set_assign(X,variable(Y),C)), _se_value(C,val(bool,true)), not _se_value(variable(Y),_).

_ge_eval_expression(E) :- _expression(ground,E), #false : E=variable(X).
_direct_implode(V) :- _variable(ground,X), _se_value(variable(X),V), #false : V=ref(set,E), _ge_eval_expression(E).

_ge_enumeratedVariables(EXPR,R) :- _expression(ground,EXPR), R=@pythonEnumerateVariables(EXPR).
_ge_mapAux(EXPR,N,()) :- _ge_enumeratedVariables(EXPR,length(N)).
_ge_mapAux(EXPR,I,((X,V),M)) :- _ge_mapAux(EXPR,I+1,M), _ge_enumeratedVariables(EXPR,(I,X)), _se_value(variable(X),V), V=(bad;val(T,W)).
_ge_mapAux(EXPR,I,((X,RV),M)) :- _ge_mapAux(EXPR,I+1,M), _ge_enumeratedVariables(EXPR,(I,X)), _se_value(variable(X),V), V!=bad, #false : V=val(T,W); _direct_imploded(V,RV).
_ge_mapAux(EXPR,I,((X,bad),M)) :- _ge_mapAux(EXPR,I+1,M), _ge_enumeratedVariables(EXPR,(I,X)), not _se_value(variable(X),_).
_ge_mapped(EXPR,M) :- _ge_mapAux(EXPR,0,M).

_python_evaluate(EXPR,M) :- _ge_eval_expression(EXPR), _ge_mapped(EXPR,M).
