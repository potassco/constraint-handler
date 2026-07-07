%%% Abdallah: we are confused
bool_evaluated(Expr, Value) :-
    _passed(compile3, LBL, bool_evaluate(Expr)),
    _se_value(Expr, Value).

evaluated(Op, ExprList, Value) :-
    _passed(compile3, LBL, evaluate(Op, ExprList)),
    _se_value(operation(Op, ExprList), Value).

_eval_eq_comparable(Type) :- Type = bool.

evaluated(eq, (Expr1, (Expr2, ())), val(bool, true)) :-
    _passed(compile3, _, evaluate(eq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(Type, V)),
    _se_value(Expr2, val(Type, V)),
    _eval_eq_comparable(Type).

evaluated(eq, (Expr1, (Expr2, ())), val(bool, false)) :-
    _passed(compile3, _, evaluate(eq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(Type, V)),
    not _se_value(Expr2, val(Type, V)),
    not _se_value(Expr2, bad),
    _eval_eq_comparable(Type).

evaluated(eq, (Expr1, (Expr2, ())), val(bool, false)) :-
    _passed(compile3, _, evaluate(eq, (Expr1, (Expr2, ())))),
    _se_value(Expr2, val(Type, V)),
    not _se_value(Expr1, val(Type, V)),
    not _se_value(Expr1, bad),
    _eval_eq_comparable(Type).

evaluated(neq, (Expr1, (Expr2, ())), val(bool, true)) :-
    _passed(compile3, _, evaluate(neq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(Type, V)),
    not _se_value(Expr2, val(Type, V)),
    not _se_value(Expr2, bad),
    _eval_eq_comparable(Type).

evaluated(neq, (Expr1, (Expr2, ())), val(bool, true)) :-
    _passed(compile3, _, evaluate(neq, (Expr1, (Expr2, ())))),
    _se_value(Expr2, val(Type, V)),
    not _se_value(Expr1, val(Type, V)),
    not _se_value(Expr1, bad),
    _eval_eq_comparable(Type).

evaluated(neq, (Expr1, (Expr2, ())), val(bool, false)) :-
    _passed(compile3, _, evaluate(neq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(Type, V)),
    _se_value(Expr2, val(Type, V)),
    _eval_eq_comparable(Type).