set_value(X,V) :- _se_value(variable(X),set), _set_contains(variable(X),V), _passed(solve,LBL,variable_interface(X)). %%% for compile2
set_value(X,V) :- _se_value(variable(X),ref(set,E)), _set_contains(E,V), _passed(solve,LBL,variable_interface(X)).
value(X,V) :- _se_value(variable(X),V), V != set, _passed(solve,LBL,variable_interface(X)).

evaluated(OP,ARGS,V) :- _evaluate(operation(OP,ARGS)), _shared_value(operation(OP,ARGS),V).

_shared_value(E,V)    :- _passed((compile;compile2;ground),LBL,share_value(E)), _se_value(E,V).

:- _passed((compile;compile2;ground),LBL,ensure(E)), not _shared_value(E,val(bool,true)), not _shared_value(E,bad).

_se_value1(variable(X)) :- _se_value(variable(X),V), _passed(compile,LBL,variable_interface(X)).
value(X,bad) :- _expression(compile,variable(X)), not _se_value1(variable(X)).
evaluated(OP,ARGS,bad) :- _passed(compile,LBL,evaluate(OP,ARGS)), not _se_value(operation(OP,ARGS),_).

type_variableD(X,T) :- _se_value(variable(X),val(T,V)), _passed(solve,LBL,variable_interface(X)).
type_variableD(X,set) :- _se_value(variable(X),set), _passed(solve,LBL,variable_interface(X)).
type_variableD(X,set) :- _se_value(variable(X),ref(set,R)), _passed(solve,LBL,variable_interface(X)).
type_variableD(X,bot) :- value(X,bad), _passed(solve,LBL,variable_interface(X)).
