ch_solve(share_value(E),LBL) :- _phase_active(solve), ch_core(evaluate(REF,E),LBL).
ch_post(evaluate(REF,E),LBL) :- ch_core(evaluate(REF,E),LBL), _engine_grounding(LBL).
propagator_evaluate(REF,E,LBL) :- ch_core(evaluate(REF,E),LBL), _engine_propagator(LBL).
