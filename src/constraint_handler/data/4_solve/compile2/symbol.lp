%%%%%%%%%%%%%%%%% leq
_se_domain(operation(leq, (Expr1, (Expr2, ()))), val(bool, true)) :-
    _expression(compile2, operation(leq, (Expr1, (Expr2, ())))),
    _se_domain(Expr1, val(symbol, S1)),
    _se_domain(Expr2, val(symbol, S2)),
    S1 <= S2.

_se_domain(operation(leq, (Expr1, (Expr2, ()))), val(bool, false)) :-
    _expression(compile2, operation(leq, (Expr1, (Expr2, ())))),
    _se_domain(Expr1, val(symbol, S1)),
    _se_domain(Expr2, val(symbol, S2)),
    S1 > S2.

%%%%%%%%%%%%%%%%% lt
_se_domain(operation(lt, (Expr1, (Expr2, ()))), val(bool, true)) :-
    _expression(compile2, operation(lt, (Expr1, (Expr2, ())))),
    _se_domain(Expr1, val(symbol, S1)),
    _se_domain(Expr2, val(symbol, S2)),
    S1 < S2.

_se_domain(operation(lt, (Expr1, (Expr2, ()))), val(bool, false)) :-
    _expression(compile2, operation(lt, (Expr1, (Expr2, ())))),
    _se_domain(Expr1, val(symbol, S1)),
    _se_domain(Expr2, val(symbol, S2)),
    S1 >= S2.

%%%%%%%%%%%%%%%%% geq
_se_domain(operation(geq, (Expr1, (Expr2, ()))), val(bool, true)) :-
    _expression(compile2, operation(geq, (Expr1, (Expr2, ())))),
    _se_domain(Expr1, val(symbol, S1)),
    _se_domain(Expr2, val(symbol, S2)),
    S1 >= S2.

_se_domain(operation(geq, (Expr1, (Expr2, ()))), val(bool, false)) :-
    _expression(compile2, operation(geq, (Expr1, (Expr2, ())))),
    _se_domain(Expr1, val(symbol, S1)),
    _se_domain(Expr2, val(symbol, S2)),
    S1 < S2.

%%%%%%%%%%%%%%%%% gt
_se_domain(operation(gt, (Expr1, (Expr2, ()))), val(bool, true)) :-
    _expression(compile2, operation(gt, (Expr1, (Expr2, ())))),
    _se_domain(Expr1, val(symbol, S1)),
    _se_domain(Expr2, val(symbol, S2)),
    S1 > S2.

_se_domain(operation(gt, (Expr1, (Expr2, ()))), val(bool, false)) :-
    _expression(compile2, operation(gt, (Expr1, (Expr2, ())))),
    _se_domain(Expr1, val(symbol, S1)),
    _se_domain(Expr2, val(symbol, S2)),
    S1 <= S2.


:-
    not _se_value(operation(leq, (Expr1, (Expr2, ()))), val(bool, true)),
    _expression(compile2, operation(leq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(symbol, S1)),
    _se_value(Expr2, val(symbol, S2)),
    S1 <= S2.

:-
    not _se_value(operation(leq, (Expr1, (Expr2, ()))), val(bool, false)),
    _expression(compile2, operation(leq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(symbol, S1)),
    _se_value(Expr2, val(symbol, S2)),
    S1 > S2.

:-
    not _se_value(operation(lt, (Expr1, (Expr2, ()))), val(bool, true)),
    _expression(compile2, operation(lt, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(symbol, S1)),
    _se_value(Expr2, val(symbol, S2)),
    S1 < S2.

:-
    not _se_value(operation(lt, (Expr1, (Expr2, ()))), val(bool, false)),
    _expression(compile2, operation(lt, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(symbol, S1)),
    _se_value(Expr2, val(symbol, S2)),
    S1 >= S2.

:-
    not _se_value(operation(geq, (Expr1, (Expr2, ()))), val(bool, true)),
    _expression(compile2, operation(geq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(symbol, S1)),
    _se_value(Expr2, val(symbol, S2)),
    S1 >= S2.

:-
    not _se_value(operation(geq, (Expr1, (Expr2, ()))), val(bool, false)),
    _expression(compile2, operation(geq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(symbol, S1)),
    _se_value(Expr2, val(symbol, S2)),
    S1 < S2.

:-
    not _se_value(operation(gt, (Expr1, (Expr2, ()))), val(bool, true)),
    _expression(compile2, operation(gt, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(symbol, S1)),
    _se_value(Expr2, val(symbol, S2)),
    S1 > S2.

:-
    not _se_value(operation(gt, (Expr1, (Expr2, ()))), val(bool, false)),
    _expression(compile2, operation(gt, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(symbol, S1)),
    _se_value(Expr2, val(symbol, S2)),
    S1 <= S2.