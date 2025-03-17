value(E,T2,V2) :- expression(E), E=operation(ite, (E1,(E2,(E3,())))), value(E1,bool,true), value(E2,T2,V2).
value(E,T3,V3) :- expression(E), E=operation(ite, (E1,(E2,(E3,())))), value(E1,bool,false), value(E3,T3,V3).

value(E,T2,V2) :- expression(E), E=operation(if,  (E1,(E2,()))), value(E1,bool,true), value(E2,T2,V2).
value(E,T,V)   :- expression(E), E=operation(phi, (E1,TL)), value(E1,T,V).
value(E,T,V)   :- expression(E), E=operation(phi, (E1,(E2,()))), not value(E1,_,_), value(E2,T,V).
