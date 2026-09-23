:- _passed(ENG,LBL,ensure(E)), not _shared_value(E,val(bool,true)), not _shared_value(E,bad), _engine_grounding(ENG).
_passed(solve,LBL,ensure(E)) :- _phase_active(solve), ch_core(ensure(E),LBL).
_passed(solve,LBL,share_value(E)) :- _phase_active(solve), ch_core(ensure(E),LBL).
propagator_ensure(EXPR,LBL) :- ch_core(ensure(EXPR),LBL), _engine(propagator,LBL).

%_passed(solve,LBL,share_value(E)) :- _phase_active(solve), ch_core(ensure(E),LBL).
%_passed(solve,LBL,bool_evaluate(E)) :- _phase_active(solve), ch_core(ensure(E),LBL).
%:- _phase_active(solve), ch_core(ensure(E),LBL), not bool_evaluated(E,val(bool,true)), not bool_evaluated(E,bad).
