% domains
_se_domain(variable(Var), Value) :- 
    _passed(compile2, _, variable_declare(Var, fromFacts)),
    _passed(compile2, _, variable_domain(Var, Expr)),
    _se_domain(Expr, Value).
_se_domain(variable(Var), Value) :- 
    _passed(compile2, _, variable_define(Var, Expr)),
    _se_domain(Expr, Value).

% set domains
_set_domain(variable(Var), Expr) :- 
    _passed(compile2, _, variable_declare(Var, set)),
    _passed(compile2, _, set_baseDomain(Var, Expr)).

% static assignments
_se_value(variable(Var), set) :- _passed(compile2, _, variable_declare(Var, set)).
_se_value(variable(Var), set) :-
    _passed(compile2, _, variable_define(Var, Expr)),
    _se_value(Expr, set).
_set_domain(variable(Var), Expr) :-
    _passed(compile2, _, variable_define(Var, Expr)),
    _se_value(variable(Var), set).
_set_contains(variable(Var), Value) :-
    _set_domain(variable(Var), Expr),
    _set_contains(Expr, Value).
_set_contains(variable(Var), Value) :-
    _passed(compile2, _, set_assign(Var, Expr)),
    _set_contains(Expr, Value).
_set_contains(variable(Var), Value) :-
    _passed(compile2, _, set_assign(Var, Expr)),
    _se_value(Expr, Value),
    Value = val(_, _).

% dynamic assignments
{_se_value(variable(Var), Value)} :- _passed(compile2,_, variable_define(Var, Expr)), _se_domain(Expr, Value).
:- _passed(compile2, _, variable_define(Var, Expr)), _se_value(variable(Var), Value), not _se_value(Expr, Value).
:- _passed(compile2, _, variable_define(Var, Expr)), _se_value(Expr, Value), not _se_value(variable(Var), Value).