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

boolean_equivalence_input(Arg) :-
    boolean_equivalence_argument(_, _, Arg), value(Arg, boolean(_)).

boolean_equivalence_false_count(Id, Count) :-
    native_expression(Id, operation(leqv, _)),
    Count = #count { Index :
        boolean_equivalence_argument(Id, Index, Arg), value(Arg, boolean(false)) },
    boolean_equivalence_input(Arg) : boolean_equivalence_argument(Id, _, Arg).

value(Id, boolean(true)) :-
    boolean_equivalence_false_count(Id, Count), Count \ 2 = 0.
value(Id, boolean(false)) :-
    boolean_equivalence_false_count(Id, Count), Count \ 2 = 1.