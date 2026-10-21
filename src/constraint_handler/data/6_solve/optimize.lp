ch_solve(share_value(E;O;P;C),LBL) :- _phase_active(solve), ch_core(optimize_component(E,O,P,ID,PRIORITY,C),LBL).

propagator_optimize_maximizeSum(operation(ite,(C,(E,(val(int,0),())))),ID,PRIO,LBL) :- _phase_active(solve), ch_core(optimize_component(E,ORIG,PREC,ID,PRIO,C),LBL), _engine_propagator(LBL).

_optimize_component(E,ORIG,PREC,ID,PRIORITY,C,LBL) :- _phase_active(solve), ch_core(optimize_component(E,ORIG,PREC,ID,PRIORITY,C),LBL).

#maximize { I@PRIORITY,ID : ch_core(optimize_component(E,ORIG,PREC,ID,PRIORITY,C),LBL), _shared_value(E,val(int,I)), _shared_value(C,val(bool,true)) }.
