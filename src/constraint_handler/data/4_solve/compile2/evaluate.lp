%%% Abdallah: we are confused
bool_evaluated(Expr, Value) :-
    _passed(compile, LBL, bool_evaluate(Expr)),
    _se_value(Expr, Value).

evaluated(Op, ExprList, Value) :-
    _passed(compile, LBL, evaluate(Op, ExprList)),
    _se_value(operation(Op, ExprList), Value).