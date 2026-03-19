%%%%%%%%%%%%%%%%% lnot, snot, wnot
operator_declare(OP,(T,()),T) :- T = bool, OP = (lnot;snot;wnot).
_computedIdx_id(E_ID,val(bool,true))  :- _computeIdx_id(E_ID, NEG), NEG=(lnot;snot;wnot), _computeIdx_id(E_ID, 0, val(bool, false)).
_computedIdx_id(E_ID,val(bool,false)) :- _computeIdx_id(E_ID, NEG), NEG=(lnot;snot;wnot), _computeIdx_id(E_ID, 0, val(bool, true)).

%% logical/classical negation
operator_declare(OP,(T,()),T) :- T = none, OP = (lnot).
_computedIdx_id(E_ID,val(none,none)) :- _computeIdx_id(E_ID, lnot), _computeIdx_id(E_ID, 0, val(none, none)).

%% strong negation / strict negation
operator_declare(OP,(T1,()),T2) :- T1 = bool,T2 = none, OP = (snot;wnot).
_se_value(E,val(bool,false))  :- direct_query(E), E=operation(snot,(E1,())), E1_ID=@pythonId(E1), conditional_hasNoValue_id(E1_ID).

%% weak negation / negation as weak failure
_se_value(E,val(bool,true))  :- direct_query(E), E=operation(wnot,(E1,())), E1_ID=@pythonId(E1), conditional_hasNoValue_id(E1_ID).

%%%%%%%%%%%%%%%%% conj disj limp
%% The _compute/_computed interface is given below the eValue interface
%% We use the eValue interface because it allows short-circuit evaluation
operator_declare_variadic(OP,T,T,1) :- T = bool, OP = (conj;disj).
%_computedIdx(E,bool,true)  :- _computeIdx(E,conj), E=operation(conj,L), _se_value(E1,val(bool,true)) : E1=@pythonListElements(L).
_computedIdx_id(E_ID,val(bool,false)) :- _computeIdx_id(E_ID,conj), _computeIdx_id(E_ID,IDX,val(bool,false)).
_computedIdx_id(E_ID,val(bool,true))  :- _computeIdx_id(E_ID,conj), _computeIdx_id(E_ID,IDX,val(bool,true)) : _computeIdx_id(E_ID,IDX,V).

%_se_value(E,val(bool,true))  :- direct_query(E), E=operation(conj,L), _se_value(E1,val(bool,true)) : E1=@pythonListElements(L).
%_se_value(E,val(bool,false)) :- direct_query(E), E=operation(conj,L), _se_value(E1,val(bool,false)), E1=@pythonListElements(L).

_computedIdx_id(E_ID,val(bool,true)) :- _computeIdx_id(E_ID, disj), _computeIdx_id(E_ID, _, val(bool, true)).
_computedIdx_id(E_ID,val(bool,false)) :- _computeIdx_id(E_ID, disj), _computeIdx_id(E_ID, IDX, val(bool, false)) : _computeIdx_id(E_ID, IDX, V).

_computedIdx_id(E_ID,val(bool,true)) :- _computeIdx_id(E_ID, limp), _computeIdx_id(E_ID, 0, val(bool, false)).
_computedIdx_id(E_ID,val(bool,true)) :- _computeIdx_id(E_ID, limp), _computeIdx_id(E_ID, 1, val(bool, true)).
_computedIdx_id(E_ID,val(bool,false)) :- _computeIdx_id(E_ID, limp), _computeIdx_id(E_ID, 0, val(bool, true)), _computeIdx_id(E_ID, 1, val(bool, false)).

_computedIdx_id(E_ID,val(none,none)) :- _computeIdx_id(E_ID, limp), _computeIdx_id(E_ID, 0, val(bool, true)), _computeIdx_id(E_ID, 1, val(none, none)).
_computedIdx_id(E_ID,val(none,none)) :- _computeIdx_id(E_ID, limp), _computeIdx_id(E_ID, 0, val(none, none)), _computeIdx_id(E_ID, 1, val(bool, false)).
_computedIdx_id(E_ID,val(none,none)) :- _computeIdx_id(E_ID, limp), _computeIdx_id(E_ID, 0, val(none, none)), _computeIdx_id(E_ID, 1, val(none, none)).

%%%%%%%%%%%%%%%%% lxor leqv
operator_declare_variadic(OP,T,T,1) :- T = bool, OP = (lxor;leqv).
_computedIdx_id(E_ID,val(bool,true)) :- _computeIdx_id(E_ID, lxor),
    N = #count { IDX : _computeIdx_id(E_ID, IDX, val(bool, true)) }, N \ 2 = 1.
_computedIdx_id(E_ID,val(bool,false)) :- _computeIdx_id(E_ID, lxor),
    N = #count { IDX : _computeIdx_id(E_ID, IDX, val(bool, true)) }, N \ 2 = 0.

_computedIdx_id(E_ID,val(bool,true)) :- _computeIdx_id(E_ID, leqv),
    N = #count { IDX : _computeIdx_id(E_ID, IDX, val(bool, false)) }, N \ 2 = 0.
_computedIdx_id(E_ID,val(bool,false)) :- _computeIdx_id(E_ID, leqv),
    N = #count { IDX : _computeIdx_id(E_ID, IDX, val(bool, false)) }, N \ 2 = 1.
