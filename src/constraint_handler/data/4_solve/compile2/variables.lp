% declarations
_variable(variable(Var)) :- _passed(compile2, _, variable_declare(Var, _)).

% domains
{ _se_value(variable(Var), Value) } :- _passed(compile2, _, variable_declare(Var, fromFacts)),
    _passed(compile2, _, variable_domain(Var, Expr)),
    _se_value(Expr, Value).

% set domains
{ _set_contains(variable(Var), Value) } :- _passed(compile2, _, variable_declare(Var, set)),
    _passed(compile2, _, set_baseDomain(Var, Expr)),
    _se_value(Expr, Value).

% static assignments
_se_value(variable(Var), set) :- _passed(compile2, _, variable_declare(Var, set)).
_se_value(variable(Var), Value) :- _passed(compile2,_, variable_define(Var, Expr)), _se_value(Expr, Value).
_set_contains(variable(Var), Value) :-
    _passed(compile2, _, variable_define(Var, Expr)),
    _se_value(Expr, set),
    _set_contains(Expr, Value).
_set_contains(variable(Var), Value) :- _passed(compile2,_, set_assign(Var, Expr)), _se_value(Expr, Value).

% exactly one value
% Note: this could be optimized only for fromFacts variables
:- _variable(X), not 1 #sum { 1,Y : _se_value(X,Y) } 1.
