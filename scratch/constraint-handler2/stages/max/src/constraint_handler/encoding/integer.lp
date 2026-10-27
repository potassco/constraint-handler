%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% integer arithmetics
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

value(Id, integer(|V|)) :-
    native_expression(Id, operation(abs, (Arg,))),
    value(Arg, integer(V)).

linear_integer_input(Arg) :-
    linear_integer_term(_, _, _, Arg), value(Arg, integer(_)).

linear_integer_single(Id) :-
    linear_integer_offset(Id, _),
    1 = #count { Index : linear_integer_term(Id, Index, _, _) }.

value(Id, integer(Offset + Coefficient * V)) :-
    linear_integer_single(Id),
    linear_integer_offset(Id, integer(Offset)),
    linear_integer_term(Id, 0, integer(Coefficient), Arg),
    value(Arg, integer(V)).

order(Arg, V) :- order_min(Arg, _), value(Arg, integer(V)).
order(Arg, Lower) :- order_next(Arg, Lower, Upper), order(Arg, Upper).

value(Id, integer(Base + Total)) :-
    linear_integer_base(Id, Base),
    Total = #sum { Coefficient * (Upper - Lower), Index, Upper :
        linear_integer_term(Id, Index, integer(Coefficient), Arg),
        order_next(Arg, Lower, Upper), order(Arg, Upper) },
    linear_integer_input(Arg) : linear_integer_term(Id, _, _, Arg).

linear_comparison_operator("eq", eq, true).
linear_comparison_operator("eq", neq, false).
linear_comparison_operator("neq", neq, true).
linear_comparison_operator("neq", eq, false).
linear_comparison_operator("lt", lt, true).
linear_comparison_operator("lt", geq, false).
linear_comparison_operator("leq", leq, true).
linear_comparison_operator("leq", gt, false).
linear_comparison_operator("gt", gt, true).
linear_comparison_operator("gt", leq, false).
linear_comparison_operator("geq", geq, true).
linear_comparison_operator("geq", lt, false).

linear_comparison_test(Id, Relation, Result, -Base) :-
    linear_comparison_relation(Id, string(Name)),
    linear_comparison_base(Id, Base),
    linear_comparison_operator(Name, Relation, Result),
    linear_integer_input(Arg) : linear_integer_term(Id, _, _, Arg).

value(Id, boolean(Result)) :-
    linear_comparison_test(Id, eq, Result, Bound),
    #sum { Coefficient * (Upper - Lower), Index, Upper :
        linear_integer_term(Id, Index, integer(Coefficient), Arg),
        order_next(Arg, Lower, Upper), order(Arg, Upper) } = Bound.

value(Id, boolean(Result)) :-
    linear_comparison_test(Id, neq, Result, Bound),
    #sum { Coefficient * (Upper - Lower), Index, Upper :
        linear_integer_term(Id, Index, integer(Coefficient), Arg),
        order_next(Arg, Lower, Upper), order(Arg, Upper) } != Bound.

value(Id, boolean(Result)) :-
    linear_comparison_test(Id, lt, Result, Bound),
    #sum { Coefficient * (Upper - Lower), Index, Upper :
        linear_integer_term(Id, Index, integer(Coefficient), Arg),
        order_next(Arg, Lower, Upper), order(Arg, Upper) } < Bound.

value(Id, boolean(Result)) :-
    linear_comparison_test(Id, leq, Result, Bound),
    #sum { Coefficient * (Upper - Lower), Index, Upper :
        linear_integer_term(Id, Index, integer(Coefficient), Arg),
        order_next(Arg, Lower, Upper), order(Arg, Upper) } <= Bound.

value(Id, boolean(Result)) :-
    linear_comparison_test(Id, gt, Result, Bound),
    #sum { Coefficient * (Upper - Lower), Index, Upper :
        linear_integer_term(Id, Index, integer(Coefficient), Arg),
        order_next(Arg, Lower, Upper), order(Arg, Upper) } > Bound.

value(Id, boolean(Result)) :-
    linear_comparison_test(Id, geq, Result, Bound),
    #sum { Coefficient * (Upper - Lower), Index, Upper :
        linear_integer_term(Id, Index, integer(Coefficient), Arg),
        order_next(Arg, Lower, Upper), order(Arg, Upper) } >= Bound.