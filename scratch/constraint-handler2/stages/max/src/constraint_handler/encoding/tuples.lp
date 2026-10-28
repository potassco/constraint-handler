tuple_argument_defined(Id, Index) :- tuple_argument(Id, Index, Arg), value(Arg, _).
value(Id, tuple) :- tuple_arity(Id, _),
    tuple_argument_defined(Id, Index) : tuple_argument(Id, Index, _).
tuple_size(Id, Size) :- tuple_arity(Id, Size), value(Id, tuple).
payload_copy(__tuple(Id, Index), Arg) :-
    tuple_argument(Id, Index, Arg), value(Id, tuple).

payload_copy(Id, __tuple(Arg, Index)) :-
    native_expression(Id, operation(tuple_get, (Arg, Position))),
    value(Arg, tuple), tuple_size(Arg, Size), value(Position, integer(Index)),
    Index >= 0, Index < Size.
value(Id, integer(Size)) :- native_expression(Id, operation(length, (Arg,))),
    value(Arg, tuple), tuple_size(Arg, Size).

variable_tuple_choice(Name, ExprId) :- variable_choose(Name, ExprId, ConditionId, _),
    value(ExprId, tuple), value(ConditionId, boolean(true)).
{ variable_value(Name, ExprId) } :- variable_tuple_choice(Name, ExprId).
payload_pair(variable(Name), ExprId) :- variable_tuple_choice(Name, ExprId).
variable_value(Name, ExprId) :- variable_tuple_choice(Name, ExprId),
    value(variable(Name), tuple), not payload_difference(variable(Name), ExprId).

equality_tuple_subject(Arg) :- equality_input(Arg), value(Arg, tuple).
equality_input(__tuple(Arg, Index)) :- equality_tuple_subject(Arg),
    tuple_size(Arg, Size), Index = 0..Size-1.
tuple_equality(Id, Op, Left, Right) :- equality_operands(Id, Op, Left, Right),
    equality_tuple_subject(Left), equality_tuple_subject(Right).
tuple_slot_match(Id, Index) :- tuple_equality(Id, _, Left, Right),
    tuple_size(Left, Size), Index = 0..Size-1,
    equality_scalar_key(__tuple(Left, Index), Key),
    equality_scalar_key(__tuple(Right, Index), Key).
tuple_slot_set(Id, Index, Left, Right) :- tuple_equality(Id, _, Left, Right),
    tuple_size(Left, Size), Index = 0..Size-1,
    value(__tuple(Left, Index), set), value(__tuple(Right, Index), set).
tuple_set_difference(Id, Index) :- tuple_slot_set(Id, Index, Left, Right),
    equality_set_key(__tuple(Left, Index), Key),
    not equality_set_key(__tuple(Right, Index), Key).
tuple_set_difference(Id, Index) :- tuple_slot_set(Id, Index, Left, Right),
    equality_set_key(__tuple(Right, Index), Key),
    not equality_set_key(__tuple(Left, Index), Key).
tuple_slot_match(Id, Index) :- tuple_slot_set(Id, Index, _, _),
    not tuple_set_difference(Id, Index).
tuple_unequal(Id) :- tuple_equality(Id, _, Left, Right),
    tuple_size(Left, Size), not tuple_size(Right, Size).
tuple_unequal(Id) :- tuple_equality(Id, _, Left, Right),
    tuple_size(Right, Size), not tuple_size(Left, Size).
tuple_unequal(Id) :- tuple_equality(Id, _, Left, _), tuple_size(Left, Size),
    Index = 0..Size-1, not tuple_slot_match(Id, Index).
value(Id, boolean(true)) :- tuple_equality(Id, eq, _, _), not tuple_unequal(Id).
value(Id, boolean(false)) :- tuple_equality(Id, eq, _, _), tuple_unequal(Id).
value(Id, boolean(false)) :- tuple_equality(Id, neq, _, _), not tuple_unequal(Id).
value(Id, boolean(true)) :- tuple_equality(Id, neq, _, _), tuple_unequal(Id).

equality_scalar(Id, Op) :- equality_operands(Id, Op, Left, Right),
    equality_tuple_subject(Left), equality_set(Right).
equality_scalar(Id, Op) :- equality_operands(Id, Op, Left, Right),
    equality_set(Left), equality_tuple_subject(Right).