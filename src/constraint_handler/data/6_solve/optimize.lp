_passed(solve,LBL,share_value(E;O;P)) :- _phase_active(solve), ch_core(optimize_component(E,O,P,ID,PRIORITY),LBL).

propagator_optimize_maximizeSum(E,ID,PRIO,LBL) :- _phase_active(solve), ch_core(optimize_component(E,ORIG,PREC,ID,PRIO),LBL), _engine(propagator,LBL).
%propagator_optimize_maximizeSum(E,ID,PRIO,LBL) :- _passed(solve,LBL,optimize_component(E,ORIG,PREC,ID,PRIO)), _engine(propagator,LBL).

_optimize_component(E,ORIG,PREC,ID,PRIORITY,LBL) :- _phase_active(solve), ch_core(optimize_component(E,ORIG,PREC,ID,PRIORITY),LBL), _engine(ENG,LBL), _engine_supportOptimization(ENG).

#maximize { I@PRIORITY,ID : ch_core(optimize_component(E,ORIG,PREC,ID,PRIORITY),LBL), _shared_value(E,val(int,I)) }.
