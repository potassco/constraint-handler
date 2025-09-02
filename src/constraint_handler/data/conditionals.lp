_direct_lazy(ite).
direct_query(E1) :- direct_query(E), E=operation(ite, (E1,(E2,(E3,())))).
direct_query(E2) :- direct_query(E), E=operation(ite, (E1,(E2,(E3,())))), eValue(E1,bool,true).
direct_query(E3) :- direct_query(E), E=operation(ite, (E1,(E2,(E3,())))), eValue(E1,bool,false).

eValue(E,T2,V2) :- direct_query(E), E=operation(ite, (E1,(E2,(E3,())))), eValue(E1,bool,true), eValue(E2,T2,V2).
eValue(E,T3,V3) :- direct_query(E), E=operation(ite, (E1,(E2,(E3,())))), eValue(E1,bool,false), eValue(E3,T3,V3).

eValue(E,T2,V2) :- direct_query(E), E=operation(if,  (E1,(E2,()))), eValue(E1,bool,true), eValue(E2,T2,V2).
eValue(E,T,V)   :- direct_query(E), E=operation(phi, (E1,TL)), eValue(E1,T,V).
eValue(E,T,V)   :- direct_query(E), E=operation(phi, (E1,(E2,()))), not conditional_hasValue(E1), eValue(E2,T,V).

conditional_hasValue(E) :- eValue(E,T,V).
conditional_hasNoValue(E) :- direct_query(E), not conditional_hasValue(E).

eValue(E,bool,true) :- direct_query(E), E=operation(hasValue, (E1,())), conditional_hasValue(E1).
eValue(E,bool,false) :- direct_query(E), E=operation(hasValue, (E1,())), conditional_hasNoValue(E1).
