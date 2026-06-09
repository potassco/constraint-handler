:- _passed(compile, LBL, ensure(Expr)),
   not _se_value(Expr, val(bool, true)),
   not _se_value(Expr, bad).