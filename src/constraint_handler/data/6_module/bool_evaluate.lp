%%%%%%%%%%%%%%%%% bool_evaluate
ch_solve(share_value(E),LBL) :- _bool_evaluate(E,LBL), E != val(bool,true).
propagator_bool_evaluate(E,LBL) :- _bool_evaluate(E,LBL), _engine_propagator(LBL), E != val(bool,true).
1 { _bool_evaluated(E,(bad;val(bool,(true;false)))) } 1 :- _bool_evaluate(E,LBL), _engine_propagator(LBL), E != val(bool,true).
_bool_evaluated(E,V) :- _bool_evaluate(E,LBL), _shared_value(E,V), V=(bad;val(bool,(true;false))), E != val(bool,true).
_bool_evaluated(val(bool,true),val(bool,true)).

:- bool_evaluated(E,V0), bool_evaluated(E,V1), V0 < V1, V0=(bad;val(bool,(true;false))), V1=(bad;val(bool,(true;false))).

:- bool_evaluated(E,V), V!=bad, V!=val(bool,true), V!=val(bool,false).

_bool_evaluate(C,LBL) :- _phase_active(solve), ch_core(variable_declare(X,D,C),LBL).
_bool_evaluate(E,LBL) :- _phase_active(solve), ch_core(bool_evaluate(E),LBL).
bool_evaluated(E,V) :- ch_core(bool_evaluate(E),LBL), _bool_evaluated(E,V).
