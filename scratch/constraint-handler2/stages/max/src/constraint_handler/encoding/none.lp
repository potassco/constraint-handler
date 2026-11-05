value(Expr, boolean(false)) :-
    native_expression(Expr), Expr = operation(has_value, (Argument,)), value(Argument, none).

value(Expr, boolean(true)) :-
    native_expression(Expr), Expr = operation(has_value, (Argument,)),
    not value(Argument, none),
    value(Argument, _).