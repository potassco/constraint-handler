eValue(E,bool,true)   :- expression(E), E=operation(eq,  (E1,(E2,()))), eValue(E1,bool,B1), eValue(E2,bool,B2), B1 =  B2.
eValue(E,bool,false)  :- expression(E), E=operation(eq,  (E1,(E2,()))), eValue(E1,bool,B1), eValue(E2,bool,B2), B1 != B2.
eValue(E,bool,true)   :- expression(E), E=operation(neq, (E1,(E2,()))), eValue(E1,bool,B1), eValue(E2,bool,B2), B1 != B2.
eValue(E,bool,false)  :- expression(E), E=operation(neq, (E1,(E2,()))), eValue(E1,bool,B1), eValue(E2,bool,B2), B1 =  B2.

eValue(E,bool,true)  :- expression(E), E=operation(disj,L), eValue(E1,bool,true),   E1=@pythonEnumerateElements(L).
eValue(E,bool,false) :- expression(E), E=operation(disj,L), eValue(E1,bool,false) : E1=@pythonEnumerateElements(L).

eValue(E,bool,true)  :- expression(E), E=operation(conj,L), eValue(E1,bool,true) : E1=@pythonEnumerateElements(L).
eValue(E,bool,false) :- expression(E), E=operation(conj,L), eValue(E1,bool,false), E1=@pythonEnumerateElements(L).

eValue(E,bool,true)  :- expression(E), E=operation(limp, (E1,(E2,()))), eValue(E1,bool,false).
eValue(E,bool,true)  :- expression(E), E=operation(limp, (E1,(E2,()))), eValue(E2,bool,true).
eValue(E,bool,false) :- expression(E), E=operation(limp, (E1,(E2,()))), eValue(E1,bool,true), eValue(E2,bool,false).
