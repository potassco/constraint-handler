%%%%%%%%%%%%%%%%% conditional_hasValue/1 conditional_hasNoValue/1
conditional_hasValue(E) :- _se_value(E,V), V != val(none,none).
conditional_hasNoValue(E) :- direct_query(E), _se_value(E,val(none,none)).

%%%%%%%%%%%%%%%%% eq neq
computed(OP,ARGS,val(bool,true))  :- compute(OP,ARGS), OP=eq,  ARGS = (val(none,V1),(val(none,V2),())).
computed(OP,ARGS,val(bool,false)) :- compute(OP,ARGS), OP=eq,  ARGS = (val(T1,V1),(val(T2,V2),())), (T1;T2) = none, (T1;T2) != none.
computed(OP,ARGS,val(bool,false)) :- compute(OP,ARGS), OP=neq, ARGS = (val(none,V1),(val(none,V2),())).
computed(OP,ARGS,val(bool,true))  :- compute(OP,ARGS), OP=neq, ARGS = (val(T1,V1),(val(T2,V2),())), (T1;T2) = none, (T1;T2) != none.

%%%%%%%%%%%%%%%%% ite
_direct_lazy(ite).
direct_query(E1) :- direct_query(E), E=operation(ite,(E1,(E2,(E3,())))).
direct_query(E2) :- direct_query(E), E=operation(ite,(E1,(E2,(E3,())))), _se_value(E1,val(bool,true)).
direct_query(E3) :- direct_query(E), E=operation(ite,(E1,(E2,(E3,())))), _se_value(E1,val(bool,false)).

_se_value(E,val(none,none)) :- direct_query(E), E=operation(ite,(E1,(E2,(E3,())))), _se_value(E1,val(none,none)).
_se_value(E,V2) :- direct_query(E), E=operation(ite,(E1,(E2,(E3,())))), _se_value(E1,val(bool,true)), _se_value(E2,V2).
_se_value(E,V3) :- direct_query(E), E=operation(ite,(E1,(E2,(E3,())))), _se_value(E1,val(bool,false)), _se_value(E3,V3).

%%%%%%%%%%%%%%%%% if
_se_value(E,V2) :- direct_query(E), E=operation(if,(E1,(E2,()))), _se_value(E1,val(bool,true)), _se_value(E2,V2).
_se_value(E,val(none,none)) :- direct_query(E), E=operation(if,(E1,(E2,()))), _se_value(E1,val(bool,false)).
_se_value(E,val(none,none)) :- direct_query(E), E=operation(if,(E1,(E2,()))), _se_value(E1,val(none,none)).

%%%%%%%%%%%%%%%%% default
_se_value(E,V) :- direct_query(E), E=operation(default,(E1,TL)), _se_value(E1,V), V != val(none,none).
_se_value(E,V) :- direct_query(E), E=operation(default,(E1,(E2,()))), _se_value(E1,val(none,none)), _se_value(E2,V).

%%%%%%%%%%%%%%%%% hasValue
_se_value(E,val(bool,true))  :- direct_query(E), E=operation(hasValue,(E1,())), conditional_hasValue(E1).
_se_value(E,val(bool,false)) :- direct_query(E), E=operation(hasValue,(E1,())), _se_value(E1,val(none,none)).
