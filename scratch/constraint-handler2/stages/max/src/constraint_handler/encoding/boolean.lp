%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% boolean expressions
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

conditional_argument(Expr, Argument) :-
    native_expression(Expr), Expr = operation(if_, (Condition, Argument)),
    value(Condition, boolean(true)).

copy_value_from_to(Argument, Expr) :- conditional_argument(Expr, Argument).

value(Expr, none) :-
    native_expression(Expr), Expr = operation(if_, (Condition, Argument)),
    value(Condition, Value), Value != boolean(true), value(Argument, _).

value(Expr, boolean(true)) :-
    native_expression(Expr), Expr = operation(disj, _),
    boolean_argument(Expr, Arg), value(Arg, boolean(true)).

value(Expr, boolean(false)) :-
    native_expression(Expr), Expr = operation(disj, _),
    value(Arg, boolean(false)) : boolean_argument(Expr, Arg).

value(Expr, boolean(false)) :-
    native_expression(Expr), Expr = operation(conj, _),
    boolean_argument(Expr, Arg), value(Arg, boolean(false)).

value(Expr, boolean(true)) :-
    native_expression(Expr), Expr = operation(conj, _),
    value(Arg, boolean(true)) : boolean_argument(Expr, Arg).

boolean_equivalence_input(Arg) :-
    boolean_equivalence_argument(_, _, Arg), value(Arg, boolean(_)).

boolean_equivalence_false_count(Expr, Count) :-
    native_expression(Expr), Expr = operation(leqv, _),
    Count = #count { Index :
        boolean_equivalence_argument(Expr, Index, Arg), value(Arg, boolean(false)) },
    boolean_equivalence_input(Arg) : boolean_equivalence_argument(Expr, _, Arg).

value(Expr, boolean(true)) :-
    boolean_equivalence_false_count(Expr, Count), Count \ 2 = 0.
value(Expr, boolean(false)) :-
    boolean_equivalence_false_count(Expr, Count), Count \ 2 = 1.