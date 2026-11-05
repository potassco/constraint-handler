%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% integer arithmetics
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

value(Expr, integer(|V|)) :-
    native_expression(Expr), Expr = operation(abs, (Arg,)),
    value(Arg, integer(V)).

linear_integer_input(Arg) :-
    linear_integer_term(_, _, _, Arg), value(Arg, integer(_)).

linear_integer_single(Expr) :-
    linear_integer_offset(Expr, _),
    1 = #count { Index : linear_integer_term(Expr, Index, _, _) }.

value(Expr, integer(Offset + Coefficient * V)) :-
    linear_integer_single(Expr),
    linear_integer_offset(Expr, integer(Offset)),
    linear_integer_term(Expr, 0, integer(Coefficient), Arg),
    value(Arg, integer(V)).

order(Arg, V) :- order_min(Arg, _), value(Arg, integer(V)).
order(Arg, Lower) :- order_next(Arg, Lower, Upper), order(Arg, Upper).

value(Expr, integer(Base + Total)) :-
    linear_integer_base(Expr, Base),
    Total = #sum { Coefficient * (Upper - Lower), Index, Upper :
        linear_integer_term(Expr, Index, integer(Coefficient), Arg),
        order_next(Arg, Lower, Upper), order(Arg, Upper) },
    linear_integer_input(Arg) : linear_integer_term(Expr, _, _, Arg).

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

linear_comparison_test(Expr, Relation, Result, -Base) :-
    linear_comparison_relation(Expr, string(Name)),
    linear_comparison_base(Expr, Base),
    linear_comparison_operator(Name, Relation, Result),
    linear_integer_input(Arg) : linear_integer_term(Expr, _, _, Arg).

value(Expr, boolean(Result)) :-
    linear_comparison_test(Expr, eq, Result, Bound),
    #sum { Coefficient * (Upper - Lower), Index, Upper :
        linear_integer_term(Expr, Index, integer(Coefficient), Arg),
        order_next(Arg, Lower, Upper), order(Arg, Upper) } = Bound.

value(Expr, boolean(Result)) :-
    linear_comparison_test(Expr, neq, Result, Bound),
    #sum { Coefficient * (Upper - Lower), Index, Upper :
        linear_integer_term(Expr, Index, integer(Coefficient), Arg),
        order_next(Arg, Lower, Upper), order(Arg, Upper) } != Bound.

value(Expr, boolean(Result)) :-
    linear_comparison_test(Expr, lt, Result, Bound),
    #sum { Coefficient * (Upper - Lower), Index, Upper :
        linear_integer_term(Expr, Index, integer(Coefficient), Arg),
        order_next(Arg, Lower, Upper), order(Arg, Upper) } < Bound.

value(Expr, boolean(Result)) :-
    linear_comparison_test(Expr, leq, Result, Bound),
    #sum { Coefficient * (Upper - Lower), Index, Upper :
        linear_integer_term(Expr, Index, integer(Coefficient), Arg),
        order_next(Arg, Lower, Upper), order(Arg, Upper) } <= Bound.

value(Expr, boolean(Result)) :-
    linear_comparison_test(Expr, gt, Result, Bound),
    #sum { Coefficient * (Upper - Lower), Index, Upper :
        linear_integer_term(Expr, Index, integer(Coefficient), Arg),
        order_next(Arg, Lower, Upper), order(Arg, Upper) } > Bound.

value(Expr, boolean(Result)) :-
    linear_comparison_test(Expr, geq, Result, Bound),
    #sum { Coefficient * (Upper - Lower), Index, Upper :
        linear_integer_term(Expr, Index, integer(Coefficient), Arg),
        order_next(Arg, Lower, Upper), order(Arg, Upper) } >= Bound.