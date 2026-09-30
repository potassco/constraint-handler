set_value(X,V) :- _se_value(variable(X),set), _set_contains(variable(X),V), _variable_interface(X,LBL). %%% for compile2
set_value(X,V) :- _se_value(variable(X),ref(set,E)), _set_contains(E,V), _variable_interface(X,LBL).
value(X,V) :- _se_value(variable(X),V), V != set, _variable_interface(X,LBL).

_shared_value(E,V)    :- _passed(ENG,LBL,share_value(E)), _se_value(E,V), _engine_grounding(ENG).
%_shared_value(E,V)    :- _passed(share,LBL,share_value(E)), _se_value(E,V).

_se_value1(variable(X)) :- _se_value(variable(X),V), _variable_interface(X,LBL).
value(X,bad) :- _variable_interface(X,LBL), _expression(compile,variable(X)), not _se_value1(variable(X)).

_type_variableD(X,T) :- _se_value(variable(X),val(T,V)).
_type_variableD(X,set) :- _se_value(variable(X),set).
_type_variableD(X,set) :- _se_value(variable(X),ref(set,R)).
_type_variableD(X,bot) :- value(X,bad).

type_variableD(X,T) :- _type_variableD(X,T), _variable_interface(X,LBL).
