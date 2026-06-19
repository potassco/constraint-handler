set_value(X,V) :- _se_value(variable(X),ref(set,E)), _set_contains(E,V), _passed(solve,LBL,variable_interface(X)).
value(X,V) :- _se_value(variable(X),V), V != set, _passed(solve,LBL,variable_interface(X)).
warning(KIND,INFO,MSG) :- _warning(KIND,INFO,MSG), not _warning_ignore(KIND).
