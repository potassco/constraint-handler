_passed(solve,LBL,share_value(E)) :- _phase_active(solve), ch_core(evaluate(REF,E),LBL).
_evaluate(REF,E) :- ch_core(evaluate(REF,E),LBL), _engine(ENG,LBL), _engine_grounding(ENG).

evaluated(REF,V) :- _evaluate(REF,E), _shared_value(E,V).
evaluated(REF,bad) :- _evaluate(REF,E), #false: _shared_value(E,V).

_evaluate(REF,E) :- ch_core(evaluate(REF,E),LBL), _engine(ENG,LBL), _engine_grounding(ENG).

_passed(solve,LBL,DECL) :- _phase_active(solve), ch_core(DECL,LBL), DECL=evaluate(REF,E).
