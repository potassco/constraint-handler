%%%%%%%%%%%%%%%%% add
%%% Abdallah: what about none handling

_expression_badArgument(ExprList) :- _expression_operationIndex(compile2, operation((add;mult), ExprList), _, Arg),
    _se_value(Arg,bad).

_non_integer_operation(ExprList) :- _expression(compile2, operation((add;mult), ExprList)),
    _expression_operationIndex(compile2, operation((add;mult), ExprList), _, Arg),
    not _type_dynamic(compile2,Arg,int),
    not _type_dynamic(compile2,Arg,bool),
    not _se_value(Arg,bad).

:-
    _expression(compile2, operation(add, ())),
    not _se_value(operation(add, ()), val(int, 0)).

:-
    _expression(compile2, operation(add, (Expr1, ()))),
    _se_value(Expr1, val(T, V)), (T,V,N)=((int,V,V);(bool,true,1);(bool,false,0)),
    not _se_value(operation(add, (Expr1, ())), val(int, N)).

%%% binary add special handling
:-
    _expression(compile2, operation(add, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(T1, V1)), (T1,V1,N1)=((int,V1,V1);(bool,true,1);(bool,false,0)),
    _se_value(Expr2, val(T2, V2)), (T2,V2,N2)=((int,V2,V2);(bool,true,1);(bool,false,0)),
    not _se_value(operation(add, (Expr1, (Expr2, ()))), val(int, N1 + N2)).

%%% n-ary add
:-
    _expression(compile2, operation(add, ExprList)),
    not _non_integer_operation(ExprList),
    not _expression_badArgument(ExprList),
    _expression_operationLength(compile2, operation(add, ExprList), Len),
    Len > 2,
    V = #sum { V1, Idx : _se_value(Arg, val(int, V1)), _expression_operationIndex(compile2, operation(add, ExprList), Idx, Arg);
                1, Idx : _se_value(Arg, val(bool, true)), _expression_operationIndex(compile2, operation(add, ExprList), Idx, Arg) },
    not _se_value(operation(add, ExprList), val(int, V)).

%%%%%%%%%%%%%%%%% mult

_int_has_zero(ExprList) :-
    _expression(compile2, operation(mult, ExprList)),
    not _non_integer_operation(ExprList),
    _expression_operationIndex(compile2, operation(mult, ExprList), _, Arg),
    _se_value(Arg, val(T,V)), (T,V)=((int,0);(bool,false)).

:-
    _expression(compile2, operation(mult, ())),
    not _se_value(operation(mult, ()), val(int, 1)).

:-
    _expression(compile2, operation(mult, (Expr1, ()))),
    _se_value(Expr1, val(T, V)), (T,V,N)=((int,V,V);(bool,true,1);(bool,false,0)),
    not _se_value(operation(mult, (Expr1, ())), val(int, N)).

_int_mul(ExprList, -1, 1) :- _expression(compile2, operation(mult, ExprList)),
   not _non_integer_operation(ExprList),
   not _int_has_zero(ExprList).

_int_mul(ExprList, Idx, ListVal * Val) :- _expression(compile2, operation(mult, ExprList)),
    _expression_operationIndex(compile2, operation(mult, ExprList), Idx, Expr),
    _se_value(Expr, val(T, V)), (T,V,Val)=((int,V,V);(bool,true,1);(bool,false,0)),
    _int_mul(ExprList, Idx-1, ListVal).

:-
    _expression(compile2, operation(mult, ExprList)),
    _expression_operationLength(compile2, operation(mult, ExprList), Len),
    _int_mul(ExprList, Len-1, Val),
    not _se_value(operation(mult, ExprList), val(int, Val)).


:- _int_has_zero(ExprList), not _se_value(operation(mult, ExprList), val(int, 0)).

:- _expression_operationIndex(compile2, operation(mult, ExprList), _, Arg),
   _se_value(Arg, bad),
   not _int_has_zero(ExprList),
   not _se_value(operation(mult, ExprList), bad).

%%%%%%%%%%%%%%%%% sub

:-
    _expression(compile2, operation(sub, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(int, V1)),
    _se_value(Expr2, val(int, V2)),
    not _se_value(operation(sub, (Expr1, (Expr2, ()))), val(int, V1 - V2)).

%%%%%%%%%%%%%%%%% pow

:-
    _expression(compile2, operation(pow, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(int, V1)),
    _se_value(Expr2, val(int, V2)),
    not _se_value(operation(pow, (Expr1, (Expr2, ()))), val(int, V1 ** V2)).
%%% Abdallah: why do we need this special case? bad ** 0, none ** 0
:-
    _expression(compile2, operation(pow, (Expr1, (Expr2, ())))),
    _se_value(Expr2, val(int, 0)),
    not _se_value(operation(pow, (Expr1, (Expr2, ()))), val(int, 1)).

:-
    _expression(compile2, operation(pow, (Expr1, (Expr2, ())))),
    _se_value(Expr1, bad),
    not _se_value(Expr2, val(int, 0)),
    not _se_value(operation(pow, (Expr1, (Expr2, ()))), bad).

:-
    _expression(compile2, operation(pow, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(none, none)),
    not _se_value(Expr2, val(int, 0)),
    not _se_value(operation(pow, (Expr1, (Expr2, ()))), bad).

:-
    _expression(compile2, operation(pow, (Expr1, (Expr2, ())))),
    _se_value(Expr2, bad),
    not _se_value(operation(pow, (Expr1, (Expr2, ()))), bad).

%%%%%%%%%%%%%%%%% int_div

:-
    _expression(compile2, operation(int_div, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(int, V0)),
    _se_value(Expr2, val(int, V1)),
    V1 != 0,
    not _se_value(operation(int_div, (Expr1, (Expr2, ()))), val(int, V0 / V1)).

:-
    _expression(compile2, operation(int_div, (Expr1, (Expr2, ())))),
    _se_value(Expr2, val(int, 0)),
    not _se_value(operation(int_div, (Expr1, (Expr2, ()))), bad).

:-
    _expression(compile2, operation(float_div, (Expr1, (Expr2, ())))),
    _se_value(Expr2, val(int, 0)),
    not _se_value(operation(float_div, (Expr1, (Expr2, ()))), bad).

_warning(expression(zeroDivisionError),(),(int_div,(Expr1, (Expr2, ())))) :-
    _expression(compile2, operation(int_div, (Expr1, (Expr2, ())))),
    _se_value(Expr2, val(int, 0)).

%%%%%%%%%%%%%%%%% abs

:-
    _expression(compile2, operation(abs, (Expr1, ()))),
    _se_value(Expr1, val(int, V)),
    not _se_value(operation(abs, (Expr1, ())), val(int, |V|)).

%%%%%%%%%%%%%%%%% ceil

:-
    _expression(compile2, operation(ceil, (Expr1, ()))),
    _se_value(Expr1, val(int, V)),
    not _se_value(operation(ceil, (Expr1, ())), val(int, V)).

%%%%%%%%%%%%%%%%% floor

:-
    _expression(compile2, operation(floor, (Expr1, ()))),
    _se_value(Expr1, val(int, V)),
    not _se_value(operation(floor, (Expr1, ())), val(int, V)).

%%%%%%%%%%%%%%%%% unary minus

:-
    _expression(compile2, operation(minus, (Expr1, ()))),
    _se_value(Expr1, val(int, V)),
    not _se_value(operation(minus, (Expr1, ())), val(int, -V)).

%%%%%%%%%%%%%%%%% leq
%%% TODO: more generic leq/lt/geq/gt for all types?
%%% order encoding for generic types or at least integer? might need domain

:-
    _expression(compile2, operation(leq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(int, V1)),
    _se_value(Expr2, val(int, V2)),
    V1 <= V2,
    not _se_value(operation(leq, (Expr1, (Expr2, ()))), val(bool, true)).

:-
    _expression(compile2, operation(leq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(int, V1)),
    _se_value(Expr2, val(int, V2)),
    V1 > V2,
    not _se_value(operation(leq, (Expr1, (Expr2, ()))), val(bool, false)).

%%%%%%%%%%%%%%%%% lt

:-
    _expression(compile2, operation(lt, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(int, V1)),
    _se_value(Expr2, val(int, V2)),
    V1 < V2,
    not _se_value(operation(lt, (Expr1, (Expr2, ()))), val(bool, true)).

:-
    _expression(compile2, operation(lt, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(int, V1)),
    _se_value(Expr2, val(int, V2)),
    V1 >= V2,
    not _se_value(operation(lt, (Expr1, (Expr2, ()))), val(bool, false)).

%%%%%%%%%%%%%%%%% geq

:-
    _expression(compile2, operation(geq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(int, V1)),
    _se_value(Expr2, val(int, V2)),
    V1 >= V2,
    not _se_value(operation(geq, (Expr1, (Expr2, ()))), val(bool, true)).

:-
    _expression(compile2, operation(geq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(int, V1)),
    _se_value(Expr2, val(int, V2)),
    V1 < V2,
    not _se_value(operation(geq, (Expr1, (Expr2, ()))), val(bool, false)).

%%%%%%%%%%%%%%%%% gt

:-
    _expression(compile2, operation(gt, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(int, V1)),
    _se_value(Expr2, val(int, V2)),
    V1 > V2,
    not _se_value(operation(gt, (Expr1, (Expr2, ()))), val(bool, true)).

:-
    _expression(compile2, operation(gt, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(int, V1)),
    _se_value(Expr2, val(int, V2)),
    V1 <= V2,
    not _se_value(operation(gt, (Expr1, (Expr2, ()))), val(bool, false)).

%%%%%%%%%%%%%%%%% max
%%% Abdallah: Shouldn't these be n-ary?

:-
    _expression(compile2, operation(max, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(int, V1)),
    _se_value(Expr2, val(int, V2)),
    V1 <= V2,
    not _se_value(operation(max, (Expr1, (Expr2, ()))), val(int, V2)).

:-
    _expression(compile2, operation(max, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(int, V1)),
    _se_value(Expr2, val(int, V2)),
    V1 > V2,
    not _se_value(operation(max, (Expr1, (Expr2, ()))), val(int, V1)).

%%%%%%%%%%%%%%%%% min

:-
    _expression(compile2, operation(min, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(int, V1)),
    _se_value(Expr2, val(int, V2)),
    V1 > V2,
    not _se_value(operation(min, (Expr1, (Expr2, ()))), val(int, V2)).

:-
    _expression(compile2, operation(min, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(int, V1)),
    _se_value(Expr2, val(int, V2)),
    V1 <= V2,
    not _se_value(operation(min, (Expr1, (Expr2, ()))), val(int, V1)).
