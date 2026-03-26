%%%%%%%%%%%%%%%%% conditional_hasValue/1 conditional_hasNoValue/1
conditional_hasValue(E) :- _se_value(E,V), V != val(none,none), V !=bad.
conditional_hasNoValue(E) :- direct_query(E), _se_value(E,val(none,none)).
%1 { conditional_hasNoValue(E); conditional_hasValue(E) } 1 :- _se_value(E,bad).

%%%%%%%%%%%%%%%%% eq neq
operator_declare((eq;neq),(T1,(T2,())),bool) :- _type(T1), _type(T2), (T1;T2)=none.
_computedIdx(E,val(bool,true)) :- _computeIdx(E,eq),
	_computeIdx(E,0,val(none,_)),
	_computeIdx(E,1,val(none,_)).

_computedIdx(E,val(bool,false)) :- _computeIdx(E,eq),
	_computeIdx(E,0,val(T1,_)),
	_computeIdx(E,1,val(T2,_)),
	(T1;T2)=none, (T1;T2)!=none.

_computedIdx(E,val(bool,false)) :- _computeIdx(E,neq),
	_computeIdx(E,0,val(none,_)),
	_computeIdx(E,1,val(none,_)).

_computedIdx(E,val(bool,true)) :- _computeIdx(E,neq),
	_computeIdx(E,0,val(T1,_)),
	_computeIdx(E,1,val(T2,_)),
	(T1;T2)=none, (T1;T2)!=none.

%%%%%%%%%%%%%%%%% ite
operator_declare(ite,(bool,(T,(T,()))),T) :- _type(T).
_direct_lazy(ite).
direct_query(E1) :- direct_query(operation(ite,(E1,(E2,(E3,()))))).
direct_query(E2) :- direct_query(operation(ite,(E1,(E2,(E3,()))))), _se_value(E1,val(bool,true)).
direct_query(E3) :- direct_query(operation(ite,(E1,(E2,(E3,()))))), _se_value(E1,val(bool,false)).

_se_value(operation(ite,(E1,(E2,(E3,())))),val(none,none)) :- direct_query(operation(ite,(E1,(E2,(E3,()))))), _se_value(E1,val(none,none)).
_se_value(operation(ite,(E1,(E2,(E3,())))),V2) :- direct_query(operation(ite,(E1,(E2,(E3,()))))), _se_value(E1,val(bool,true)), _se_value(E2,V2).
_se_value(operation(ite,(E1,(E2,(E3,())))),V3) :- direct_query(operation(ite,(E1,(E2,(E3,()))))), _se_value(E1,val(bool,false)), _se_value(E3,V3).

%%%%%%%%%%%%%%%%% if
_se_value(operation(if,(E1,(E2,()))),V2) :- direct_query(operation(if,(E1,(E2,())))), _se_value(E1,val(bool,true)), _se_value(E2,V2).
_se_value(operation(if,(E1,(E2,()))),val(none,none)) :- direct_query(operation(if,(E1,(E2,())))), _se_value(E1,val(bool,false)).
_se_value(operation(if,(E1,(E2,()))),val(none,none)) :- direct_query(operation(if,(E1,(E2,())))), _se_value(E1,val(none,none)).

%%%%%%%%%%%%%%%%% default
_se_value(operation(default,(E1,TL)),V) :- direct_query(operation(default,(E1,TL))), _se_value(E1,V), V!=val(none,none).
_se_value(operation(default,(E1,(E2,()))),V) :- direct_query(operation(default,(E1,(E2,())))), _se_value(E1,val(none,none)), _se_value(E2,V).

%%%%%%%%%%%%%%%%% hasValue
operator_declare(hasValue,(T,()),bool) :- _type(T).
_se_value(operation(hasValue,(E1,())),val(bool,true))  :- direct_query(operation(hasValue,(E1,()))), conditional_hasValue(E1).
_se_value(operation(hasValue,(E1,())),val(bool,false)) :- direct_query(operation(hasValue,(E1,()))), _se_value(E1,val(none,none)).
