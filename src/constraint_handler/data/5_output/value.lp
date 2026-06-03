set_value(X,V) :- _se_value(variable(X),ref(set,E)), _set_contains(E,V).
value(X,V) :- _se_value(variable(X),V).
warning(KIND,INFO,MSG) :- _warning(KIND,INFO,MSG), not _warning_ignore(KIND).
