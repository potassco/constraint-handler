% constants
_se_domain(val(Type, Value), val(Type, Value)) :- _expression(compile3, val(Type, Value)).
_se_value(val(Type, Value), val(Type, Value)) :- _expression(compile3, val(Type, Value)).
% bad
_se_domain(bad, bad) :- _expression(compile3, bad).
_se_value(bad, bad) :- _expression(compile3, bad).

% expression values
{ _se_value(Expr, Value) } :-  _expression(compile3, Expr), _se_domain(Expr, Value).
:- _expression(compile3, Expr), not {_se_value(Expr, Value)} = 1.