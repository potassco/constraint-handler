% constants
_se_value(val(Type, Value), val(Type, Value)) :- _expression(compile, val(Type, Value)).
% bad
_se_value(bad, bad) :- _expression(compile, bad).