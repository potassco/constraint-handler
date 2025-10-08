%%%%%%%%%%%%%%%%% eq neq

computed(OP,ARGS,val(bool,true))  :- compute(OP,ARGS), OP=eq,  ARGS = (val(bool,V1),(val(bool,V2),())), V1 =  V2.
computed(OP,ARGS,val(bool,false)) :- compute(OP,ARGS), OP=eq,  ARGS = (val(bool,V1),(val(bool,V2),())), V1 != V2.
computed(OP,ARGS,val(bool,true))  :- compute(OP,ARGS), OP=neq, ARGS = (val(bool,V1),(val(bool,V2),())), V1 != V2.
computed(OP,ARGS,val(bool,false)) :- compute(OP,ARGS), OP=neq, ARGS = (val(bool,V1),(val(bool,V2),())), V1 =  V2.

%%%%%%%%%%%%%%%%% lnot
%% logical negation

computed(lnot,ARGS,val(bool,true))  :- compute(lnot,ARGS), ARGS=(val(bool,V1),()), V1=false.
computed(lnot,ARGS,val(bool,false)) :- compute(lnot,ARGS), ARGS=(val(bool,V1),()), V1=true.

%%%%%%%%%%%%%%%%% dnot
%% default negation

eValue(E,bool,false) :- direct_query(E), E=operation(dnot,(E1,())), eValue(E1,bool,true).
eValue(E,bool,true)  :- direct_query(E), E=operation(dnot,(E1,())), eValue(E1,bool,false).
eValue(E,bool,false) :- direct_query(E), E=operation(dnot,(E1,())), conditional_hasNoValue(E1).

%%%%%%%%%%%%%%%%% conj disj limp
%% The compute/computed interface is given below the eValue interface
%% We use the eValue interface because it allows short-circuit evaluation

eValue(E,bool,true)  :- direct_query(E), E=operation(conj,L), eValue(E1,bool,true) : E1=@pythonListElements(L).
eValue(E,bool,false) :- direct_query(E), E=operation(conj,L), eValue(E1,bool,false), E1=@pythonListElements(L).

eValue(E,bool,true)  :- direct_query(E), E=operation(disj,L), eValue(E1,bool,true),  E1=@pythonListElements(L).
eValue(E,bool,false) :- direct_query(E), E=operation(disj,L), eValue(E1,bool,false): E1=@pythonListElements(L).

eValue(E,bool,true)  :- direct_query(E), E=operation(limp, (E1,(E2,()))), eValue(E1,bool,false).
eValue(E,bool,true)  :- direct_query(E), E=operation(limp, (E1,(E2,()))), eValue(E2,bool,true).
eValue(E,bool,false) :- direct_query(E), E=operation(limp, (E1,(E2,()))), eValue(E1,bool,true), eValue(E2,bool,false).


%%%%%%%%%%%%%%%%% lxor leqv

computed(lxor,ARGS,val(bool,true))  :- compute(lxor,ARGS),
    N = #count { I : (I,val(bool,true))=@pythonEnumerateElements(ARGS) }, N \ 2 = 1.
computed(lxor,ARGS,val(bool,false)) :- compute(lxor,ARGS),
    N = #count { I : (I,val(bool,true))=@pythonEnumerateElements(ARGS) }, N \ 2 = 0.

computed(leqv,ARGS,val(bool,true))  :- compute(leqv,ARGS),
    N = #count { I : (I,val(bool,true))=@pythonEnumerateElements(ARGS) }, N \ 2 = 0.
computed(leqv,ARGS,val(bool,false)) :- compute(leqv,ARGS),
    N = #count { I : (I,val(bool,true))=@pythonEnumerateElements(ARGS) }, N \ 2 = 1.
