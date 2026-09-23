%%%%%%%%%%%%%%%%% bool_evaluate
propagator_bool_evaluate(E,LBL) :- _bool_evaluate(E,LBL), _engine(propagator,LBL).
1 { _bool_evaluated(E,(bad;val(bool,(true;false)))) } 1 :- _bool_evaluate(E,LBL), _engine(propagator,LBL).
_bool_evaluated(E,V) :- _bool_evaluate(E,LBL), _se_value(E,V), V=(bad;val(bool,(true;false))).

:- bool_evaluated(E,V0), bool_evaluated(E,V1), V0 < V1, V0=(bad;val(bool,(true;false))), V1=(bad;val(bool,(true;false))).

:- bool_evaluated(E,V), V!=bad, V!=val(bool,true), V!=val(bool,false).

_bool_evaluate(E,LBL) :- _phase_active(solve), ch_core(bool_evaluate(E),LBL).
bool_evaluated(E,V) :- ch_core(bool_evaluate(E),LBL), _bool_evaluated(E,V).
