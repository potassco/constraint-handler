%%%%%%%%%%%%%%%%% conditional_hasValue/1 conditional_hasNoValue/1
conditional_hasValue(E) :- eValue(E,T,V), (T,V) != (none,none).
conditional_hasNoValue(E) :- direct_query(E), not conditional_hasValue(E).

%%%%%%%%%%%%%%%%% eq neq
computed(OP,ARGS,val(bool,true))  :- compute(OP,ARGS), OP=eq,  ARGS = (val(none,V1),(val(none,V2),())).
computed(OP,ARGS,val(bool,false)) :- compute(OP,ARGS), OP=eq,  ARGS = (val(T1,V1),(val(T2,V2),())), (T1;T2) = none, (T1;T2) != none.
computed(OP,ARGS,val(bool,false)) :- compute(OP,ARGS), OP=neq, ARGS = (val(none,V1),(val(none,V2),())).
computed(OP,ARGS,val(bool,true))  :- compute(OP,ARGS), OP=neq, ARGS = (val(T1,V1),(val(T2,V2),())), (T1;T2) = none, (T1;T2) != none.

%%%%%%%%%%%%%%%%% ite
_direct_lazy(ite).
direct_query(E1) :- direct_query(E), E=operation(ite,(E1,(E2,(E3,())))).
direct_query(E2) :- direct_query(E), E=operation(ite,(E1,(E2,(E3,())))), eValue(E1,bool,true).
direct_query(E3) :- direct_query(E), E=operation(ite,(E1,(E2,(E3,())))), eValue(E1,bool,false).

eValue(E,none,none) :- direct_query(E), E=operation(ite,(E1,(E2,(E3,())))), eValue(E1,none,none).
eValue(E,T2,V2) :- direct_query(E), E=operation(ite,(E1,(E2,(E3,())))), eValue(E1,bool,true), eValue(E2,T2,V2).
eValue(E,T3,V3) :- direct_query(E), E=operation(ite,(E1,(E2,(E3,())))), eValue(E1,bool,false), eValue(E3,T3,V3).

%%%%%%%%%%%%%%%%% if
eValue(E,T2,V2) :- direct_query(E), E=operation(if,(E1,(E2,()))), eValue(E1,bool,true), eValue(E2,T2,V2).
eValue(E,none,none) :- direct_query(E), E=operation(if,(E1,(E2,()))), eValue(E1,bool,false).
eValue(E,none,none) :- direct_query(E), E=operation(if,(E1,(E2,()))), eValue(E1,none,none).

%%%%%%%%%%%%%%%%% default
eValue(E,T,V) :- direct_query(E), E=operation(default,(E1,TL)), eValue(E1,T,V), (T,V) != (none,none).
eValue(E,T,V) :- direct_query(E), E=operation(default,(E1,(E2,()))), not conditional_hasValue(E1), eValue(E2,T,V).

%%%%%%%%%%%%%%%%% hasValue
eValue(E,bool,true)  :- direct_query(E), E=operation(hasValue,(E1,())), conditional_hasValue(E1).
eValue(E,bool,false) :- direct_query(E), E=operation(hasValue,(E1,())), conditional_hasNoValue(E1).
