%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% boolean expressions
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

conditional_argument(Id, Argument) :-
    native_expression(Id), Id = operation(if_, (Condition, Argument)),
    value(Condition, boolean(true)).

value(Id, Value) :- conditional_argument(Id, Argument), value(Argument, Value).
set_value(Id, Value) :- conditional_argument(Id, Argument), set_value(Argument, Value).
tuple_size(Id, Size) :- conditional_argument(Id, Argument), tuple_size(Argument, Size).
value(__tuple(Id, Index), Value) :- conditional_argument(Id, Argument),
    tuple_size(Argument, Size), Index = 0..Size-1, value(__tuple(Argument, Index), Value).
set_value(__tuple(Id, Index), Value) :- conditional_argument(Id, Argument),
    tuple_size(Argument, Size), Index = 0..Size-1, set_value(__tuple(Argument, Index), Value).

value(Id, none) :-
    native_expression(Id), Id = operation(if_, (Condition, Argument)),
    value(Condition, Value), Value != boolean(true), value(Argument, _).

value(Id, boolean(true)) :-
    native_expression(Id), Id = operation(disj, _),
    boolean_argument(Id, Arg), value(Arg, boolean(true)).

value(Id, boolean(false)) :-
    native_expression(Id), Id = operation(disj, _),
    value(Arg, boolean(false)) : boolean_argument(Id, Arg).

value(Id, boolean(false)) :-
    native_expression(Id), Id = operation(conj, _),
    boolean_argument(Id, Arg), value(Arg, boolean(false)).

value(Id, boolean(true)) :-
    native_expression(Id), Id = operation(conj, _),
    value(Arg, boolean(true)) : boolean_argument(Id, Arg).

boolean_equivalence_input(Arg) :-
    boolean_equivalence_argument(_, _, Arg), value(Arg, boolean(_)).

boolean_equivalence_false_count(Id, Count) :-
    native_expression(Id), Id = operation(leqv, _),
    Count = #count { Index :
        boolean_equivalence_argument(Id, Index, Arg), value(Arg, boolean(false)) },
    boolean_equivalence_input(Arg) : boolean_equivalence_argument(Id, _, Arg).

value(Id, boolean(true)) :-
    boolean_equivalence_false_count(Id, Count), Count \ 2 = 0.
value(Id, boolean(false)) :-
    boolean_equivalence_false_count(Id, Count), Count \ 2 = 1.