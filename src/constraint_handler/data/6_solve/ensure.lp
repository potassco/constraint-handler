_passed(solve,LBL,share_value(E)) :- _phase_active(solve), ch_core(ensure(E),LBL).
_passed(solve,LBL,bool_evaluate(E)) :- _phase_active(solve), ch_core(ensure(E),LBL).
:- _phase_active(solve), ch_core(ensure(E),LBL), not bool_evaluated(E,val(bool,true)), not bool_evaluated(E,bad).
