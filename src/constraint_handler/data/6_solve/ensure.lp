ch_solve(share_value(E),LBL) :- _phase_active(solve), ch_core(ensure(E),LBL).
_bool_evaluate(E,LBL) :- _phase_active(solve), ch_core(ensure(E),LBL).
:- _phase_active(solve), ch_core(ensure(E),LBL), not _bool_evaluated(E,val(bool,true)), not _bool_evaluated(E,bad).
