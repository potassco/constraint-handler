%%%%%%%%%%%%%%%%% length

:-
    _expression(compile2, operation(length, (Expr, ()))),
    _se_value(Expr, val(string, S)),
    N=@pythonStringLength(S),
    not _se_value(operation(length, (Expr, ())), val(int, N)).

%%%%%%%%%%%%%%%%% concat

:-
    _expression(compile2, operation(concat, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(string, S1)),
    _se_value(Expr2, val(string, S2)),
    R=@pythonStringAdd(S1,S2),
    not _se_value(operation(concat, (Expr1, (Expr2, ()))), val(string, R)).

%%%%%%%%%%%%%%%%%%%% leq

:-
    _expression(compile2, operation(leq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(string, S1)),
    _se_value(Expr2, val(string, S2)),
    S1 <= S2,
    not _se_value(operation(leq, (Expr1, (Expr2, ()))), val(bool, true)).

:-
    _expression(compile2, operation(leq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(string, S1)),
    _se_value(Expr2, val(string, S2)),
    S1 > S2,
    not _se_value(operation(leq, (Expr1, (Expr2, ()))), val(bool, false)).

%%%%%%%%%%%%%%%%%%%%% lt

:-
    _expression(compile2, operation(lt, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(string, S1)),
    _se_value(Expr2, val(string, S2)),
    S1 < S2,
    not _se_value(operation(lt, (Expr1, (Expr2, ()))), val(bool, true)).

:-
    _expression(compile2, operation(lt, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(string, S1)),
    _se_value(Expr2, val(string, S2)),
    S1 >= S2,
    not _se_value(operation(lt, (Expr1, (Expr2, ()))), val(bool, false)).

%%%%%%%%%%%%%%%%%%%%%% geq

:-
    _expression(compile2, operation(geq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(string, S1)),
    _se_value(Expr2, val(string, S2)),
    S1 >= S2,
    not _se_value(operation(geq, (Expr1, (Expr2, ()))), val(bool, true)).

:-
    _expression(compile2, operation(geq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(string, S1)),
    _se_value(Expr2, val(string, S2)),
    S1 < S2,
    not _se_value(operation(geq, (Expr1, (Expr2, ()))), val(bool, false)).

%%%%%%%%%%%%%%%%%%%%%% gt

:-
    _expression(compile2, operation(gt, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(string, S1)),
    _se_value(Expr2, val(string, S2)),
    S1 > S2,
    not _se_value(operation(gt, (Expr1, (Expr2, ()))), val(bool, true)).

:-
    _expression(compile2, operation(gt, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(string, S1)),
    _se_value(Expr2, val(string, S2)),
    S1 <= S2,
    not _se_value(operation(gt, (Expr1, (Expr2, ()))), val(bool, false)).
