minimize_defined(Statement) :-
    minimize_statement(Statement, Expr, Condition, _),
    value(Condition, boolean(true)), value(Expr, integer(_)).

#minimize {
    0@Priority : minimize_statement(_, _, _, Priority);
    Base@Priority, Statement :
        minimize_statement(Statement, Expr, _, Priority),
        minimize_defined(Statement), linear_integer_base(Expr, Base);
    Coefficient * (Upper - Lower)@Priority, Statement, Index, Upper :
        minimize_statement(Statement, Expr, _, Priority),
        minimize_defined(Statement),
        linear_integer_term(Expr, Index, integer(Coefficient), Arg),
        order_next(Arg, Lower, Upper), order(Arg, Upper)
}.