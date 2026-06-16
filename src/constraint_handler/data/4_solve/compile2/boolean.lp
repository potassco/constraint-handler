%%%%%%%%%%%%%%%%% lnot, snot, wnot
_rev(true, false).
_rev(false, true).

_se_domain(operation(lnot, (Expr1, ())), val(bool, Val)) :-
    _expression(compile2, operation(lnot, (Expr1, ()))),
    _se_domain(Expr1, val(bool, NegVal)),
    _rev(NegVal, Val).

_se_domain(operation(snot, (Expr1, ())), val(bool, Val)) :-
    _expression(compile2, operation(snot, (Expr1, ()))),
    _se_domain(Expr1, val(bool, NegVal)),
    _rev(NegVal, Val).

_se_domain(operation(wnot, (Expr1, ())), val(bool, Val)) :-
    _expression(compile2, operation(wnot, (Expr1, ()))),
    _se_domain(Expr1, val(bool, NegVal)),
    _rev(NegVal, Val).

_se_domain(operation(lnot, (Expr1, ())), val(none, none)) :-
    _expression(compile2, operation(lnot, (Expr1, ()))),
    _se_domain(Expr1, val(none, none)).

_se_domain(operation(snot, (Expr1, ())), val(bool, false)) :-
    _expression(compile2, operation(snot, (Expr1, ()))),
    _se_domain(Expr1, val(none, none)).

_se_domain(operation(wnot, (Expr1, ())), val(bool, true)) :-
    _expression(compile2, operation(wnot, (Expr1, ()))),
    _se_domain(Expr1, val(none, none)).

%%%%%%%%%%%%%%%%% conj disj limp

% conj
_se_domain(operation(conj, ExprList), val(bool, false)) :-
    _expression(compile2, operation(conj, ExprList)),
    _expression_operationIndex(compile2, operation(conj, ExprList), _, Arg),
    _se_domain(Arg, val(bool, false)).

_se_domain(operation(conj, ExprList), val(bool, true)) :-
    _expression(compile2, operation(conj, ExprList)),
    _se_domain(Arg, val(bool, true)) : _expression_operationIndex(compile2, operation(conj, ExprList), _, Arg).

_se_domain(operation(conj, ExprList), bad) :-
    _expression(compile2, operation(conj, ExprList)),
    _expression_operationIndex(compile2, operation(conj, ExprList), _, Special),
    _se_domain(Special, bad),
    #false : _se_domain(Arg, val(bool, false)), _expression_operationIndex(compile2, operation(conj, ExprList), _, Arg).

% disj
_se_domain(operation(disj, ExprList), val(bool, true)) :-
    _expression(compile2, operation(disj, ExprList)),
    _expression_operationIndex(compile2, operation(disj, ExprList), _, Arg),
    _se_domain(Arg, val(bool, true)).

_se_domain(operation(disj, ExprList), val(bool, false)) :-
    _expression(compile2, operation(disj, ExprList)),
    _se_domain(Arg, val(bool, false)) : _expression_operationIndex(compile2, operation(disj, ExprList), _, Arg).

_se_domain(operation(disj, ExprList), bad) :-
    _expression(compile2, operation(disj, ExprList)),
    _expression_operationIndex(compile2, operation(disj, ExprList), _, Special),
    _se_domain(Special, bad),
    #false : _se_domain(Arg, val(bool, true)), _expression_operationIndex(compile2, operation(disj, ExprList), _, Arg).

% limp % implication
_se_domain(operation(limp, (Expr1, (Expr2, ()))), val(bool, true)) :-
    _expression(compile2, operation(limp, (Expr1, (Expr2, ())))),
    _se_domain(Expr1, val(bool, false)).

_se_domain(operation(limp, (Expr1, (Expr2, ()))), val(bool, true)) :-
    _expression(compile2, operation(limp, (Expr1, (Expr2, ())))),
    _se_domain(Expr2, val(bool, true)).

_se_domain(operation(limp, (Expr1, (Expr2, ()))), val(bool, false)) :-
    _expression(compile2, operation(limp, (Expr1, (Expr2, ())))),
    _se_domain(Expr1, val(bool, true)),
    _se_domain(Expr2, val(bool, false)).

_se_domain(operation(limp, (Expr1, (Expr2, ()))), val(none, none)) :-
    _expression(compile2, operation(limp, (Expr1, (Expr2, ())))),
    _se_domain(Expr1, val(bool, true)),
    _se_domain(Expr2, val(none, none)).

_se_domain(operation(limp, (Expr1, (Expr2, ()))), val(none, none)) :-
    _expression(compile2, operation(limp, (Expr1, (Expr2, ())))),
    _se_domain(Expr1, val(none, none)),
    _se_domain(Expr2, val(bool, false)).

_se_domain(operation(limp, (Expr1, (Expr2, ()))), val(none, none)) :-
    _expression(compile2, operation(limp, (Expr1, (Expr2, ())))),
    _se_domain(Expr1, val(none, none)),
    _se_domain(Expr2, val(none, none)).

_se_domain(operation(limp, (Expr1, (Expr2, ()))), bad) :-
    _expression(compile2, operation(limp, (Expr1, (Expr2, ())))),
    _se_domain(Expr1, val(bool, true)),
    _se_domain(Expr2, bad).

_se_domain(operation(limp, (Expr1, (Expr2, ()))), bad) :-
    _expression(compile2, operation(limp, (Expr1, (Expr2, ())))),
    _se_domain(Expr1, bad),
    not _se_domain(Expr2, val(bool, true)).


%%%%%%%%%%%%%%%%% lxor leqv
% this implementation of lxor and leqv is not very efficient,
% can be much better if we have a binary xor
_bool_has_bad(ExprList) :-
    _expression(compile2, operation((lxor;leqv), ExprList)),
    _expression_operationIndex(compile2, operation((lxor;leqv), ExprList), _, Arg),
    _se_domain(Arg, bad).

_se_domain(operation(lxor, ExprList),(val(bool,true);val(bool,false))) :- 
    not _bool_has_bad(ExprList), _expression(compile2, operation(lxor, ExprList)).
_se_domain(operation(leqv, ExprList),(val(bool,true);val(bool,false))) :- 
    not _bool_has_bad(ExprList), _expression(compile2, operation(leqv, ExprList)).

%%%%%%%%%%%%%%%%%% ite
_se_domain(operation(ite,(E1,(E2,(E3,())))), Value) :-
    _expression(compile2, operation(ite,(E1,(E2,(E3,()))))),
    _se_domain(E1, val(bool, true)),
    _se_domain(E2, Value).

_se_domain(operation(ite,(E1,(E2,(E3,())))), Value) :-
    _expression(compile2, operation(ite,(E1,(E2,(E3,()))))),
    _se_domain(E1, val(bool, false)),
    _se_domain(E3, Value).

%%% Abdallah: not python compatible?
_se_domain(operation(ite,(E1,(E2,(E3,())))), val(none, none)) :-
    _expression(compile2, operation(ite,(E1,(E2,(E3,()))))),
    _se_domain(E1, val(none, none)).

_se_domain(operation(ite,(E1,(E2,(E3,())))), bad) :-
    _expression(compile2, operation(ite,(E1,(E2,(E3,()))))),
    _se_domain(E1, bad).

%%%%%%%%%%%%%%%%%%% if
_se_domain(operation(if,(E1,(E2,()))), Value) :-
    _expression(compile2, operation(if,(E1,(E2,())))),
    _se_domain(E1, val(bool, true)),
    _se_domain(E2, Value).

_se_domain(operation(if,(E1,(E2,()))), val(none, none)) :-
    _expression(compile2, operation(if,(E1,(E2,())))),
    _se_domain(E1, val(bool, false)).

_se_domain(operation(if,(E1,(E2,()))), val(none, none)) :-
    _expression(compile2, operation(if,(E1,(E2,())))),
    _se_domain(E1, val(none, none)).

_se_domain(operation(if,(E1,(E2,()))), bad) :-
    _expression(compile2, operation(if,(E1,(E2,())))),
    _se_domain(E1, bad).

%%%%%%%%%%%%%%%%%% default
_se_domain(operation(default,(E1,E2)), Value) :-
    _expression(compile2, operation(default,(E1,E2))),
    _se_domain(E1, Value),
    Value != val(none, none).

_se_domain(operation(default,(E1,(E2,()))), Value) :-
    _expression(compile2, operation(default,(E1,(E2,())))),
    _se_domain(E1, val(none, none)),
    _se_domain(E2, Value).

%%%%%%%%%%%%%%%%%% hasValue
_se_domain(operation(hasValue,(E1,())), val(bool, true)) :-
    _expression(compile2, operation(hasValue,(E1,()))),
    not _se_domain(E1, val(none, none)),
    not _se_domain(E1, bad).

_se_domain(operation(hasValue,(E1,())), val(bool, false)) :-
    _expression(compile2, operation(hasValue,(E1,()))),
    _se_domain(E1, val(none, none)).

%%% Abdallah: should bad input become bad output? --> see bad.lp
%_se_domain(operation(hasValue,(E1,())), bad) :-
%    _expression(compile2, operation(hasValue,(E1,()))),
%    _se_domain(E1, bad).

%%%%%%%%% copied _se_domain rules shifted to body with _se_value
:-
    not _se_value(operation(lnot, (Expr1, ())), val(bool, Val)),
    _expression(compile2, operation(lnot, (Expr1, ()))),
    _se_value(Expr1, val(bool, NegVal)),
    _rev(NegVal, Val).

:-
    not _se_value(operation(snot, (Expr1, ())), val(bool, Val)),
    _expression(compile2, operation(snot, (Expr1, ()))),
    _se_value(Expr1, val(bool, NegVal)),
    _rev(NegVal, Val).

:-
    not _se_value(operation(wnot, (Expr1, ())), val(bool, Val)),
    _expression(compile2, operation(wnot, (Expr1, ()))),
    _se_value(Expr1, val(bool, NegVal)),
    _rev(NegVal, Val).

:-
    not _se_value(operation(lnot, (Expr1, ())), val(none, none)),
    _expression(compile2, operation(lnot, (Expr1, ()))),
    _se_value(Expr1, val(none, none)).

:-
    not _se_value(operation(snot, (Expr1, ())), val(bool, false)),
    _expression(compile2, operation(snot, (Expr1, ()))),
    _se_value(Expr1, val(none, none)).

:-
    not _se_value(operation(wnot, (Expr1, ())), val(bool, true)),
    _expression(compile2, operation(wnot, (Expr1, ()))),
    _se_value(Expr1, val(none, none)).

:-
    not _se_value(operation(conj, ExprList), val(bool, false)),
    _expression(compile2, operation(conj, ExprList)),
    _expression_operationIndex(compile2, operation(conj, ExprList), _, Arg),
    _se_value(Arg, val(bool, false)).

:-
    not _se_value(operation(conj, ExprList), val(bool, true)),
    _expression(compile2, operation(conj, ExprList)),
    _se_value(Arg, val(bool, true)) : _expression_operationIndex(compile2, operation(conj, ExprList), _, Arg).

:-
    not _se_value(operation(conj, ExprList), bad),
    _expression(compile2, operation(conj, ExprList)),
    _expression_operationIndex(compile2, operation(conj, ExprList), _, Special),
    _se_value(Special, bad),
    #false : _se_value(Arg, val(bool, false)), _expression_operationIndex(compile2, operation(conj, ExprList), _, Arg).

:-
    not _se_value(operation(disj, ExprList), val(bool, true)),
    _expression(compile2, operation(disj, ExprList)),
    _expression_operationIndex(compile2, operation(disj, ExprList), _, Arg),
    _se_value(Arg, val(bool, true)).

:-
    not _se_value(operation(disj, ExprList), val(bool, false)),
    _expression(compile2, operation(disj, ExprList)),
    _se_value(Arg, val(bool, false)) : _expression_operationIndex(compile2, operation(disj, ExprList), _, Arg).

:-
    not _se_value(operation(disj, ExprList), bad),
    _expression(compile2, operation(disj, ExprList)),
    _expression_operationIndex(compile2, operation(disj, ExprList), _, Special),
    _se_value(Special, bad),
    #false : _se_value(Arg, val(bool, true)), _expression_operationIndex(compile2, operation(disj, ExprList), _, Arg).

:-
    not _se_value(operation(limp, (Expr1, (Expr2, ()))), val(bool, true)),
    _expression(compile2, operation(limp, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(bool, false)).

:-
    not _se_value(operation(limp, (Expr1, (Expr2, ()))), val(bool, true)),
    _expression(compile2, operation(limp, (Expr1, (Expr2, ())))),
    _se_value(Expr2, val(bool, true)).

:-
    not _se_value(operation(limp, (Expr1, (Expr2, ()))), val(bool, false)),
    _expression(compile2, operation(limp, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(bool, true)),
    _se_value(Expr2, val(bool, false)).

:-
    not _se_value(operation(limp, (Expr1, (Expr2, ()))), val(none, none)),
    _expression(compile2, operation(limp, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(bool, true)),
    _se_value(Expr2, val(none, none)).

:-
    not _se_value(operation(limp, (Expr1, (Expr2, ()))), val(none, none)),
    _expression(compile2, operation(limp, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(none, none)),
    _se_value(Expr2, val(bool, false)).

:-
    not _se_value(operation(limp, (Expr1, (Expr2, ()))), val(none, none)),
    _expression(compile2, operation(limp, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(none, none)),
    _se_value(Expr2, val(none, none)).

:-
    not _se_value(operation(limp, (Expr1, (Expr2, ()))), bad),
    _expression(compile2, operation(limp, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(bool, true)),
    _se_value(Expr2, bad).

:-
    not _se_value(operation(limp, (Expr1, (Expr2, ()))), bad),
    _expression(compile2, operation(limp, (Expr1, (Expr2, ())))),
    _se_value(Expr1, bad),
    not _se_value(Expr2, val(bool, true)).

:-
    not _se_value(operation(lxor, ExprList),val(bool,true)),
    _expression(compile2,operation(lxor, ExprList)),
    not _bool_has_bad(ExprList),
    N = #count { Idx : _se_value(Arg, val(bool,true)), _expression_operationIndex(compile2, operation(lxor, ExprList), Idx, Arg) }, N \ 2 = 1.

:-
    not _se_value(operation(lxor, ExprList),val(bool,false)),
    _expression(compile2,operation(lxor, ExprList)),
    not _bool_has_bad(ExprList),
    N = #count { Idx : _se_value(Arg, val(bool,true)), _expression_operationIndex(compile2, operation(lxor, ExprList), Idx, Arg) }, N \ 2 = 0.

:-
    not _se_value(operation(leqv, ExprList),val(bool,true)),
    _expression(compile2,operation(leqv, ExprList)),
    not _bool_has_bad(ExprList),
    N = #count { Idx : _se_value(Arg, val(bool,false)), _expression_operationIndex(compile2, operation(leqv, ExprList), Idx, Arg) }, N \ 2 = 0.

:-
    not _se_value(operation(leqv, ExprList),val(bool,false)),
    _expression(compile2,operation(leqv, ExprList)),
    not _bool_has_bad(ExprList),
    N = #count { Idx : _se_value(Arg, val(bool,false)), _expression_operationIndex(compile2, operation(leqv, ExprList), Idx, Arg) }, N \ 2 = 1.

:-
    not _se_value(operation(ite,(E1,(E2,(E3,())))), Value),
    _expression(compile2, operation(ite,(E1,(E2,(E3,()))))),
    _se_value(E1, val(bool, true)),
    _se_value(E2, Value).

:-
    not _se_value(operation(ite,(E1,(E2,(E3,())))), Value),
    _expression(compile2, operation(ite,(E1,(E2,(E3,()))))),
    _se_value(E1, val(bool, false)),
    _se_value(E3, Value).

:-
    not _se_value(operation(ite,(E1,(E2,(E3,())))), val(none, none)),
    _expression(compile2, operation(ite,(E1,(E2,(E3,()))))),
    _se_value(E1, val(none, none)).

:-
    not _se_value(operation(ite,(E1,(E2,(E3,())))), bad),
    _expression(compile2, operation(ite,(E1,(E2,(E3,()))))),
    _se_value(E1, bad).

:-
    not _se_value(operation(if,(E1,(E2,()))), Value),
    _expression(compile2, operation(if,(E1,(E2,())))),
    _se_value(E1, val(bool, true)),
    _se_value(E2, Value).

:-
    not _se_value(operation(if,(E1,(E2,()))), val(none, none)),
    _expression(compile2, operation(if,(E1,(E2,())))),
    _se_value(E1, val(bool, false)).

:-
    not _se_value(operation(if,(E1,(E2,()))), val(none, none)),
    _expression(compile2, operation(if,(E1,(E2,())))),
    _se_value(E1, val(none, none)).

:-
    not _se_value(operation(if,(E1,(E2,()))), bad),
    _expression(compile2, operation(if,(E1,(E2,())))),
    _se_value(E1, bad).

:-
    not _se_value(operation(default,(E1,E2)), Value),
    _expression(compile2, operation(default,(E1,E2))),
    _se_value(E1, Value),
    Value != val(none, none).

:-
    not _se_value(operation(default,(E1,(E2,()))), Value),
    _expression(compile2, operation(default,(E1,(E2,())))),
    _se_value(E1, val(none, none)),
    _se_value(E2, Value).

:-
    not _se_value(operation(hasValue,(E1,())), val(bool, true)),
    _expression(compile2, operation(hasValue,(E1,()))),
    not _se_value(E1, val(none, none)),
    not _se_value(E1, bad).

:-
    not _se_value(operation(hasValue,(E1,())), val(bool, false)),
    _expression(compile2, operation(hasValue,(E1,()))),
    _se_value(E1, val(none, none)).

