set_value(X,V) :- _se_value(variable(X),set), _set_contains(variable(X),V), _passed(solve,LBL,variable_interface(X)). %%% for compile2
set_value(X,V) :- _se_value(variable(X),ref(set,E)), _set_contains(E,V), _passed(solve,LBL,variable_interface(X)).
value(X,V) :- _se_value(variable(X),V), V != set, _passed(solve,LBL,variable_interface(X)).
warning(KIND,INFO,MSG) :- _warning(KIND,INFO,MSG), not _warning_ignore(KIND).

evaluated(OP,ARGS,V) :- _passed((compile;compile2;ground),LBL,evaluate(OP,ARGS)), _se_value(operation(OP,ARGS),V).

:- _passed((compile;compile2;ground),LBL,ensure(E)), not _se_value(E,val(bool,true)), not _se_value(E,bad).
