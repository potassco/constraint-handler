%%%%%%%%%%%%%%%%% length

_se_value(operation(length, (Expr, ())), val(int, N)) :- 
    _expression(compile2, operation(length, (Expr, ()))),
    _se_value(Expr, val(string, S)),
    N=@pythonStringLength(S).

%%%%%%%%%%%%%%%%% concat

_se_value(operation(concat, (Expr1, (Expr2, ()))), val(string, R)) :- 
    _expression(compile2, operation(concat, (Expr1, (Expr2, ())))), 
    _se_value(Expr1, val(string, S1)),
    _se_value(Expr2, val(string, S2)),
    R=@pythonStringAdd(S1,S2).

%%%%%%%%%%%%%%%%% eq neq
_se_value(operation(eq, (Expr1, (Expr2, ()))), val(bool, true)) :-
    _expression(compile2, operation(eq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(string, V)),
    _se_value(Expr2, val(string, V)).

_se_value(operation(eq, (Expr1, (Expr2, ()))), val(bool, false)) :-
    _expression(compile2, operation(eq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(string, V)),
    not _se_value(Expr2, val(string, V)),
    not _se_value(Expr2, bad).

%%% TODO: do I actually need both directions?
_se_value(operation(eq, (Expr1, (Expr2, ()))), val(bool, false)) :-
    _expression(compile2, operation(eq, (Expr1, (Expr2, ())))),
    _se_value(Expr2, val(string, V)),
    not _se_value(Expr1, val(string, V)),
    not _se_value(Expr1, bad).

_se_value(operation(neq, (Expr1, (Expr2, ()))), val(bool, true)) :-
    _expression(compile2, operation(neq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(string, V)),
    not _se_value(Expr2, val(string, V)),
    not _se_value(Expr2, bad).

_se_value(operation(neq, (Expr1, (Expr2, ()))), val(bool, true)) :-
    _expression(compile2, operation(neq, (Expr1, (Expr2, ())))),
    _se_value(Expr2, val(string, V)),
    not _se_value(Expr1, val(string, V)),
    not _se_value(Expr1, bad).

_se_value(operation(neq, (Expr1, (Expr2, ()))), val(bool, false)) :-
    _expression(compile2, operation(neq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(string, V)),
    _se_value(Expr2, val(string, V)).


%%%%%%%%%%%%%%%%%%%% leq

_se_value(operation(leq, (Expr1, (Expr2, ()))), val(bool, true)) :-
    _expression(compile2, operation(leq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(string, S1)),
    _se_value(Expr2, val(string, S2)),
    S1 <= S2.

_se_value(operation(leq, (Expr1, (Expr2, ()))), val(bool, false)) :-
    _expression(compile2, operation(leq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(string, S1)),
    _se_value(Expr2, val(string, S2)),
    S1 > S2.

%%%%%%%%%%%%%%%%%%%%% lt

_se_value(operation(lt, (Expr1, (Expr2, ()))), val(bool, true)) :-
    _expression(compile2, operation(lt, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(string, S1)),
    _se_value(Expr2, val(string, S2)),
    S1 < S2.

_se_value(operation(lt, (Expr1, (Expr2, ()))), val(bool, false)) :-
    _expression(compile2, operation(lt, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(string, S1)),
    _se_value(Expr2, val(string, S2)),
    S1 >= S2.

%%%%%%%%%%%%%%%%%%%%%% geq

_se_value(operation(geq, (Expr1, (Expr2, ()))), val(bool, true)) :-
    _expression(compile2, operation(geq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(string, S1)),
    _se_value(Expr2, val(string, S2)),
    S1 >= S2.

_se_value(operation(geq, (Expr1, (Expr2, ()))), val(bool, false)) :-
    _expression(compile2, operation(geq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(string, S1)),
    _se_value(Expr2, val(string, S2)),
    S1 < S2.

%%%%%%%%%%%%%%%%%%%%%% gt

_se_value(operation(gt, (Expr1, (Expr2, ()))), val(bool, true)) :-
    _expression(compile2, operation(gt, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(string, S1)),
    _se_value(Expr2, val(string, S2)),
    S1 > S2.

_se_value(operation(gt, (Expr1, (Expr2, ()))), val(bool, false)) :-
    _expression(compile2, operation(gt, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(string, S1)),
    _se_value(Expr2, val(string, S2)),
    S1 <= S2.