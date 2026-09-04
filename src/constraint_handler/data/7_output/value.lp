set_value(X,V) :- _se_value(variable(X),set), _set_contains(variable(X),V), _passed(solve,LBL,variable_interface(X)). %%% for compile2
set_value(X,V) :- _se_value(variable(X),ref(set,E)), _set_contains(E,V), _passed(solve,LBL,variable_interface(X)).
value(X,V) :- _se_value(variable(X),V), V != set, _passed(solve,LBL,variable_interface(X)).

_shared_value(E,V)    :- _passed(ENG,LBL,share_value(E)), _se_value(E,V), _engine_grounding(ENG).
%_shared_value(E,V)    :- _passed(share,LBL,share_value(E)), _se_value(E,V).

evaluated(OP,ARGS,V) :- _evaluate(REF,E), _shared_value(E,V), REF=operation(OP,ARGS).
evaluated(OP,ARGS,bad) :- _evaluate(REF,E), REF=operation(OP,ARGS), #false: _shared_value(E,V).

:- _passed(ENG,LBL,ensure(E)), not _shared_value(E,val(bool,true)), not _shared_value(E,bad), _engine_grounding(ENG).

_se_value1(variable(X)) :- _se_value(variable(X),V), _passed(compile,LBL,variable_interface(X)).
value(X,bad) :- _expression(compile,variable(X)), not _se_value1(variable(X)).

type_variableD(X,T) :- _se_value(variable(X),val(T,V)), _passed(solve,LBL,variable_interface(X)).
type_variableD(X,set) :- _se_value(variable(X),set), _passed(solve,LBL,variable_interface(X)).
type_variableD(X,set) :- _se_value(variable(X),ref(set,R)), _passed(solve,LBL,variable_interface(X)).
type_variableD(X,bot) :- value(X,bad), _passed(solve,LBL,variable_interface(X)).
