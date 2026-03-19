%%%%%%%%%%%%%%%%% conditional_hasValue/1 conditional_hasNoValue/1
conditional_hasValue_id(E_ID) :- _se_value(E,V), E_ID=@pythonId(E), V != val(none,none), V !=bad.
conditional_hasNoValue_id(E_ID) :- direct_query(E), E_ID=@pythonId(E), _se_value(E,val(none,none)).
%1 { conditional_hasNoValue_id(E_ID); conditional_hasValue_id(E_ID) } 1 :- _se_value(E,bad), E_ID=@pythonId(E).

%%%%%%%%%%%%%%%%% eq neq
operator_declare(OP,(T1,(T2,())),bool) :- _type(T1), _type(T2), OP = (eq;neq), (T1;T2) = none.
_computedIdx_id(E_ID,val(bool,true)) :- _computeIdx_id(E_ID, eq),
	_computeIdx_id(E_ID, 0, val(none, _)),
	_computeIdx_id(E_ID, 1, val(none, _)).

_computedIdx_id(E_ID,val(bool,false)) :- _computeIdx_id(E_ID, eq),
	_computeIdx_id(E_ID, 0, val(T1, _)),
	_computeIdx_id(E_ID, 1, val(T2, _)),
	(T1;T2) = none, (T1;T2) != none.

_computedIdx_id(E_ID,val(bool,false)) :- _computeIdx_id(E_ID, neq),
	_computeIdx_id(E_ID, 0, val(none, _)),
	_computeIdx_id(E_ID, 1, val(none, _)).

_computedIdx_id(E_ID,val(bool,true)) :- _computeIdx_id(E_ID, neq),
	_computeIdx_id(E_ID, 0, val(T1, _)),
	_computeIdx_id(E_ID, 1, val(T2, _)),
	(T1;T2) = none, (T1;T2) != none.

%%%%%%%%%%%%%%%%% ite
operator_declare(ite,(bool,(T,(T,()))),T) :-  _type(T), OP = ite.
_direct_lazy(ite).
direct_query(E1) :- direct_query(E), E=operation(ite,(E1,(E2,(E3,())))).
direct_query(E2) :- direct_query(E), E=operation(ite,(E1,(E2,(E3,())))), E1_ID=@pythonId(E1), _se_value_id(E1_ID,val(bool,true)).
direct_query(E3) :- direct_query(E), E=operation(ite,(E1,(E2,(E3,())))), E1_ID=@pythonId(E1), _se_value_id(E1_ID,val(bool,false)).

_se_value(E,val(none,none)) :- direct_query(E), E=operation(ite,(E1,(E2,(E3,())))), E1_ID=@pythonId(E1), _se_value_id(E1_ID,val(none,none)).
_se_value(E,V2) :- direct_query(E), E=operation(ite,(E1,(E2,(E3,())))), E1_ID=@pythonId(E1), E2_ID=@pythonId(E2), _se_value_id(E1_ID,val(bool,true)), _se_value_id(E2_ID,V2).
_se_value(E,V3) :- direct_query(E), E=operation(ite,(E1,(E2,(E3,())))), E1_ID=@pythonId(E1), E3_ID=@pythonId(E3), _se_value_id(E1_ID,val(bool,false)), _se_value_id(E3_ID,V3).

%%%%%%%%%%%%%%%%% if
_se_value(E,V2) :- direct_query(E), E=operation(if,(E1,(E2,()))), E1_ID=@pythonId(E1), E2_ID=@pythonId(E2), _se_value_id(E1_ID,val(bool,true)), _se_value_id(E2_ID,V2).
_se_value(E,val(none,none)) :- direct_query(E), E=operation(if,(E1,(E2,()))), E1_ID=@pythonId(E1), _se_value_id(E1_ID,val(bool,false)).
_se_value(E,val(none,none)) :- direct_query(E), E=operation(if,(E1,(E2,()))), E1_ID=@pythonId(E1), _se_value_id(E1_ID,val(none,none)).

%%%%%%%%%%%%%%%%% default
_se_value(E,V) :- direct_query(E), E=operation(default,(E1,TL)), E1_ID=@pythonId(E1), _se_value_id(E1_ID,V), V != val(none,none).
_se_value(E,V) :- direct_query(E), E=operation(default,(E1,(E2,()))), E1_ID=@pythonId(E1), E2_ID=@pythonId(E2), _se_value_id(E1_ID,val(none,none)), _se_value_id(E2_ID,V).

%%%%%%%%%%%%%%%%% hasValue
operator_declare(OP,(T,()),bool) :- _type(T), OP = hasValue.
_se_value(E,val(bool,true))  :- direct_query(E), E=operation(hasValue,(E1,())), E1_ID=@pythonId(E1), conditional_hasValue_id(E1_ID).
_se_value(E,val(bool,false)) :- direct_query(E), E=operation(hasValue,(E1,())), E1_ID=@pythonId(E1), _se_value_id(E1_ID,val(none,none)).
