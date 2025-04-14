eValue(E,bool,true)   :- expression(E), E=operation(eq,  (E1,(E2,()))), eValue(E1,bool,B1), eValue(E2,bool,B2), B1 =  B2.
eValue(E,bool,false)  :- expression(E), E=operation(eq,  (E1,(E2,()))), eValue(E1,bool,B1), eValue(E2,bool,B2), B1 != B2.
eValue(E,bool,true)   :- expression(E), E=operation(neq, (E1,(E2,()))), eValue(E1,bool,B1), eValue(E2,bool,B2), B1 != B2.
eValue(E,bool,false)  :- expression(E), E=operation(neq, (E1,(E2,()))), eValue(E1,bool,B1), eValue(E2,bool,B2), B1 =  B2.

eValue(E,bool,true)  :- expression(E), E=operation(disj,L), eValue(E1,bool,true),   E1=@pythonListElements(L).
eValue(E,bool,false) :- expression(E), E=operation(disj,L), eValue(E1,bool,false) : E1=@pythonListElements(L).

eValue(E,bool,true)  :- expression(E), E=operation(conj,L), eValue(E1,bool,true) : E1=@pythonListElements(L).
eValue(E,bool,false) :- expression(E), E=operation(conj,L), eValue(E1,bool,false), E1=@pythonListElements(L).

eValue(E,bool,true)  :- expression(E), E=operation(limp, (E1,(E2,()))), eValue(E1,bool,false).
eValue(E,bool,true)  :- expression(E), E=operation(limp, (E1,(E2,()))), eValue(E2,bool,true).
eValue(E,bool,false) :- expression(E), E=operation(limp, (E1,(E2,()))), eValue(E1,bool,true), eValue(E2,bool,false).

eValue(E,bool,true)  :- expression(E), E=operation(lnot,L), L = (E1,()), eValue(E1,bool,false).
eValue(E,bool,false) :- expression(E), E=operation(lnot,L), L = (E1,()), eValue(E1,bool,true).

eValue(E,bool,true)  :- expression(E), E=operation(lxor,L), N = #count { I1 : eValue(E1,bool,true), (I1,E1)=@pythonEnumerateElements(L) }, N \ 2 = 1, #false : not eValue(E1,bool,true), not eValue(E1,bool,false), E1=@pythonListElements(L).
eValue(E,bool,false) :- expression(E), E=operation(lxor,L), N = #count { I1 : eValue(E1,bool,true), (I1,E1)=@pythonEnumerateElements(L) }, N \ 2 = 0, #false : not eValue(E1,bool,true), not eValue(E1,bool,false), E1=@pythonListElements(L).

eValue(E,bool,true)  :- expression(E), E=operation(leqv,L), N = #count { I1 : eValue(E1,bool,false), (I1,E1)=@pythonEnumerateElements(L) }, N \ 2 = 0, #false : not eValue(E1,bool,true), not eValue(E1,bool,false), E1=@pythonListElements(L).
eValue(E,bool,false) :- expression(E), E=operation(leqv,L), N = #count { I1 : eValue(E1,bool,false), (I1,E1)=@pythonEnumerateElements(L) }, N \ 2 = 1, #false : not eValue(E1,bool,true), not eValue(E1,bool,false), E1=@pythonListElements(L).
