value(Id, boolean(false)) :-
    native_expression(Id, operation(has_value, (Argument,))), value(Argument, none).

value(Id, boolean(true)) :-
    native_expression(Id, operation(has_value, (Argument,))),
    not value(Argument, none),
    value(Argument, _).