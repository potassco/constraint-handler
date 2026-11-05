%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% set expressions
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


set_operands(Expr, Op, Left, Right) :-
    native_expression(Expr), Expr = operation(Op, (Left, Right)),
    Op = (union; inter; diff; subset; eq; neq),
    value(Left, set), value(Right, set).

value(Expr, set) :-
    set_operands(Expr, Op, _, _), Op = (union; inter; diff).

set_value(Expr, Member) :-
    set_operands(Expr, union, Left, _), set_value(Left, Member).
set_value(Expr, Member) :-
    set_operands(Expr, union, _, Right), set_value(Right, Member).
set_value(Expr, Member) :-
    set_operands(Expr, inter, Left, Right),
    set_value(Left, Member), set_value(Right, Member).
set_value(Expr, Member) :-
    set_operands(Expr, diff, Left, Right),
    set_value(Left, Member), not set_value(Right, Member).

set_left_difference(Expr) :-
    set_operands(Expr, subset, Left, Right),
    set_value(Left, Member), not set_value(Right, Member).

value(Expr, boolean(false)) :-
    set_operands(Expr, subset, _, _), set_left_difference(Expr).
value(Expr, boolean(true)) :-
    set_operands(Expr, subset, _, _), not set_left_difference(Expr).

set_unequal(Expr) :-
    set_operands(Expr, Op, Left, Right), Op = (eq; neq),
    equality_set_key(Left, Key), not equality_set_key(Right, Key).
set_unequal(Expr) :-
    set_operands(Expr, Op, Left, Right), Op = (eq; neq),
    equality_set_key(Right, Key), not equality_set_key(Left, Key).

value(Expr, boolean(true)) :- set_operands(Expr, eq, _, _), not set_unequal(Expr).
value(Expr, boolean(false)) :- set_operands(Expr, eq, _, _), set_unequal(Expr).
value(Expr, boolean(true)) :- set_operands(Expr, neq, _, _), set_unequal(Expr).
value(Expr, boolean(false)) :- set_operands(Expr, neq, _, _), not set_unequal(Expr).

set_membership(Expr, Op, Member, Set) :-
    native_expression(Expr), Expr = operation(Op, (Element, Set)), Op = (set_isin; set_notin),
    value(Element, Member), value(Set, set).

value(Expr, boolean(true)) :-
    set_membership(Expr, set_isin, Member, Set), set_value(Set, Member).
value(Expr, boolean(false)) :-
    set_membership(Expr, set_isin, Member, Set), not set_value(Set, Member).
value(Expr, boolean(false)) :-
    set_membership(Expr, set_notin, Member, Set), set_value(Set, Member).
value(Expr, boolean(true)) :-
    set_membership(Expr, set_notin, Member, Set), not set_value(Set, Member).

value(Expr, integer(Size)) :-
    native_expression(Expr), Expr = operation(Op, (Set,)), Op = (cardinality; length),
    value(Set, set), Size = #count { Member : set_value(Set, Member) }.

set_argument_defined(Expr, Arg) :- set_argument(Expr, Arg), value(Arg, _).

value(Expr, set) :-
    native_expression(Expr), Expr = operation(set_make, _),
    set_argument_defined(Expr, Arg) : set_argument(Expr, Arg).
set_value(Expr, Member) :-
    native_expression(Expr), Expr = operation(set_make, _), value(Expr, set),
    set_argument(Expr, Arg), value(Arg, Member).