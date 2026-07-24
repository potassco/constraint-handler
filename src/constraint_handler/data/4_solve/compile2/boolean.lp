%%%%%%%%%%%%%%%%% lnot, snot, wnot
_rev(true, false).
_rev(false, true).

:-
    _expression(compile2, operation(lnot, (Expr1, ()))),
    _se_value(Expr1, val(bool, NegVal)),
    _rev(NegVal, Val),
    not _se_value(operation(lnot, (Expr1, ())), val(bool, Val)).

:-
    _expression(compile2, operation(snot, (Expr1, ()))),
    _se_value(Expr1, val(bool, NegVal)),
    _rev(NegVal, Val),
    not _se_value(operation(snot, (Expr1, ())), val(bool, Val)).

:-
    _expression(compile2, operation(wnot, (Expr1, ()))),
    _se_value(Expr1, val(bool, NegVal)),
    _rev(NegVal, Val),
    not _se_value(operation(wnot, (Expr1, ())), val(bool, Val)).

:-
    _expression(compile2, operation(lnot, (Expr1, ()))),
    _se_value(Expr1, val(none, none)),
    not _se_value(operation(lnot, (Expr1, ())), val(none, none)).

:-
    _expression(compile2, operation(snot, (Expr1, ()))),
    _se_value(Expr1, val(none, none)),
    not _se_value(operation(snot, (Expr1, ())), val(bool, false)).

:-
    _expression(compile2, operation(wnot, (Expr1, ()))),
    _se_value(Expr1, val(none, none)),
    not _se_value(operation(wnot, (Expr1, ())), val(bool, true)).

%%%%%%%%%%%%%%%%% conj disj limp

% conj
_conj_has_false(ExprList) :-
    _expression(compile2, operation(conj, ExprList)),
    _expression_operationIndex(compile2, operation(conj, ExprList), _, Arg),
    _se_value(Arg, val(bool, false)).

_conj_has_bad(ExprList) :-
    _expression(compile2, operation(conj, ExprList)),
    _expression_operationIndex(compile2, operation(conj, ExprList), _, Arg),
    _se_value(Arg, bad).

_conj_has_none(ExprList) :-
    _expression(compile2, operation(conj, ExprList)),
    _expression_operationIndex(compile2, operation(conj, ExprList), _, Arg),
    _se_value(Arg, val(none, none)).

_conj_all_true(ExprList) :-
    _expression(compile2, operation(conj, ExprList)),
    not _conj_has_false(ExprList),
    not _conj_has_none(ExprList),
    not _conj_has_bad(ExprList).

% false if false
:-
    _expression(compile2, operation(conj, ExprList)),
    _conj_has_false(ExprList),
    not _se_value(operation(conj, ExprList), val(bool, false)).

% true if all true
:-
    _expression(compile2, operation(conj, ExprList)),
    _conj_all_true(ExprList),
    not _se_value(operation(conj, ExprList), val(bool, true)).

% bad if not false and has bad
:-
    _expression(compile2, operation(conj, ExprList)),
    _conj_has_bad(ExprList),
    not _conj_has_false(ExprList),
    not _se_value(operation(conj, ExprList), bad).

% none if not false and not bad and has none
:-
    _expression(compile2, operation(conj, ExprList)),
    _conj_has_none(ExprList),
    not _conj_has_false(ExprList),
    not _conj_has_bad(ExprList),
    not _se_value(operation(conj, ExprList), val(none, none)).

% disj
_disj_has_true(ExprList) :-
    _expression(compile2, operation(disj, ExprList)),
    _expression_operationIndex(compile2, operation(disj, ExprList), _, Arg),
    _se_value(Arg, val(bool, true)).

_disj_has_bad(ExprList) :-
    _expression(compile2, operation(disj, ExprList)),
    _expression_operationIndex(compile2, operation(disj, ExprList), _, Arg),
    _se_value(Arg, bad).

_disj_has_none(ExprList) :-
    _expression(compile2, operation(disj, ExprList)),
    _expression_operationIndex(compile2, operation(disj, ExprList), _, Arg),
    _se_value(Arg, val(none, none)).

_disj_all_false(ExprList) :-
    _expression(compile2, operation(disj, ExprList)),
    not _disj_has_true(ExprList),
    not _disj_has_bad(ExprList),
    not _disj_has_none(ExprList).

% true if true
:-
    _expression(compile2, operation(disj, ExprList)),
    _disj_has_true(ExprList),
    not _se_value(operation(disj, ExprList), val(bool, true)).

% bad if not true and bad
:-
    _expression(compile2, operation(disj, ExprList)),
    _disj_has_bad(ExprList),
    not _disj_has_true(ExprList),
    not _se_value(operation(disj, ExprList), bad).

% none if not true and not bad and none
:-
    _expression(compile2, operation(disj, ExprList)),
    _disj_has_none(ExprList),
    not _disj_has_true(ExprList),
    not _disj_has_bad(ExprList),
    not _se_value(operation(disj, ExprList), val(none, none)).

% false if all false
:-
    _expression(compile2, operation(disj, ExprList)),
    _disj_all_false(ExprList),
    not _se_value(operation(disj, ExprList), val(bool, false)).

% limp % implication
_limp_true(E1, E2) :-
    _expression(compile2, operation(limp, (E1, (E2, ())))),
    _se_value(E1, val(bool, false)).

_limp_true(E1, E2) :-
    _expression(compile2, operation(limp, (E1, (E2, ())))),
    _se_value(E2, val(bool, true)).

_limp_false(E1, E2) :-
    _expression(compile2, operation(limp, (E1, (E2, ())))),
    _se_value(E1, val(bool, true)),
    _se_value(E2, val(bool, false)).

_limp_none(E1, E2) :-
    _expression(compile2, operation(limp, (E1, (E2, ())))),
    _se_value(E1, val(bool, true)),
    _se_value(E2, val(none, none)).

_limp_none(E1, E2) :-
    _expression(compile2, operation(limp, (E1, (E2, ())))),
    _se_value(E1, val(none, none)),
    _se_value(E2, val(bool, false)).

_limp_none(E1, E2) :-
    _expression(compile2, operation(limp, (E1, (E2, ())))),
    _se_value(E1, val(none, none)),
    _se_value(E2, val(none, none)).

_limp_bad(E1, E2) :-
    _expression(compile2, operation(limp, (E1, (E2, ())))),
    _se_value(E1, bad),
    not _se_value(E2, val(bool, true)).

_limp_bad(E1, E2) :-
    _expression(compile2, operation(limp, (E1, (E2, ())))),
    _se_value(E2, bad),
    not _se_value(E1, val(bool, false)).

:-
    _expression(compile2, operation(limp, (Expr1, (Expr2, ())))),
    _limp_true(Expr1, Expr2),
    not _se_value(operation(limp, (Expr1, (Expr2, ()))), val(bool, true)).

:-
    _expression(compile2, operation(limp, (Expr1, (Expr2, ())))),
    _limp_false(Expr1, Expr2),
    not _se_value(operation(limp, (Expr1, (Expr2, ()))), val(bool, false)).

:-
    _expression(compile2, operation(limp, (Expr1, (Expr2, ())))),
    _limp_none(Expr1, Expr2),
    not _se_value(operation(limp, (Expr1, (Expr2, ()))), val(none, none)).

:-
    _expression(compile2, operation(limp, (Expr1, (Expr2, ())))),
    _limp_bad(Expr1, Expr2),
    not _se_value(operation(limp, (Expr1, (Expr2, ()))), bad).


%%%%%%%%%%%%%%%%% lxor leqv
% this implementation of lxor and leqv is not very efficient,
% can be much better if we have a binary xor
_bool_has_bad(ExprList) :-
    _expression(compile2, operation((lxor;leqv), ExprList)),
    _expression_operationIndex(compile2, operation((lxor;leqv), ExprList), _, Arg),
    _se_value(Arg, bad).

:-
    _expression(compile2, operation(OP, ExprList)),
    _bool_has_bad(ExprList),
    OP = (lxor;leqv),
    not _se_value(operation(OP, ExprList), bad).

:-
    _expression(compile2,operation(lxor, ExprList)),
    not _bool_has_bad(ExprList),
    N = #count { Idx : _se_value(Arg, val(bool,true)), _expression_operationIndex(compile2, operation(lxor, ExprList), Idx, Arg) }, N \ 2 = 1,
    not _se_value(operation(lxor, ExprList),val(bool,true)).
:- _expression(compile2,operation(lxor, ExprList)),
    not _bool_has_bad(ExprList),
    N = #count { Idx : _se_value(Arg, val(bool,true)), _expression_operationIndex(compile2, operation(lxor, ExprList), Idx, Arg) }, N \ 2 = 0,
    not _se_value(operation(lxor, ExprList),val(bool,false)).

:- _expression(compile2,operation(leqv, ExprList)),
    not _bool_has_bad(ExprList),
    N = #count { Idx : _se_value(Arg, val(bool,false)), _expression_operationIndex(compile2, operation(leqv, ExprList), Idx, Arg) }, N \ 2 = 0,
    not _se_value(operation(leqv, ExprList),val(bool,true)).
:- _expression(compile2,operation(leqv, ExprList)),
    not _bool_has_bad(ExprList),
    N = #count { Idx : _se_value(Arg, val(bool,false)), _expression_operationIndex(compile2, operation(leqv, ExprList), Idx, Arg) }, N \ 2 = 1,
    not _se_value(operation(leqv, ExprList),val(bool,false)).

%%%%%%%%%%%%%%%%%% ite
:-
    _expression(compile2, operation(ite,(E1,(E2,(E3,()))))),
    _se_value(E1, val(bool, true)),
    _se_value(E2, Value),
    not _se_value(operation(ite,(E1,(E2,(E3,())))), Value).

:-
    _expression(compile2, operation(ite,(E1,(E2,(E3,()))))),
    _se_value(E1, val(bool, false)),
    _se_value(E3, Value),
    not _se_value(operation(ite,(E1,(E2,(E3,())))), Value).

%%% Abdallah: not python compatible?
:-
    _expression(compile2, operation(ite,(E1,(E2,(E3,()))))),
    _se_value(E1, val(none, none)),
    not _se_value(operation(ite,(E1,(E2,(E3,())))), val(none, none)).

:-
    _expression(compile2, operation(ite,(E1,(E2,(E3,()))))),
    _se_value(E1, bad),
    not _se_value(operation(ite,(E1,(E2,(E3,())))), bad).

_set_contains(operation(ite,(E1,(E2,(E3,())))), Val) :-
    _expression(compile2, operation(ite,(E1,(E2,(E3,()))))),
    _se_value(E1, val(bool, true)),
    _set_contains(E2, Val).

_set_contains(operation(ite,(E1,(E2,(E3,())))), Val) :-
    _expression(compile2, operation(ite,(E1,(E2,(E3,()))))),
    _se_value(E1, val(bool, false)),
    _set_contains(E3, Val).

%%%%%%%%%%%%%%%%%%% if
:-
    _expression(compile2, operation(if,(E1,(E2,())))),
    _se_value(E1, val(bool, true)),
    _se_value(E2, Value),
    not _se_value(operation(if,(E1,(E2,()))), Value).

:-
    _expression(compile2, operation(if,(E1,(E2,())))),
    _se_value(E1, val(bool, false)),
    not _se_value(operation(if,(E1,(E2,()))), val(none, none)).

:-
    _expression(compile2, operation(if,(E1,(E2,())))),
    _se_value(E1, val(none, none)),
    not _se_value(operation(if,(E1,(E2,()))), val(none, none)).

:-
    _expression(compile2, operation(if,(E1,(E2,())))),
    _se_value(E1, bad),
    not _se_value(operation(if,(E1,(E2,()))), bad).

_set_contains(operation(if,(E1,(E2,()))), Val) :-
    _expression(compile2, operation(if,(E1,(E2,())))),
    _se_value(E1, val(bool, true)),
    _set_contains(E2, Val).

%%%%%%%%%%%%%%%%%% default
:-
    _expression(compile2, operation(default,(E1,E2))),
    _se_value(E1, Value),
    Value != val(none, none),
    not _se_value(operation(default,(E1,E2)), Value).

:-
    _expression(compile2, operation(default,(E1,(E2,())))),
    _se_value(E1, val(none, none)),
    _se_value(E2, Value),
    not _se_value(operation(default,(E1,(E2,()))), Value).

%%%%%%%%%%%%%%%%%% hasValue
:-
    _expression(compile2, operation(hasValue,(E1,()))),
    not _se_value(E1, val(none, none)),
    not _se_value(E1, bad),
    not _se_value(operation(hasValue,(E1,())), val(bool, true)).

:-
    _expression(compile2, operation(hasValue,(E1,()))),
    _se_value(E1, val(none, none)),
    not _se_value(operation(hasValue,(E1,())), val(bool, false)).

%%% Abdallah: should bad input become bad output? --> see bad.lp
%_se_value(operation(hasValue,(E1,())), bad) :-
%    _expression(compile2, operation(hasValue,(E1,()))),
%    _se_value(E1, bad).
