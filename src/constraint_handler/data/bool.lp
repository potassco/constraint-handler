%%%%%%%%%%%%%%%%% lnot, snot, wnot
operator_declare(OP,(T,()),T) :- T = bool, OP = (lnot;snot;wnot).
_computedIdx(E,val(bool,true))  :- _computeIdx(E, NEG), NEG=(lnot;snot;wnot), _computeIdx(E, 0, val(bool, false)).
_computedIdx(E,val(bool,false)) :- _computeIdx(E, NEG), NEG=(lnot;snot;wnot), _computeIdx(E, 0, val(bool, true)).

%% logical/classical negation
operator_declare(OP,(T,()),T) :- T = none, OP = (lnot).
_computedIdx(E,val(none,none)) :- _computeIdx(E, lnot), _computeIdx(E, 0, val(none, none)).

%% strong negation / strict negation
operator_declare(OP,(T1,()),T2) :- T1 = bool,T2 = none, OP = (snot;wnot).
_se_value(operation(snot,(E1,())),val(bool,false))  :- direct_query(operation(snot,(E1,()))), conditional_hasNoValue(E1).

%% weak negation / negation as weak failure
_se_value(operation(wnot,(E1,())),val(bool,true))  :- direct_query(operation(wnot,(E1,()))), conditional_hasNoValue(E1).

%%%%%%%%%%%%%%%%% conj disj limp
%% The _compute/_computed interface is given below the eValue interface
%% We use the eValue interface because it allows short-circuit evaluation
operator_declare_variadic(OP,T,T,1) :- T = bool, OP = (conj;disj).
%_computedIdx(E,bool,true)  :- _computeIdx(E,conj), E=operation(conj,L), _se_value(E1,val(bool,true)) : E1=@pythonListElements(L).
_computedIdx(E,val(bool,false)) :- _computeIdx(E,conj), _computeIdx(E,IDX,val(bool,false)).
_computedIdx(E,val(bool,true))  :- _computeIdx(E,conj), _computeIdx(E,IDX,val(bool,true)) : _computeIdx(E,IDX,V).

%_se_value(E,val(bool,true))  :- direct_query(E), E=operation(conj,L), _se_value(E1,val(bool,true)) : E1=@pythonListElements(L).
%_se_value(E,val(bool,false)) :- direct_query(E), E=operation(conj,L), _se_value(E1,val(bool,false)), E1=@pythonListElements(L).

_computedIdx(E,val(bool,true)) :- _computeIdx(E, disj), _computeIdx(E, _, val(bool, true)).
_computedIdx(E,val(bool,false)) :- _computeIdx(E, disj), _computeIdx(E, IDX, val(bool, false)) : _computeIdx(E, IDX, V).

_computedIdx(E,val(bool,true)) :- _computeIdx(E, limp), _computeIdx(E, 0, val(bool, false)).
_computedIdx(E,val(bool,true)) :- _computeIdx(E, limp), _computeIdx(E, 1, val(bool, true)).
_computedIdx(E,val(bool,false)) :- _computeIdx(E, limp), _computeIdx(E, 0, val(bool, true)), _computeIdx(E, 1, val(bool, false)).

_computedIdx(E,val(none,none)) :- _computeIdx(E, limp), _computeIdx(E, 0, val(bool, true)), _computeIdx(E, 1, val(none, none)).
_computedIdx(E,val(none,none)) :- _computeIdx(E, limp), _computeIdx(E, 0, val(none, none)), _computeIdx(E, 1, val(bool, false)).
_computedIdx(E,val(none,none)) :- _computeIdx(E, limp), _computeIdx(E, 0, val(none, none)), _computeIdx(E, 1, val(none, none)).

%%%%%%%%%%%%%%%%% lxor leqv
operator_declare_variadic(OP,T,T,1) :- T = bool, OP = (lxor;leqv).
_computedIdx(E,val(bool,true)) :- _computeIdx(E, lxor),
    N = #count { IDX : _computeIdx(E, IDX, val(bool, true)) }, N \ 2 = 1.
_computedIdx(E,val(bool,false)) :- _computeIdx(E, lxor),
    N = #count { IDX : _computeIdx(E, IDX, val(bool, true)) }, N \ 2 = 0.

_computedIdx(E,val(bool,true)) :- _computeIdx(E, leqv),
    N = #count { IDX : _computeIdx(E, IDX, val(bool, false)) }, N \ 2 = 0.
_computedIdx(E,val(bool,false)) :- _computeIdx(E, leqv),
    N = #count { IDX : _computeIdx(E, IDX, val(bool, false)) }, N \ 2 = 1.
