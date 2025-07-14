eValue(E,T2,V2) :- expression(E), E=operation(ite, (E1,(E2,(E3,())))), eValue(E1,bool,true), eValue(E2,T2,V2).
eValue(E,T3,V3) :- expression(E), E=operation(ite, (E1,(E2,(E3,())))), eValue(E1,bool,false), eValue(E3,T3,V3).

eValue(E,T2,V2) :- expression(E), E=operation(if,  (E1,(E2,()))), eValue(E1,bool,true), eValue(E2,T2,V2).
eValue(E,T,V)   :- expression(E), E=operation(phi, (E1,TL)), eValue(E1,T,V).
eValue(E,T,V)   :- expression(E), E=operation(phi, (E1,(E2,()))), not conditional_hasValue(E1), eValue(E2,T,V).

conditional_hasValue(E) :- eValue(E,T,V).
