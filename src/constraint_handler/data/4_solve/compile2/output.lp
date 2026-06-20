set_value(X,V) :- _se_value(variable(X),set), _set_contains(variable(X),V).
value(X,V) :- _se_value(variable(X),V), V != set.
domain(X,V) :- _se_domain(X,V).
warning(KIND,INFO,MSG) :- _warning(KIND,INFO,MSG), not _warning_ignore(KIND).
