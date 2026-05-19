% Regression: repeated x + base * (...) nesting.
% This should stay fast with the ground engine even as depth grows.

#const digit_count = 10.
#const max_depth = 7.

domain(0..digit_count - 1).
depth(1..max_depth).

variable_declare(assign_x, x, fromFacts).
variable_domain(x, val(int, I)) :- domain(I).

expr(1, variable(x)).
expr(K + 1, NextExpr) :-
    expr(K, Expr),
    depth(K + 1),
    ScaledExpr = operation(mult, (val(int, digit_count), (Expr, ()))),
    NextExpr = operation(add, (variable(x), (ScaledExpr, ()))).

variable_define(assign_y, y, Expr) :- expr(K, Expr), max_depth = K.

ensure(y_has_upper_bound, operation(eq, (variable(y), (val(int, digit_count**max_depth - 1), ())))).