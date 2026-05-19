% Regression: nested max over many bounded variables.
% This should stay fast with the compile engine even as depth grows.

#const digit_count = 10.
#const max_depth = 6.

domain(0..digit_count - 1).
depth(1..max_depth).

var(v(K)) :- depth(K).
variable_declare(def(V), V, fromFacts) :- var(V).
variable_domain(V, val(int, I)) :- var(V), domain(I).

expr(1, variable(v(1))).
expr(K + 1, NextExpr) :-
    expr(K, Expr),
    depth(K + 1),
    NextExpr = operation(max, (variable(v(K + 1)), (Expr, ()))).

variable_define(assign_y, y, Expr) :- expr(K, Expr), max_depth = K.

ensure(y_has_upper_bound, operation(eq, (variable(y), (val(int, digit_count - 1), ())))).