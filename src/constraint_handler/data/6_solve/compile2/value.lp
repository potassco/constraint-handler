% constants
_se_value(val(Type, Value), val(Type, Value)) :- _expression(compile2, val(Type, Value)).
% bad
_se_value(bad, bad) :- _expression(compile2, bad).

_type_dynamic(compile2,E,T) :- _expression(compile2,E),
    _se_value(E,val(T,V)).
