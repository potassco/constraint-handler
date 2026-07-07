%%%%%%%%%%%%%%%%% length

_se_domain(operation(length, (Expr, ())), val(int, N)) :- 
    _expression(compile3, operation(length, (Expr, ()))),
    _se_domain(Expr, val(string, S)),
    N=@pythonStringLength(S).

%%%%%%%%%%%%%%%%% concat

_se_domain(operation(concat, (Expr1, (Expr2, ()))), val(string, R)) :- 
    _expression(compile3, operation(concat, (Expr1, (Expr2, ())))), 
    _se_domain(Expr1, val(string, S1)),
    _se_domain(Expr2, val(string, S2)),
    R=@pythonStringAdd(S1,S2).

%%%%%%%%%%%%%%%%%%%% leq

_se_domain(operation(leq, (Expr1, (Expr2, ()))), val(bool, true)) :-
    _expression(compile3, operation(leq, (Expr1, (Expr2, ())))),
    _se_domain(Expr1, val(string, S1)),
    _se_domain(Expr2, val(string, S2)),
    S1 <= S2.

_se_domain(operation(leq, (Expr1, (Expr2, ()))), val(bool, false)) :-
    _expression(compile3, operation(leq, (Expr1, (Expr2, ())))),
    _se_domain(Expr1, val(string, S1)),
    _se_domain(Expr2, val(string, S2)),
    S1 > S2.

%%%%%%%%%%%%%%%%%%%%% lt

_se_domain(operation(lt, (Expr1, (Expr2, ()))), val(bool, true)) :-
    _expression(compile3, operation(lt, (Expr1, (Expr2, ())))),
    _se_domain(Expr1, val(string, S1)),
    _se_domain(Expr2, val(string, S2)),
    S1 < S2.

_se_domain(operation(lt, (Expr1, (Expr2, ()))), val(bool, false)) :-
    _expression(compile3, operation(lt, (Expr1, (Expr2, ())))),
    _se_domain(Expr1, val(string, S1)),
    _se_domain(Expr2, val(string, S2)),
    S1 >= S2.

%%%%%%%%%%%%%%%%%%%%%% geq

_se_domain(operation(geq, (Expr1, (Expr2, ()))), val(bool, true)) :-
    _expression(compile3, operation(geq, (Expr1, (Expr2, ())))),
    _se_domain(Expr1, val(string, S1)),
    _se_domain(Expr2, val(string, S2)),
    S1 >= S2.

_se_domain(operation(geq, (Expr1, (Expr2, ()))), val(bool, false)) :-
    _expression(compile3, operation(geq, (Expr1, (Expr2, ())))),
    _se_domain(Expr1, val(string, S1)),
    _se_domain(Expr2, val(string, S2)),
    S1 < S2.

%%%%%%%%%%%%%%%%%%%%%% gt

_se_domain(operation(gt, (Expr1, (Expr2, ()))), val(bool, true)) :-
    _expression(compile3, operation(gt, (Expr1, (Expr2, ())))),
    _se_domain(Expr1, val(string, S1)),
    _se_domain(Expr2, val(string, S2)),
    S1 > S2.

_se_domain(operation(gt, (Expr1, (Expr2, ()))), val(bool, false)) :-
    _expression(compile3, operation(gt, (Expr1, (Expr2, ())))),
    _se_domain(Expr1, val(string, S1)),
    _se_domain(Expr2, val(string, S2)),
    S1 <= S2.


:-
    not _se_value(operation(length, (Expr, ())), val(int, N)),
    _expression(compile3, operation(length, (Expr, ()))),
    _se_value(Expr, val(string, S)),
    N = @pythonStringLength(S).

:-
    not _se_value(operation(concat, (Expr1, (Expr2, ()))), val(string, R)),
    _expression(compile3, operation(concat, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(string, S1)),
    _se_value(Expr2, val(string, S2)),
    R = @pythonStringAdd(S1, S2).

:-
    not _se_value(operation(leq, (Expr1, (Expr2, ()))), val(bool, true)),
    _expression(compile3, operation(leq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(string, S1)),
    _se_value(Expr2, val(string, S2)),
    S1 <= S2.

:-
    not _se_value(operation(leq, (Expr1, (Expr2, ()))), val(bool, false)),
    _expression(compile3, operation(leq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(string, S1)),
    _se_value(Expr2, val(string, S2)),
    S1 > S2.

:-
    not _se_value(operation(lt, (Expr1, (Expr2, ()))), val(bool, true)),
    _expression(compile3, operation(lt, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(string, S1)),
    _se_value(Expr2, val(string, S2)),
    S1 < S2.

:-
    not _se_value(operation(lt, (Expr1, (Expr2, ()))), val(bool, false)),
    _expression(compile3, operation(lt, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(string, S1)),
    _se_value(Expr2, val(string, S2)),
    S1 >= S2.

:-
    not _se_value(operation(geq, (Expr1, (Expr2, ()))), val(bool, true)),
    _expression(compile3, operation(geq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(string, S1)),
    _se_value(Expr2, val(string, S2)),
    S1 >= S2.

:-
    not _se_value(operation(geq, (Expr1, (Expr2, ()))), val(bool, false)),
    _expression(compile3, operation(geq, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(string, S1)),
    _se_value(Expr2, val(string, S2)),
    S1 < S2.

:-
    not _se_value(operation(gt, (Expr1, (Expr2, ()))), val(bool, true)),
    _expression(compile3, operation(gt, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(string, S1)),
    _se_value(Expr2, val(string, S2)),
    S1 > S2.

:-
    not _se_value(operation(gt, (Expr1, (Expr2, ()))), val(bool, false)),
    _expression(compile3, operation(gt, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(string, S1)),
    _se_value(Expr2, val(string, S2)),
    S1 <= S2.