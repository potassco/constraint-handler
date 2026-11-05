%%% copy_value_from_to(Expr1, Expr2): Expr2 takes over the whole payload of Expr1.

value(Expr2, Value) :- copy_value_from_to(Expr1, Expr2), value(Expr1, Value).
set_value(Expr2, Member) :- copy_value_from_to(Expr1, Expr2), set_value(Expr1, Member).
tuple_size(Expr2, Size) :- copy_value_from_to(Expr1, Expr2), tuple_size(Expr1, Size).
value(__tuple(Expr2, Index), Value) :- copy_value_from_to(Expr1, Expr2),
    tuple_size(Expr1, Size), Index = 0..Size-1, value(__tuple(Expr1, Index), Value).
set_value(__tuple(Expr2, Index), Member) :- copy_value_from_to(Expr1, Expr2),
    tuple_size(Expr1, Size), Index = 0..Size-1, set_value(__tuple(Expr1, Index), Member).
