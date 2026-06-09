_float_operation(ExprList) :-
    _expression(compile, operation((add;mult;sub;pow;abs;ceil;floor;minus;int_div;eq;neq;leq;lt;geq;gt;max;min), ExprList)),
    Arg = @pythonListElements(ExprList),
    _se_value(Arg, val(float, _)).
%%% Abdallah: works also on only ints but is float
_float_operation(ExprList) :- _expression(compile, operation(float_div, ExprList)).

%    @pythonFloatEval(Op, Val1, Val2)


%%%%%%%%%%%%%%%%% 1-ary operations

_se_value(operation(add, (Expr, ())), val(float, V)) :-
    _expression(compile, operation(add, (Expr, ()))),
    _se_value(Expr, val(float, V)).

_se_value(operation(mult, (Expr, ())), val(float, V)) :-
    _expression(compile, operation(mult, (Expr, ()))),
    _se_value(Expr, val(float, V)).

_unary_float_operation(abs;ceil;floor;minus).

_se_value(operation(OP, (Expr, ())), @pythonFloatUnary(OP, V)) :-
    _expression(compile, operation(OP, (Expr, ()))),
    _unary_float_operation(OP),
    _se_value(Expr, val(float, V)).



%%%%%%%%%%%%%%%%% nary operations

_float_add(add, ExprList, -1, val(float, float("0.0"))) :-
    _expression(compile, operation(add, ExprList)),
    _float_operation(ExprList).

_float_add(add, ExprList, Idx, @pythonFloatBinary(add, Val, ListVal)) :-
    _expression(compile, operation(add, ExprList)),
    _float_operation(ExprList),
    (Idx, Expr) = @pythonEnumerateElements(ExprList),
    _se_value(Expr, val((int;float), Val)),
    _float_add(add, ExprList, Idx-1, val(float, ListVal)).
    
_se_value(operation(add, ExprList), val(float, Val)) :-
    _expression(compile, operation(add, ExprList)),
    _float_operation(ExprList),
    Len = @pythonListLength(ExprList),
    _float_add(add, ExprList, Len-1, val(float, Val)).

_float_has_zero(ExprList) :-
    _expression(compile, operation(mult, ExprList)),
    _float_operation(ExprList),
    Arg = @pythonListElements(ExprList),
    _se_value(Arg, (val(float, "0.0"); val(int, 0))).

_float_mul(mult, ExprList, -1, val(float, float("1.0"))) :-
    _expression(compile, operation(mult, ExprList)),
    _float_operation(ExprList),
    not _float_has_zero(ExprList).

_float_mul(mult, ExprList, Idx, @pythonFloatBinary(mult, Val, ListVal)) :-
    _expression(compile, operation(mult, ExprList)),
    (Idx, Expr) = @pythonEnumerateElements(ExprList),
    _se_value(Expr, val((int;float), Val)),
    _float_mul(mult, ExprList, Idx-1, val(float, ListVal)).

_se_value(operation(mult, ExprList), val(float, Val)) :-
    _expression(compile, operation(mult, ExprList)),
    Len = @pythonListLength(ExprList),
    _float_mul(mult, ExprList, Len-1, val(float, Val)).

_se_value(operation(mult, ExprList), val(int, 0)) :- _float_has_zero(ExprList).

_se_value(operation(mult, ExprList), bad) :-
    _expression(compile, operation(mult, ExprList)),
    _float_operation(ExprList),
    Arg = @pythonListElements(ExprList),
    _se_value(Arg, bad),
    not _float_has_zero(ExprList).
  

%%%%%%%%%%%%%%%%% binary operations

_binary_float_operation(sub;pow;float_div;int_div;eq;neq;leq;lt;geq;gt;max;min).

_se_value(operation(OP, (Expr1, (Expr2, ()))), @pythonFloatBinary(OP, Val1, Val2)) :-
    _expression(compile, operation(OP, (Expr1, (Expr2, ())))),
    _float_operation((Expr1, (Expr2, ()))),
    _binary_float_operation(OP),
    _se_value(Expr1, val((int;float), Val1)),
    _se_value(Expr2, val((int;float), Val2)).
