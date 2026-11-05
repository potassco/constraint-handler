tuple_argument_defined(Expr, Index) :- tuple_argument(Expr, Index, Arg), value(Arg, _).
value(Expr, tuple) :- tuple_arity(Expr, _),
    tuple_argument_defined(Expr, Index) : tuple_argument(Expr, Index, _).
tuple_size(Expr, Size) :- tuple_arity(Expr, Size), value(Expr, tuple).
value(__tuple(Expr, Index), Value) :- tuple_argument(Expr, Index, Arg), value(Expr, tuple), value(Arg, Value).
set_value(__tuple(Expr, Index), Value) :- tuple_argument(Expr, Index, Arg), value(Expr, tuple), set_value(Arg, Value).

value(Expr, Value) :-
    native_expression(Expr), Expr = operation(tuple_get, (Arg, Position)),
    value(Arg, tuple), tuple_size(Arg, Size), value(Position, integer(Index)),
    Index >= 0, Index < Size, value(__tuple(Arg, Index), Value).
set_value(Expr, Value) :-
    native_expression(Expr), Expr = operation(tuple_get, (Arg, Position)),
    value(Arg, tuple), tuple_size(Arg, Size), value(Position, integer(Index)),
    Index >= 0, Index < Size, set_value(__tuple(Arg, Index), Value).
value(Expr, integer(Size)) :- native_expression(Expr), Expr = operation(length, (Arg,)),
    value(Arg, tuple), tuple_size(Arg, Size).

equality_tuple_subject(Arg) :- equality_input(Arg), value(Arg, tuple).
equality_input(__tuple(Arg, Index)) :- equality_tuple_subject(Arg),
    tuple_size(Arg, Size), Index = 0..Size-1.
tuple_equality(Expr, Op, Left, Right) :- equality_operands(Expr, Op, Left, Right),
    equality_tuple_subject(Left), equality_tuple_subject(Right).
tuple_slot_match(Expr, Index) :- tuple_equality(Expr, _, Left, Right),
    tuple_size(Left, Size), Index = 0..Size-1,
    equality_scalar_key(__tuple(Left, Index), Key),
    equality_scalar_key(__tuple(Right, Index), Key).
tuple_slot_set(Expr, Index, Left, Right) :- tuple_equality(Expr, _, Left, Right),
    tuple_size(Left, Size), Index = 0..Size-1,
    value(__tuple(Left, Index), set), value(__tuple(Right, Index), set).
tuple_set_difference(Expr, Index) :- tuple_slot_set(Expr, Index, Left, Right),
    equality_set_key(__tuple(Left, Index), Key),
    not equality_set_key(__tuple(Right, Index), Key).
tuple_set_difference(Expr, Index) :- tuple_slot_set(Expr, Index, Left, Right),
    equality_set_key(__tuple(Right, Index), Key),
    not equality_set_key(__tuple(Left, Index), Key).
tuple_slot_match(Expr, Index) :- tuple_slot_set(Expr, Index, _, _),
    not tuple_set_difference(Expr, Index).
tuple_unequal(Expr) :- tuple_equality(Expr, _, Left, Right),
    tuple_size(Left, Size), not tuple_size(Right, Size).
tuple_unequal(Expr) :- tuple_equality(Expr, _, Left, Right),
    tuple_size(Right, Size), not tuple_size(Left, Size).
tuple_unequal(Expr) :- tuple_equality(Expr, _, Left, _), tuple_size(Left, Size),
    Index = 0..Size-1, not tuple_slot_match(Expr, Index).
value(Expr, boolean(true)) :- tuple_equality(Expr, eq, _, _), not tuple_unequal(Expr).
value(Expr, boolean(false)) :- tuple_equality(Expr, eq, _, _), tuple_unequal(Expr).
value(Expr, boolean(false)) :- tuple_equality(Expr, neq, _, _), not tuple_unequal(Expr).
value(Expr, boolean(true)) :- tuple_equality(Expr, neq, _, _), tuple_unequal(Expr).

equality_scalar(Expr, Op) :- equality_operands(Expr, Op, Left, Right),
    equality_tuple_subject(Left), equality_set(Right).
equality_scalar(Expr, Op) :- equality_operands(Expr, Op, Left, Right),
    equality_set(Left), equality_tuple_subject(Right).