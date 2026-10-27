%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% boolean expressions
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


value(Id, boolean(true)) :-
    native_expression(Id, operation(disj, _)),
    boolean_argument(Id, Arg), value(Arg, boolean(true)).

value(Id, boolean(false)) :-
    native_expression(Id, operation(disj, _)),
    value(Arg, boolean(false)) : boolean_argument(Id, Arg).

value(Id, boolean(false)) :-
    native_expression(Id, operation(conj, _)),
    boolean_argument(Id, Arg), value(Arg, boolean(false)).

value(Id, boolean(true)) :-
    native_expression(Id, operation(conj, _)),
    value(Arg, boolean(true)) : boolean_argument(Id, Arg).