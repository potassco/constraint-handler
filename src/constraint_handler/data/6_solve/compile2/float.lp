_float_operation(ExprList) :-
    _expression(compile2, operation((add;mult;sub;pow;abs;ceil;floor;minus;int_div;eq;neq;leq;lt;geq;gt;max;min), ExprList)),
    _expression_operationIndex(compile2, operation((add;mult;sub;pow;abs;ceil;floor;minus;int_div;eq;neq;leq;lt;geq;gt;max;min), ExprList), _, Arg),
    _type_dynamic(compile2,Arg,float).
%%% Abdallah: works also on only ints but is float
_float_operation(ExprList) :- _expression(compile2, operation(float_div, ExprList)).

%    @pythonFloatEval(Op, Val1, Val2)


%%%%%%%%%%%%%%%%% 1-ary operations

:-
    _expression(compile2, operation(add, (Expr, ()))),
    _se_value(Expr, val(float, V)),
    not _se_value(operation(add, (Expr, ())), val(float, V)).

:-
    _expression(compile2, operation(mult, (Expr, ()))),
    _se_value(Expr, val(float, V)),
    not _se_value(operation(mult, (Expr, ())), val(float, V)).

_unary_float_operation(abs;ceil;floor;minus).

:-
    _expression(compile2, operation(OP, (Expr, ()))),
    _unary_float_operation(OP),
    _se_value(Expr, val(float, V)),
    not _se_value(operation(OP, (Expr, ())), @pythonFloatUnary(OP, V)).



%%%%%%%%%%%%%%%%% nary operations

_float_add(add, ExprList, -1, val(float, float("0.0"))) :-
    _expression(compile2, operation(add, ExprList)),
    _float_operation(ExprList).

_float_add(add, ExprList, Idx, @pythonFloatBinary(add, Val, ListVal)) :-
    _expression(compile2, operation(add, ExprList)),
    _float_operation(ExprList),
    _expression_operationIndex(compile2, operation(add, ExprList), Idx, Expr),
    _se_value(Expr, val((int;float), Val)),
    _float_add(add, ExprList, Idx-1, val(float, ListVal)).

:-
    _expression(compile2, operation(add, ExprList)),
    _float_operation(ExprList),
    _expression_operationLength(compile2, operation(add, ExprList), Len),
    _float_add(add, ExprList, Len-1, val(float, Val)),
    not _se_value(operation(add, ExprList), val(float, Val)).

_float_has_zero(ExprList) :-
    _expression(compile2, operation(mult, ExprList)),
    _float_operation(ExprList),
    _expression_operationIndex(compile2, operation(mult, ExprList), _, Arg),
    _se_value(Arg, (val(float, "0.0"); val(int, 0))).

_float_mul(mult, ExprList, -1, val(float, float("1.0"))) :-
    _expression(compile2, operation(mult, ExprList)),
    _float_operation(ExprList),
    not _float_has_zero(ExprList).

_float_mul(mult, ExprList, Idx, @pythonFloatBinary(mult, Val, ListVal)) :-
    _expression(compile2, operation(mult, ExprList)),
    _expression_operationIndex(compile2, operation(mult, ExprList), Idx, Expr),
    _se_value(Expr, val((int;float), Val)),
    _float_mul(mult, ExprList, Idx-1, val(float, ListVal)).

:-
    _expression(compile2, operation(mult, ExprList)),
    _expression_operationLength(compile2, operation(mult, ExprList), Len),
    _float_mul(mult, ExprList, Len-1, val(float, Val)),
    not _se_value(operation(mult, ExprList), val(float, Val)).

:- _float_has_zero(ExprList), not _se_value(operation(mult, ExprList), val(int, 0)).

:-
    _expression(compile2, operation(mult, ExprList)),
    _float_operation(ExprList),
    _expression_operationIndex(compile2, operation(mult, ExprList), _, Arg),
    _se_value(Arg, bad),
    not _float_has_zero(ExprList),
    not _se_value(operation(mult, ExprList), bad).


%%%%%%%%%%%%%%%%% binary operations

_binary_float_operation(sub;pow;float_div;int_div;leq;lt;geq;gt;max;min).

_float_eq_used_expression(Expr) :-
    _expression(compile2, operation((eq;neq), (Expr, (OtherExpr, ())))).

_float_eq_used_expression(Expr) :-
    _expression(compile2, operation((eq;neq), (OtherExpr, (Expr, ())))).

_float_eq_value(Expr, FloatVal) :-
    _float_eq_used_expression(Expr),
    _se_value(Expr, val(float, FloatVal)).

_float_eq_value(Expr, FloatVal) :-
    _float_eq_used_expression(Expr),
    _se_value(Expr, val(int, IntVal)),
    val(float, FloatVal) = @pythonFloatBinary(add, IntVal, float("0.0")).

:-
    _expression(compile2, operation(eq, (Expr1, (Expr2, ())))),
    _float_operation((Expr1, (Expr2, ()))),
    _se_value(Expr1, val(none, none)),
    _se_value(Expr2, val(none, none)),
    not _se_value(operation(eq, (Expr1, (Expr2, ()))), val(bool, true)).

:-
    _expression(compile2, operation(eq, (Expr1, (Expr2, ())))),
    _float_operation((Expr1, (Expr2, ()))),
    _se_value(Expr1, val(none, none)),
    not _se_value(Expr2, val(none, none)),
    not _se_value(Expr2, bad),
    not _se_value(operation(eq, (Expr1, (Expr2, ()))), val(bool, false)).

:-
    _expression(compile2, operation(eq, (Expr1, (Expr2, ())))),
    _float_operation((Expr1, (Expr2, ()))),
    _se_value(Expr2, val(none, none)),
    not _se_value(Expr1, val(none, none)),
    not _se_value(Expr1, bad),
    not _se_value(operation(eq, (Expr1, (Expr2, ()))), val(bool, false)).

:-
    _expression(compile2, operation(eq, (Expr1, (Expr2, ())))),
    _float_operation((Expr1, (Expr2, ()))),
    _float_eq_value(Expr1, FloatVal),
    _float_eq_value(Expr2, FloatVal),
    not _se_value(operation(eq, (Expr1, (Expr2, ()))), val(bool, true)).

:-
    _expression(compile2, operation(eq, (Expr1, (Expr2, ())))),
    _float_operation((Expr1, (Expr2, ()))),
    _float_eq_value(Expr1, FloatVal),
    not _float_eq_value(Expr2, FloatVal),
    not _se_value(Expr2, val(none, none)),
    not _se_value(Expr2, bad),
    not _se_value(operation(eq, (Expr1, (Expr2, ()))), val(bool, false)).

:-
    _expression(compile2, operation(eq, (Expr1, (Expr2, ())))),
    _float_operation((Expr1, (Expr2, ()))),
    _float_eq_value(Expr2, FloatVal),
    not _float_eq_value(Expr1, FloatVal),
    not _se_value(Expr1, val(none, none)),
    not _se_value(Expr1, bad),
    not _se_value(operation(eq, (Expr1, (Expr2, ()))), val(bool, false)).

:-
    _expression(compile2, operation(neq, (Expr1, (Expr2, ())))),
    _float_operation((Expr1, (Expr2, ()))),
    _se_value(Expr1, val(none, none)),
    _se_value(Expr2, val(none, none)),
    not _se_value(operation(neq, (Expr1, (Expr2, ()))), val(bool, false)).

:-
    _expression(compile2, operation(neq, (Expr1, (Expr2, ())))),
    _float_operation((Expr1, (Expr2, ()))),
    _se_value(Expr1, val(none, none)),
    not _se_value(Expr2, val(none, none)),
    not _se_value(Expr2, bad),
    not _se_value(operation(neq, (Expr1, (Expr2, ()))), val(bool, true)).

:-
    _expression(compile2, operation(neq, (Expr1, (Expr2, ())))),
    _float_operation((Expr1, (Expr2, ()))),
    _se_value(Expr2, val(none, none)),
    not _se_value(Expr1, val(none, none)),
    not _se_value(Expr1, bad),
    not _se_value(operation(neq, (Expr1, (Expr2, ()))), val(bool, true)).

:-
    _expression(compile2, operation(neq, (Expr1, (Expr2, ())))),
    _float_operation((Expr1, (Expr2, ()))),
    _float_eq_value(Expr1, FloatVal),
    not _float_eq_value(Expr2, FloatVal),
    not _se_value(Expr2, val(none, none)),
    not _se_value(Expr2, bad),
    not _se_value(operation(neq, (Expr1, (Expr2, ()))), val(bool, true)).

:-
    _expression(compile2, operation(neq, (Expr1, (Expr2, ())))),
    _float_operation((Expr1, (Expr2, ()))),
    _float_eq_value(Expr2, FloatVal),
    not _float_eq_value(Expr1, FloatVal),
    not _se_value(Expr1, val(none, none)),
    not _se_value(Expr1, bad),
    not _se_value(operation(neq, (Expr1, (Expr2, ()))), val(bool, true)).

:-
    _expression(compile2, operation(neq, (Expr1, (Expr2, ())))),
    _float_operation((Expr1, (Expr2, ()))),
    _float_eq_value(Expr1, FloatVal),
    _float_eq_value(Expr2, FloatVal),
    not _se_value(operation(neq, (Expr1, (Expr2, ()))), val(bool, false)).

:-
    _expression(compile2, operation(OP, (Expr1, (Expr2, ())))),
    _float_operation((Expr1, (Expr2, ()))),
    _binary_float_operation(OP),
    _se_value(Expr1, val((int;float), Val1)),
    _se_value(Expr2, val((int;float), Val2)),
    not _se_value(operation(OP, (Expr1, (Expr2, ()))), @pythonFloatBinary(OP, Val1, Val2)).
