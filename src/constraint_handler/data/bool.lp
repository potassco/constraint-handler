%*! compute(OP,ARGS)

Interface for boolean computations.

Args:
    - OP: The operator used in the computation.
    - ARGS: The arguments passed to the computation in list form.
*%


%# Equality and Inequality
computed(OP,ARGS,val(bool,true))  :- compute(OP,ARGS), OP=eq,  ARGS = (val(bool,V1),(val(bool,V2),())), V1 =  V2.
computed(OP,ARGS,val(bool,false)) :- compute(OP,ARGS), OP=eq,  ARGS = (val(bool,V1),(val(bool,V2),())), V1 != V2.
computed(OP,ARGS,val(bool,true))  :- compute(OP,ARGS), OP=neq, ARGS = (val(bool,V1),(val(bool,V2),())), V1 != V2.
computed(OP,ARGS,val(bool,false)) :- compute(OP,ARGS), OP=neq, ARGS = (val(bool,V1),(val(bool,V2),())), V1 =  V2.

%%%%%%%%%%%%%%%%% lnot, snot, wnot
computed(NEG,ARGS,val(bool,true))  :- compute(NEG,ARGS), NEG=(lnot;snot;wnot), ARGS=(val(bool,false),()).
computed(NEG,ARGS,val(bool,false)) :- compute(NEG,ARGS), NEG=(lnot;snot;wnot), ARGS=(val(bool,true),()).
%% logical/classical negation
computed(lnot,ARGS,val(none,none))  :- compute(lnot,ARGS), ARGS=(val(none,none),()).
%% strong negation / strict negation
eValue(E,bool,false)  :- direct_query(E), E=operation(snot,(E1,())), conditional_hasNoValue(E1).
%% weak negation / negation as weak failure
eValue(E,bool,true)  :- direct_query(E), E=operation(wnot,(E1,())), conditional_hasNoValue(E1).

%%%%%%%%%%%%%%%%% conj disj limp
%% The compute/computed interface is given below the eValue interface
%% We use the eValue interface because it allows short-circuit evaluation

%computedIdx(E,bool,true)  :- computeIdx(E,conj), E=operation(conj,L), eValue(E1,bool,true) : E1=@pythonListElements(L).
computedIdx(E,val(bool,false)) :- computeIdx(E,conj), computeIdx(E,IDX,val(bool,false)).
computedIdx(E,val(bool,true))  :- computeIdx(E,conj), computeIdx(E,IDX,val(bool,true)) : computeIdx(E,IDX,V).

%eValue(E,bool,true)  :- direct_query(E), E=operation(conj,L), eValue(E1,bool,true) : E1=@pythonListElements(L).
%eValue(E,bool,false) :- direct_query(E), E=operation(conj,L), eValue(E1,bool,false), E1=@pythonListElements(L).

eValue(E,bool,true)  :- direct_query(E), E=operation(disj,L), eValue(E1,bool,true),  E1=@pythonListElements(L).
eValue(E,bool,false) :- direct_query(E), E=operation(disj,L), eValue(E1,bool,false): E1=@pythonListElements(L).

%eValue(E,bool,true)  :- direct_query(E), E=operation(limp, (E1,(E2,()))), eValue(E1,bool,false).
%eValue(E,bool,true)  :- direct_query(E), E=operation(limp, (E1,(E2,()))), eValue(E2,bool,true).
%eValue(E,bool,false) :- direct_query(E), E=operation(limp, (E1,(E2,()))), eValue(E1,bool,true), eValue(E2,bool,false).
computed(OP,ARGS,val(bool,true))  :- compute(OP,ARGS), OP=limp,  ARGS = (val(bool,false),(val(T2,V2),())).
computed(OP,ARGS,val(bool,true))  :- compute(OP,ARGS), OP=limp,  ARGS = (val(T1,V1),(val(bool,true),())).
computed(OP,ARGS,val(bool,false)) :- compute(OP,ARGS), OP=limp,  ARGS = (val(bool,true),(val(bool,false),())).

computed(OP,ARGS,val(none,none)) :- compute(OP,ARGS), OP=limp,  ARGS = (val(bool,true),(val(none,none),())).
computed(OP,ARGS,val(none,none)) :- compute(OP,ARGS), OP=limp,  ARGS = (val(none,none),(val(bool,false),())).
computed(OP,ARGS,val(none,none)) :- compute(OP,ARGS), OP=limp,  ARGS = (val(none,none),(val(none,none),())).

%%%%%%%%%%%%%%%%% lxor leqv

computed(lxor,ARGS,val(bool,true))  :- compute(lxor,ARGS),
    N = #count { I : (I,val(bool,true))=@pythonEnumerateElements(ARGS) }, N \ 2 = 1.
computed(lxor,ARGS,val(bool,false)) :- compute(lxor,ARGS),
    N = #count { I : (I,val(bool,true))=@pythonEnumerateElements(ARGS) }, N \ 2 = 0.

computed(leqv,ARGS,val(bool,true))  :- compute(leqv,ARGS),
    N = #count { I : (I,val(bool,true))=@pythonEnumerateElements(ARGS) }, N \ 2 = 0.
computed(leqv,ARGS,val(bool,false)) :- compute(leqv,ARGS),
    N = #count { I : (I,val(bool,true))=@pythonEnumerateElements(ARGS) }, N \ 2 = 1.
