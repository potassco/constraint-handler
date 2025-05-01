%%%%%%%%%%%%%%%%% eq neq

computed(OP,ARGS,bool,true)  :- compute(OP,ARGS), OP=eq,  ARGS = (bool,(V1,(bool,(V2,())))), V1 =  V2.
computed(OP,ARGS,bool,false) :- compute(OP,ARGS), OP=eq,  ARGS = (bool,(V1,(bool,(V2,())))), V1 != V2.
computed(OP,ARGS,bool,true)  :- compute(OP,ARGS), OP=neq, ARGS = (bool,(V1,(bool,(V2,())))), V1 != V2.
computed(OP,ARGS,bool,false) :- compute(OP,ARGS), OP=neq, ARGS = (bool,(V1,(bool,(V2,())))), V1 =  V2.

%%%%%%%%%%%%%%%%% lnot

computed(lnot,ARGS,bool,true)  :- compute(lnot,ARGS), ARGS=(bool,(V1,())), V1=false.
computed(lnot,ARGS,bool,false) :- compute(lnot,ARGS), ARGS=(bool,(V1,())), V1=true.

%%%%%%%%%%%%%%%%% conj disj limp
%% The compute/computed interface is given below the eValue interface
%% We use the eValue interface because it allows short-circuit evaluation

eValue(E,bool,true)  :- expression(E), E=operation(conj,L), eValue(E1,bool,true) : E1=@pythonListElements(L).
eValue(E,bool,false) :- expression(E), E=operation(conj,L), eValue(E1,bool,false), E1=@pythonListElements(L).

eValue(E,bool,true)  :- expression(E), E=operation(disj,L), eValue(E1,bool,true),  E1=@pythonListElements(L).
eValue(E,bool,false) :- expression(E), E=operation(disj,L), eValue(E1,bool,false): E1=@pythonListElements(L).

eValue(E,bool,true)  :- expression(E), E=operation(limp, (E1,(E2,()))), eValue(E1,bool,false).
eValue(E,bool,true)  :- expression(E), E=operation(limp, (E1,(E2,()))), eValue(E2,bool,true).
eValue(E,bool,false) :- expression(E), E=operation(limp, (E1,(E2,()))), eValue(E1,bool,true), eValue(E2,bool,false).

%computed(conj,ARGS,bool,true)  :- compute(conj,ARGS), V=true : (bool,V)=@pythonListElements(ARGS,2).
%computed(conj,ARGS,bool,false) :- compute(conj,ARGS), V=false, (bool,V)=@pythonListElements(ARGS,2).
%
%computed(disj,ARGS,bool,true)  :- compute(disj,ARGS), V=true,  (bool,V)=@pythonListElements(ARGS,2).
%computed(disj,ARGS,bool,false) :- compute(disj,ARGS), V=false: (bool,V)=@pythonListElements(ARGS,2).
%
%computed(limp,ARGS,bool,true)  :- compute(limp,ARGS), ARGS=(bool,(V1,(bool,(V2,())))), #false : V1!=false, V2!=true.
%computed(limp,ARGS,bool,false) :- compute(limp,ARGS), ARGS=(bool,(V1,(bool,(V2,())))), V1=true, V2=false.

%%%%%%%%%%%%%%%%% lxor leqv

computed(lxor,ARGS,bool,true)  :- compute(lxor,ARGS),
    N = #count { I : (I,(bool,true))=@pythonEnumerateElements(ARGS,2) }, N \ 2 = 1.
computed(lxor,ARGS,bool,false) :- compute(lxor,ARGS),
    N = #count { I : (I,(bool,true))=@pythonEnumerateElements(ARGS,2) }, N \ 2 = 0.

computed(leqv,ARGS,bool,true)  :- compute(leqv,ARGS),
    N = #count { I : (I,(bool,true))=@pythonEnumerateElements(ARGS,2) }, N \ 2 = 0.
computed(leqv,ARGS,bool,false) :- compute(leqv,ARGS),
    N = #count { I : (I,(bool,true))=@pythonEnumerateElements(ARGS,2) }, N \ 2 = 1.
