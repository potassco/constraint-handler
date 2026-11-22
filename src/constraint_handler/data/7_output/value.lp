_variable_declared(X) :- ch_core(variable_declare(X,D,C),LBL), _bool_evaluated(C,val(bool,true)).
variable_declared(X) :- _variable_declared(X), ch_post(variable_interface(X),LBL).
_variable_defined(X) :- _se_value(variable(X),V), V != bad.
variable_defined(X) :- _variable_defined(X), ch_post(variable_interface(X),LBL).

set_value(X,V) :- _se_value(variable(X),set), _set_contains(variable(X),V), ch_post(variable_interface(X),LBL). %%% for compile2
set_value(X,V) :- _se_value(variable(X),ref(set,E)), _set_contains(E,V), ch_post(variable_interface(X),LBL).
value(X,V) :- _se_value(variable(X),V), V != set, V != bad, ch_post(variable_interface(X),LBL).
value(X,bad) :- _se_value(variable(X),bad), ch_post(variable_interface(X),LBL), _passed(ENG,_,variable_declare(X,D,C)), _bool_evaluated(C,val(bool,true)).

_shared_value(E,V)    :- _passed(ENG,LBL,share_value(E)), _se_value(E,V).
_shared_value(variable(X),bad) :- _passed(ground,LBL,share_value(variable(X))), not _se_value(variable(X),_).

_se_value1(variable(X)) :- _se_value(variable(X),V), ch_post(variable_interface(X),LBL).
value(X,bad) :- ch_post(variable_interface(X),LBL), _passed(compile,_,variable_declare(X,D,C)), _bool_evaluated(C,val(bool,true)), _expression(compile,variable(X)), not _se_value1(variable(X)).

_variable_typed(X,T) :- _se_value(variable(X),val(T,V)).
_variable_typed(X,set) :- _se_value(variable(X),set).
_variable_typed(X,set) :- _se_value(variable(X),ref(set,R)).
_variable_typed(X,bot) :- value(X,bad).

variable_typed(X,T) :- _variable_typed(X,T), ch_post(variable_interface(X),LBL).
