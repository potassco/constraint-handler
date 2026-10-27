%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% set expressions
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


set_operands(Id, Op, Left, Right) :-
    native_expression(Id, operation(Op, (Left, Right))),
    Op = (union; inter; diff; subset; eq; neq),
    value(Left, set), value(Right, set).

value(Id, set) :-
    set_operands(Id, Op, _, _), Op = (union; inter; diff).

set_value(Id, Member) :-
    set_operands(Id, union, Left, _), set_value(Left, Member).
set_value(Id, Member) :-
    set_operands(Id, union, _, Right), set_value(Right, Member).
set_value(Id, Member) :-
    set_operands(Id, inter, Left, Right),
    set_value(Left, Member), set_value(Right, Member).
set_value(Id, Member) :-
    set_operands(Id, diff, Left, Right),
    set_value(Left, Member), not set_value(Right, Member).

set_left_difference(Id) :-
    set_operands(Id, subset, Left, Right),
    set_value(Left, Member), not set_value(Right, Member).

value(Id, boolean(false)) :-
    set_operands(Id, subset, _, _), set_left_difference(Id).
value(Id, boolean(true)) :-
    set_operands(Id, subset, _, _), not set_left_difference(Id).

set_unequal(Id) :-
    set_operands(Id, Op, Left, Right), Op = (eq; neq),
    equality_set_key(Left, Key), not equality_set_key(Right, Key).
set_unequal(Id) :-
    set_operands(Id, Op, Left, Right), Op = (eq; neq),
    equality_set_key(Right, Key), not equality_set_key(Left, Key).

value(Id, boolean(true)) :- set_operands(Id, eq, _, _), not set_unequal(Id).
value(Id, boolean(false)) :- set_operands(Id, eq, _, _), set_unequal(Id).
value(Id, boolean(true)) :- set_operands(Id, neq, _, _), set_unequal(Id).
value(Id, boolean(false)) :- set_operands(Id, neq, _, _), not set_unequal(Id).

set_membership(Id, Op, Member, Set) :-
    native_expression(Id, operation(Op, (Element, Set))), Op = (set_isin; set_notin),
    value(Element, Member), value(Set, set).

value(Id, boolean(true)) :-
    set_membership(Id, set_isin, Member, Set), set_value(Set, Member).
value(Id, boolean(false)) :-
    set_membership(Id, set_isin, Member, Set), not set_value(Set, Member).
value(Id, boolean(false)) :-
    set_membership(Id, set_notin, Member, Set), set_value(Set, Member).
value(Id, boolean(true)) :-
    set_membership(Id, set_notin, Member, Set), not set_value(Set, Member).

value(Id, integer(Size)) :-
    native_expression(Id, operation(Op, (Set,))), Op = (cardinality; length),
    value(Set, set), Size = #count { Member : set_value(Set, Member) }.

set_argument_defined(Id, Arg) :- set_argument(Id, Arg), value(Arg, _).

value(Id, set) :-
    native_expression(Id, operation(set_make, _)),
    set_argument_defined(Id, Arg) : set_argument(Id, Arg).
set_value(Id, Member) :-
    native_expression(Id, operation(set_make, _)), value(Id, set),
    set_argument(Id, Arg), value(Arg, Member).