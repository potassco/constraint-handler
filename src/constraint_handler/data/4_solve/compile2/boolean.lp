%%%%%%%%%%%%%%%%% eq neq
_se_value(operation(eq, (Expr1, (Expr2, ()))), val(bool, true)):-
   _expression(compile, operation(eq, (Expr1, (Expr2, ())))),
   _se_value(Expr1, val(bool, V)),
   _se_value(Expr2, val(bool, V)).

_se_value(operation(eq, (Expr1, (Expr2, ()))), val(bool, false)):-
   _expression(compile, operation(eq, (Expr1, (Expr2, ())))),
   _se_value(Expr1, val(bool, V)),
   not _se_value(Expr2, val(bool, V)),
   not _se_value(Expr2, bad).

_se_value(operation(eq, (Expr1, (Expr2, ()))), val(bool, false)):-
   _expression(compile, operation(eq, (Expr1, (Expr2, ())))),
   _se_value(Expr2, val(bool, V)),
   not _se_value(Expr1, val(bool, V)),
   not _se_value(Expr1, bad).

_se_value(operation(neq, (Expr1, (Expr2, ()))), val(bool, true)):-
   _expression(compile, operation(neq, (Expr1, (Expr2, ())))),
   _se_value(Expr1, val(bool, V)),
   not _se_value(Expr2, val(bool, V)),
   not _se_value(Expr2, bad).

_se_value(operation(neq, (Expr1, (Expr2, ()))), val(bool, true)):-
   _expression(compile, operation(neq, (Expr1, (Expr2, ())))),
   _se_value(Expr2, val(bool, V)),
   not _se_value(Expr1, val(bool, V)),
   not _se_value(Expr1, bad).

_se_value(operation(neq, (Expr1, (Expr2, ()))), val(bool, false)):-
   _expression(compile, operation(neq, (Expr1, (Expr2, ())))),
   _se_value(Expr1, val(bool, V)),
   _se_value(Expr2, val(bool, V)).

%%%%%%%%%%%%%%%%% lnot, snot, wnot
_rev(true, false).
_rev(false, true).

_se_value(operation(lnot, (Expr1, ())), val(bool, Val)) :-
    _expression(compile, operation(lnot, (Expr1, ()))),
    _se_value(Expr1, val(bool, NegVal)),
    _rev(NegVal, Val).

_se_value(operation(snot, (Expr1, ())), val(bool, Val)) :-
    _expression(compile, operation(snot, (Expr1, ()))),
    _se_value(Expr1, val(bool, NegVal)),
    _rev(NegVal, Val).

_se_value(operation(wnot, (Expr1, ())), val(bool, Val)) :-
    _expression(compile, operation(wnot, (Expr1, ()))),
    _se_value(Expr1, val(bool, NegVal)),
    _rev(NegVal, Val).

_se_value(operation(lnot, (Expr1, ())), val(none, none)) :-
    _expression(compile, operation(lnot, (Expr1, ()))),
    _se_value(Expr1, val(none, none)).

_se_value(operation(snot, (Expr1, ())), val(bool, false)) :-
    _expression(compile, operation(snot, (Expr1, ()))),
    _se_value(Expr1, val(none, none)).

_se_value(operation(wnot, (Expr1, ())), val(bool, true)) :-
    _expression(compile, operation(wnot, (Expr1, ()))),
    _se_value(Expr1, val(none, none)).

%%%%%%%%%%%%%%%%% conj disj limp

% conj
_se_value(operation(conj, ExprList), val(bool, false)) :-
    _expression(compile, operation(conj, ExprList)),
    Arg = @pythonListElements(ExprList),
    _se_value(Arg, val(bool, false)).

_se_value(operation(conj, ExprList), val(bool, true)) :-
    _expression(compile, operation(conj, ExprList)),
    _se_value(Arg, val(bool, true)) : Arg = @pythonListElements(ExprList).

_se_value(operation(conj, ExprList), bad) :-
    _expression(compile, operation(conj, ExprList)),
    Special = @pythonListElements(ExprList),
    _se_value(Special, bad),
    #false : _se_value(Arg, val(bool, false)), Arg = @pythonListElements(ExprList).

% disj
_se_value(operation(disj, ExprList), val(bool, true)) :-
    _expression(compile, operation(disj, ExprList)),
    Arg = @pythonListElements(ExprList),
    _se_value(Arg, val(bool, true)).

_se_value(operation(disj, ExprList), val(bool, false)) :-
    _expression(compile, operation(disj, ExprList)),
    _se_value(Arg, val(bool, false)) : Arg = @pythonListElements(ExprList).

_se_value(operation(disj, ExprList), bad) :-
    _expression(compile, operation(disj, ExprList)),
    Special = @pythonListElements(ExprList),
    _se_value(Special, bad),
    #false : _se_value(Arg, val(bool, true)), Arg = @pythonListElements(ExprList).

% limp % implication
_se_value(operation(limp, (Expr1, (Expr2, ()))), val(bool, true)) :-
    _expression(compile, operation(limp, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(bool, false)).

_se_value(operation(limp, (Expr1, (Expr2, ()))), val(bool, true)) :-
    _expression(compile, operation(limp, (Expr1, (Expr2, ())))),
    _se_value(Expr2, val(bool, true)).

_se_value(operation(limp, (Expr1, (Expr2, ()))), val(bool, false)) :-
    _expression(compile, operation(limp, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(bool, true)),
    _se_value(Expr2, val(bool, false)).

_se_value(operation(limp, (Expr1, (Expr2, ()))), val(none, none)) :-
    _expression(compile, operation(limp, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(bool, true)),
    _se_value(Expr2, val(none, none)).

_se_value(operation(limp, (Expr1, (Expr2, ()))), val(none, none)) :-
    _expression(compile, operation(limp, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(none, none)),
    _se_value(Expr2, val(bool, false)).

_se_value(operation(limp, (Expr1, (Expr2, ()))), val(none, none)) :-
    _expression(compile, operation(limp, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(none, none)),
    _se_value(Expr2, val(none, none)).

_se_value(operation(limp, (Expr1, (Expr2, ()))), bad) :-
    _expression(compile, operation(limp, (Expr1, (Expr2, ())))),
    _se_value(Expr1, val(bool, true)),
    _se_value(Expr2, bad).

_se_value(operation(limp, (Expr1, (Expr2, ()))), bad) :-
    _expression(compile, operation(limp, (Expr1, (Expr2, ()))),
    _se_value(Expr1, bad)),
    not _se_value(Expr2, val(bool, true)).


%%%%%%%%%%%%%%%%% lxor leqv
% this implementation of lxor and leqv is not very efficient,
% can be much better if we have a binary xor
_bool_has_bad(ExprList) :-
    _expression(compile, operation((lxor;leqv), ExprList)),
    Arg = @pythonListElements(ExprList),
    _se_value(Arg, bad).

_se_value(operation(lxor, ExprList),val(bool,true)) :-
    _expression(compile,operation(lxor, ExprList)),
    not _bool_has_bad(ExprList),
    N = #count { Idx : _se_value(Arg, val(bool,true)), (Idx, Arg) = @pythonEnumerateElements(ExprList) }, N \ 2 = 1.
_se_value(operation(lxor, ExprList),val(bool,false)) :- _expression(compile,operation(lxor, ExprList)),
    not _bool_has_bad(ExprList),
    N = #count { Idx : _se_value(Arg, val(bool,true)), (Idx, Arg) = @pythonEnumerateElements(ExprList) }, N \ 2 = 0.

_se_value(operation(leqv, ExprList),val(bool,true)) :- _expression(compile,operation(leqv, ExprList)),
    not _bool_has_bad(ExprList),
    N = #count { Idx : _se_value(Arg, val(bool,false)), (Idx, Arg) = @pythonEnumerateElements(ExprList) }, N \ 2 = 0.
_se_value(operation(leqv, ExprList),val(bool,false)) :- _expression(compile,operation(leqv, ExprList)),
    not _bool_has_bad(ExprList),
    N = #count { Idx : _se_value(Arg, val(bool,false)), (Idx, Arg) = @pythonEnumerateElements(ExprList) }, N \ 2 = 1.

%%%%%%%%%%%%%%%%%% ite
_se_value(operation(ite,(E1,(E2,(E3,())))), Value) :-
    _expression(compile, operation(ite,(E1,(E2,(E3,()))))),
    _se_value(E1, val(bool, true)),
    _se_value(E2, Value).

_se_value(operation(ite,(E1,(E2,(E3,())))), Value) :-
    _expression(compile, operation(ite,(E1,(E2,(E3,()))))),
    _se_value(E1, val(bool, false)),
    _se_value(E3, Value).

%%% Abdallah: not python compatible?
_se_value(operation(ite,(E1,(E2,(E3,())))), val(none, none)) :-
    _expression(compile, operation(ite,(E1,(E2,(E3,()))))),
    _se_value(E1, val(none, none)).

_se_value(operation(ite,(E1,(E2,(E3,())))), bad) :-
    _expression(compile, operation(ite,(E1,(E2,(E3,()))))),
    _se_value(E1, bad).

%%%%%%%%%%%%%%%%%%% if
_se_value(operation(if,(E1,(E2,()))), Value) :-
    _expression(compile, operation(if,(E1,(E2,())))),
    _se_value(E1, val(bool, true)),
    _se_value(E2, Value).

_se_value(operation(if,(E1,(E2,()))), val(none, none)) :-
    _expression(compile, operation(if,(E1,(E2,())))),
    _se_value(E1, val(bool, false)).

_se_value(operation(if,(E1,(E2,()))), val(none, none)) :-
    _expression(compile, operation(if,(E1,(E2,())))),
    _se_value(E1, val(none, none)).

_se_value(operation(if,(E1,(E2,()))), bad) :-
    _expression(compile, operation(if,(E1,(E2,())))),
    _se_value(E1, bad).

%%%%%%%%%%%%%%%%%% default
_se_value(operation(default,(E1,E2)), Value) :-
    _expression(compile, operation(default,(E1,E2))),
    _se_value(E1, Value),
    Value != val(none, none).

_se_value(operation(default,(E1,(E2,()))), Value) :-
    _expression(compile, operation(default,(E1,(E2,())))),
    _se_value(E1, val(none, none)),
    _se_value(E2, Value).

%%%%%%%%%%%%%%%%%% hasValue
_se_value(operation(hasValue,(E1,())), val(bool, true)) :-
    _expression(compile, operation(hasValue,(E1,()))),
    not _se_value(E1, val(none, none)),
    not _se_value(E1, bad).

_se_value(operation(hasValue,(E1,())), val(bool, false)) :-
    _expression(compile, operation(hasValue,(E1,()))),
    _se_value(E1, val(none, none)).

%%% Abdallah: should bad input become bad output? --> see bad.lp
%_se_value(operation(hasValue,(E1,())), bad) :-
%    _expression(compile, operation(hasValue,(E1,()))),
%    _se_value(E1, bad).
