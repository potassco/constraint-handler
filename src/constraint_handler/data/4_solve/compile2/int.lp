%%%%%%%%%%%%%%%%% add
%%% Abdallah: what about none handling

_non_integer_operation(ExprList) :- _expression(compile2, operation((add;mult), ExprList)),
    _expression_operationIndex(compile2, operation((add;mult), ExprList), _, Arg),
    not _se_value(Arg, val(int, _)).

_se_value(operation(add, ()), val(int, 0)) :-
    _expression(compile2, operation(add, ())).

_se_value(operation(add, (Expr1, ())), val(int, V)) :-
    _expression(compile2, operation(add, (Expr1, ()))),
    _se_value(Expr1, val(int, V)).
    

%%% binary add special handling
_se_value(operation(add, (Expr1, (Expr2, ()))), val(int, V1 + V2)) :-
    _expression(compile2, operation(add, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(int, V1)),
    _se_value(Expr2, val(int, V2)).

%%% n-ary add
_se_value(operation(add, ExprList), val(int, V)) :-
    _expression(compile2, operation(add, ExprList)),
    not _non_integer_operation(ExprList),
    _expression_operationLength(compile2, operation(add, ExprList), Len),
    Len > 2,
    V = #sum { V1, Idx : _se_value(Arg, val(int, V1)), _expression_operationIndex(compile2, operation(add, ExprList), Idx, Arg) }.

%%%%%%%%%%%%%%%%% mult

_int_has_zero(ExprList) :-
    _expression(compile2, operation(mult, ExprList)),
    not _non_integer_operation(ExprList),
    _expression_operationIndex(compile2, operation(mult, ExprList), _, Arg),
    _se_value(Arg, val(int, 0)).

_se_value(operation(mult, ()), val(int, 1)) :-
    _expression(compile2, operation(mult, ())).

_se_value(operation(mult, (Expr1, ())), val(int, V)) :-
    _expression(compile2, operation(mult, (Expr1, ()))),
    _se_value(Expr1, val(int, V)).

_int_mul(ExprList, -1, 1) :- _expression(compile2, operation(mult, ExprList)),
   not _non_integer_operation(ExprList),
   not _int_has_zero(ExprList).

_int_mul(ExprList, Idx, ListVal * Val) :- _expression(compile2, operation(mult, ExprList)),
    _expression_operationIndex(compile2, operation(mult, ExprList), Idx, Expr),
    _se_value(Expr, val(int, Val)),
    _int_mul(ExprList, Idx-1, ListVal).

_se_value(operation(mult, ExprList), val(int, Val)) :-
    _expression(compile2, operation(mult, ExprList)),
    _expression_operationLength(compile2, operation(mult, ExprList), Len),
    _int_mul(ExprList, Len-1, Val).


_se_value(operation(mult, ExprList), val(int, 0)) :- _int_has_zero(ExprList).

_se_value(operation(mult, ExprList), bad) :-
    _expression(compile2, operation(mult, ExprList)),
    not _non_integer_operation(ExprList),
    _expression_operationIndex(compile2, operation(mult, ExprList), _, Arg),
    _se_value(Arg, bad),
    not _int_has_zero(ExprList).


%%%%%%%%%%%%%%%%% sub

_se_value(operation(sub, (Expr1, (Expr2, ()))), val(int, V1 - V2)) :-
    _expression(compile2, operation(sub, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(int, V1)),
    _se_value(Expr2, val(int, V2)).

%%%%%%%%%%%%%%%%% pow

_se_value(operation(pow, (Expr1, (Expr2, ()))), val(int, V1 ** V2)) :-
    _expression(compile2, operation(pow, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(int, V1)),
    _se_value(Expr2, val(int, V2)).
%%% Abdallah: why do we need this special case? bad ** 0, none ** 0
_se_value(operation(pow, (Expr1, (Expr2, ()))), val(int, 1)) :-
    _expression(compile2, operation(pow, (Expr1, (Expr2, ())))),
    _se_value(Expr1, V0),
    _se_value(Expr2, val(int, 0)).

_se_value(operation(pow, (Expr1, (Expr2, ()))), bad) :-
    _expression(compile2, operation(pow, (Expr1, (Expr2, ())))),
    _se_value(Expr1, bad),
    not _se_value(Expr2, val(int, 0)).

_se_value(operation(pow, (Expr1, (Expr2, ()))), bad) :-
    _expression(compile2, operation(pow, (Expr1, (Expr2, ())))),
    _se_value(Expr2, bad).

%%%%%%%%%%%%%%%%% int_div

_se_value(operation(int_div, (Expr1, (Expr2, ()))), val(int, V0 / V1)) :-
    _expression(compile2, operation(int_div, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(int, V0)),
    _se_value(Expr2, val(int, V1)),
    V1 != 0.

_se_value(operation((int_div;float_div), (Expr1, (Expr2, ()))), bad) :-
    _expression(compile2, operation((int_div;float_div), (Expr1, (Expr2, ())))),
    _se_value(Expr2, val(int, 0)).
%%% TODO: put float_div in float.lp and remove this
_warning(expression(zeroDivisionError),(),(int_div,(Expr1, (Expr2, ())))) :-
    _expression(compile2, operation(int_div, (Expr1, (Expr2, ())))),
    _se_value(Expr2, val(int, 0)).

%%%%%%%%%%%%%%%%% abs

_se_value(operation(abs, (Expr1, ())), val(int, |V|)) :-
    _expression(compile2, operation(abs, (Expr1, ()))),
    _se_value(Expr1, val(int, V)).

%%%%%%%%%%%%%%%%% ceil

_se_value(operation(ceil, (Expr1, ())), val(int, V)) :-
    _expression(compile2, operation(ceil, (Expr1, ()))),
    _se_value(Expr1, val(int, V)).

%%%%%%%%%%%%%%%%% floor

_se_value(operation(floor, (Expr1, ())), val(int, V)) :-
    _expression(compile2, operation(floor, (Expr1, ()))),
    _se_value(Expr1, val(int, V)).

%%%%%%%%%%%%%%%%% unary minus

_se_value(operation(minus, (Expr1, ())), val(int, -V)) :-
    _expression(compile2, operation(minus, (Expr1, ()))),
    _se_value(Expr1, val(int, V)).

%%%%%%%%%%%%%%%%% leq
%%% TODO: more generic leq/lt/geq/gt for all types?
%%% order encoding for generic types or at least integer? might need domain

_se_value(operation(leq, (Expr1, (Expr2, ()))), val(bool, true)) :-
    _expression(compile2, operation(leq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(int, V1)),
    _se_value(Expr2, val(int, V2)),
    V1 <= V2.

_se_value(operation(leq, (Expr1, (Expr2, ()))), val(bool, false)) :-
    _expression(compile2, operation(leq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(int, V1)),
    _se_value(Expr2, val(int, V2)),
    V1 > V2.

%%%%%%%%%%%%%%%%% lt

_se_value(operation(lt, (Expr1, (Expr2, ()))), val(bool, true)) :-
    _expression(compile2, operation(lt, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(int, V1)),
    _se_value(Expr2, val(int, V2)),
    V1 < V2.

_se_value(operation(lt, (Expr1, (Expr2, ()))), val(bool, false)) :-
    _expression(compile2, operation(lt, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(int, V1)),
    _se_value(Expr2, val(int, V2)),
    V1 >= V2.

%%%%%%%%%%%%%%%%% geq 

_se_value(operation(geq, (Expr1, (Expr2, ()))), val(bool, true)) :-
    _expression(compile2, operation(geq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(int, V1)),
    _se_value(Expr2, val(int, V2)),
    V1 >= V2.

_se_value(operation(geq, (Expr1, (Expr2, ()))), val(bool, false)) :-
    _expression(compile2, operation(geq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(int, V1)),
    _se_value(Expr2, val(int, V2)),
    V1 < V2.

%%%%%%%%%%%%%%%%% gt

_se_value(operation(gt, (Expr1, (Expr2, ()))), val(bool, true)) :-
    _expression(compile2, operation(gt, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(int, V1)),
    _se_value(Expr2, val(int, V2)),
    V1 > V2.

_se_value(operation(gt, (Expr1, (Expr2, ()))), val(bool, false)) :-
    _expression(compile2, operation(gt, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(int, V1)),
    _se_value(Expr2, val(int, V2)),
    V1 <= V2.

%%%%%%%%%%%%%%%%% max
%%% Abdallah: Shouldn't these be n-ary?

_se_value(operation(max, (Expr1, (Expr2, ()))), val(int, V2)) :-
    _expression(compile2, operation(max, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(int, V1)),
    _se_value(Expr2, val(int, V2)),
    V1 <= V2.

_se_value(operation(max, (Expr1, (Expr2, ()))), val(int, V1)) :-
    _expression(compile2, operation(max, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(int, V1)),
    _se_value(Expr2, val(int, V2)),
    V1 > V2.

%%%%%%%%%%%%%%%%% min

_se_value(operation(min, (Expr1, (Expr2, ()))), val(int, V2)) :-
    _expression(compile2, operation(min, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(int, V1)),
    _se_value(Expr2, val(int, V2)),
    V1 > V2.

_se_value(operation(min, (Expr1, (Expr2, ()))), val(int, V1)) :-
    _expression(compile2, operation(min, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(int, V1)),
    _se_value(Expr2, val(int, V2)),
    V1 <= V2.
