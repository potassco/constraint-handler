_expression_is_value(val(Type, Value)) :- _expression(compile2, val(Type, Value)).
_expression_is_value(bad) :- _expression(compile2, bad).

_se_value(Expr, Expr) :- _expression_is_value(Expr).

:- not _se_value(variable(Var), Value),
	_passed(compile2, _, variable_define(Var, Expr)),
	_se_value(Expr, Value).

% var has to take one of the values of the domain
var_has_domain(Var) :- _passed(compile2, _, variable_domain(Var, Expr)).
:- var_has_domain(Var),
   not 1 #sum { 1, Value : _se_value(variable(Var), Value),
                      _passed(compile2, _, variable_domain(Var, Expr)),
                      _se_value(Expr, Value) } 1.



1 { _se_value(Expr, Value) : _se_domain(Expr, Value) } 1 :-
	_se_domain(Expr, _),
	not _expression_is_value(Expr),
	not _se_is_set(Expr).


% statically define it as a set
_se_value(Expr, set) :- _se_is_set(Expr).

% bad
_se_value(variable(Var), bad) :-
    _passed(compile2, _, variable_define(Var, Expr)),
	_se_is_set(variable(Var)),
	_se_value(Expr, bad).
_se_value(variable(Var), bad) :-
    _passed(compile2, _, variable_define(Var, Expr)),
	_se_is_set(variable(Var)),
	not _se_is_set(Expr).
_se_value(variable(Var), bad) :-
    _passed(compile2, _, variable_domain(Var, Expr)),
	_se_is_set(variable(Var)),
	_se_value(Expr, bad).
_se_value(variable(Var), bad) :-
    _passed(compile2, _, variable_domain(Var, Expr)),
	_se_is_set(variable(Var)),
	not _se_is_set(Expr).
_se_value(variable(Var), bad) :-
    _passed(compile2, _, set_baseDomain(Var, Expr)),
	_se_value(Expr, bad).
_se_value(variable(Var), bad) :-
    _passed(compile2, _, set_assign(Var, Expr)),
	_se_value(Expr, bad).

 _set_contains(variable(Var), Val):-
    _passed(compile2, _, variable_define(Var, Expr)),
    _se_is_set(variable(Var)),
	_set_contains(Expr, Val),
	Val != bad.

_set_contains(variable(Var), Val) :-
    _passed(compile2, _, variable_domain(Var, Expr)),
    _se_is_set(variable(Var)),
	_set_contains(Expr, Val),
	Val != bad.

_set_contains(variable(Var), Val) :-
    _passed(compile2, _, set_assign(Var, Expr)),
	_se_value(Expr, Val),
	Val != bad.

{_set_contains(variable(Var), Val) } :-
	_passed(compile2, _, set_baseDomain(Var, Expr)),
	_se_value(Expr, Val),
	Val != bad.
