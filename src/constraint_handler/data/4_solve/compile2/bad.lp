
_bad_is_bad(add; sub; int_div; float_div; eq; neq; leq; lt; geq; gt; max; min;
    lnot; wnot; snot; lxor; leqv; hasValue; abs; ceil; floor; minus;
    length; concat).
    %% set_fold and implode?

_bad_on_none_ordered_comparison(leq; lt; geq; gt).

:-
    _expression(compile2, operation(OP, (Expr1, (Expr2, ())))),
    _bad_on_none_ordered_comparison(OP),
    _se_value(Expr1, val(none, none)),
    not _se_value(Expr2, bad),
    not _se_value(operation(OP, (Expr1, (Expr2, ()))), bad).

:-
    _expression(compile2, operation(OP, (Expr1, (Expr2, ())))),
    _bad_on_none_ordered_comparison(OP),
    _se_value(Expr2, val(none, none)),
    not _se_value(Expr1, bad),
    not _se_value(operation(OP, (Expr1, (Expr2, ()))), bad).

:-  _expression(compile2, operation(OP, ExprList)),
    _bad_is_bad(OP),
    _expression_operationIndex(compile2, operation(OP, ExprList), _, Arg),
    _se_value(Arg, bad),
    not _se_value(operation(OP, ExprList), bad).



% _se_value(operation(OP, ExprList), bad) :-
%     _expression(compile2, operation(OP, ExprList)),
%     _warning(type(failed_operation), (), (OP, ExprList)),
%     not _se_value(operation(OP, ExprList), val(_, _)),
%     not _se_value(operation(OP, ExprList), set).
