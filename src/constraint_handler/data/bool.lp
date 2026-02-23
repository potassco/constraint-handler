%%%%%%%%%%%%%%%%% eq neq
operator_declare(OP,(T,(T,())),T) :- T = bool, OP = (eq;neq).
computed(OP,ARGS,val(bool,true))  :- compute(OP,ARGS), OP=eq,  ARGS = (val(bool,V1),(val(bool,V2),())), V1 =  V2.
computed(OP,ARGS,val(bool,false)) :- compute(OP,ARGS), OP=eq,  ARGS = (val(bool,V1),(val(bool,V2),())), V1 != V2.
computed(OP,ARGS,val(bool,true))  :- compute(OP,ARGS), OP=neq, ARGS = (val(bool,V1),(val(bool,V2),())), V1 != V2.
computed(OP,ARGS,val(bool,false)) :- compute(OP,ARGS), OP=neq, ARGS = (val(bool,V1),(val(bool,V2),())), V1 =  V2.

%%%%%%%%%%%%%%%%% lnot, snot, wnot
operator_declare(OP,(T,()),T) :- T = bool, OP = (lnot;snot;wnot).
computed(NEG,ARGS,val(bool,true))  :- compute(NEG,ARGS), NEG=(lnot;snot;wnot), ARGS=(val(bool,false),()).
computed(NEG,ARGS,val(bool,false)) :- compute(NEG,ARGS), NEG=(lnot;snot;wnot), ARGS=(val(bool,true),()).

%% logical/classical negation
operator_declare(OP,(T,()),T) :- T = none, OP = (lnot).
computed(lnot,ARGS,val(none,none))  :- compute(lnot,ARGS), ARGS=(val(none,none),()).

%% strong negation / strict negation
operator_declare(OP,(T1,()),T2) :- T1 = bool,T2 = none, OP = (snot;wnot).
_se_value(E,val(bool,false))  :- direct_query(E), E=operation(snot,(E1,())), conditional_hasNoValue(E1).

%% weak negation / negation as weak failure
_se_value(E,val(bool,true))  :- direct_query(E), E=operation(wnot,(E1,())), conditional_hasNoValue(E1).

%%%%%%%%%%%%%%%%% conj disj limp
%% The compute/computed interface is given below the eValue interface
%% We use the eValue interface because it allows short-circuit evaluation
operator_declare_variadic(OP,T,T,1) :- T = bool, OP = (conj;disj).
%computedIdx(E,bool,true)  :- computeIdx(E,conj), E=operation(conj,L), _se_value(E1,val(bool,true)) : E1=@pythonListElements(L).
computedIdx(E,val(bool,false)) :- computeIdx(E,conj), computeIdx(E,IDX,val(bool,false)).
computedIdx(E,val(bool,true))  :- computeIdx(E,conj), computeIdx(E,IDX,val(bool,true)) : computeIdx(E,IDX,V).

%_se_value(E,val(bool,true))  :- direct_query(E), E=operation(conj,L), _se_value(E1,val(bool,true)) : E1=@pythonListElements(L).
%_se_value(E,val(bool,false)) :- direct_query(E), E=operation(conj,L), _se_value(E1,val(bool,false)), E1=@pythonListElements(L).

_se_value(E,val(bool,true))  :- direct_query(E), E=operation(disj,L), _se_value(E1,val(bool,true)),  E1=@pythonListElements(L).
_se_value(E,val(bool,false)) :- direct_query(E), E=operation(disj,L), _se_value(E1,val(bool,false)): E1=@pythonListElements(L).

%_se_value(E,val(bool,true))  :- direct_query(E), E=operation(limp, (E1,(E2,()))), _se_value(E1,val(bool,false)).
%_se_value(E,val(bool,true))  :- direct_query(E), E=operation(limp, (E1,(E2,()))), _se_value(E2,val(bool,true)).
%_se_value(E,val(bool,false)) :- direct_query(E), E=operation(limp, (E1,(E2,()))), _se_value(E1,val(bool,true)), _se_value(E2,val(bool,false)).
computed(OP,ARGS,val(bool,true))  :- compute(OP,ARGS), OP=limp,  ARGS = (val(bool,false),(val(T2,V2),())).
computed(OP,ARGS,val(bool,true))  :- compute(OP,ARGS), OP=limp,  ARGS = (val(T1,V1),(val(bool,true),())).
computed(OP,ARGS,val(bool,false)) :- compute(OP,ARGS), OP=limp,  ARGS = (val(bool,true),(val(bool,false),())).

computed(OP,ARGS,val(none,none)) :- compute(OP,ARGS), OP=limp,  ARGS = (val(bool,true),(val(none,none),())).
computed(OP,ARGS,val(none,none)) :- compute(OP,ARGS), OP=limp,  ARGS = (val(none,none),(val(bool,false),())).
computed(OP,ARGS,val(none,none)) :- compute(OP,ARGS), OP=limp,  ARGS = (val(none,none),(val(none,none),())).

%%%%%%%%%%%%%%%%% lxor leqv
operator_declare_variadic(OP,T,T,1) :- T = bool, OP = (lxor;leqv).
computed(lxor,ARGS,val(bool,true))  :- compute(lxor,ARGS),
    N = #count { I : (I,val(bool,true))=@pythonEnumerateElements(ARGS) }, N \ 2 = 1.
computed(lxor,ARGS,val(bool,false)) :- compute(lxor,ARGS),
    N = #count { I : (I,val(bool,true))=@pythonEnumerateElements(ARGS) }, N \ 2 = 0.

computed(leqv,ARGS,val(bool,true))  :- compute(leqv,ARGS),
    N = #count { I : (I,val(bool,false))=@pythonEnumerateElements(ARGS) }, N \ 2 = 0.
computed(leqv,ARGS,val(bool,false)) :- compute(leqv,ARGS),
    N = #count { I : (I,val(bool,false))=@pythonEnumerateElements(ARGS) }, N \ 2 = 1.
