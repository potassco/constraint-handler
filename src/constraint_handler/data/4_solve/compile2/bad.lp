
_bad_is_bad(add; sub; int_div; float_div; eq; neq; leq; lt; geq; gt; max; min;
    lnot; wnot; snot; lxor; leqv; hasValue; abs; ceil; floor; minus;
    length; set_make; union; inter; diff; subset; set_isin; set_notin; concat).
    %% set_fold and implode?

_se_value(operation(OP, ExprList), bad) :-
    _expression(compile2, operation(OP, ExprList)),
    _bad_is_bad(OP),
    Arg = @pythonListElements(ExprList),
    _se_value(Arg, bad).