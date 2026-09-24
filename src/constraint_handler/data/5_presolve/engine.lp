%%%%%%%%%%%%%%%%% engines
_engine_supportOptimization(compile;compile2;ground;propagator).
_engine(compile;compile2;ground;propagator;none).
_engine_grounding(compile;compile2;ground).

_engine_default(ENG) :- ch_core(engine_request(ENG),_label_anonymous).
_engine_defaultProvided :- ch_core(engine_request(ENG),_label_anonymous).
_engine_default(compile) :- not _engine_defaultProvided.

_label(LBL) :- ch_core(DECL,LBL).
_engine_userRequest(LBL) :- ch_core(engine_request(ENG),LBL).
_engine(ENG,LBL) :- ch_core(engine_request(ENG),LBL).
_engine(ENG,LBL) :- _engine_default(ENG), not _engine_userRequest(LBL), _label(LBL).

%%%%%%%%%%%%%%%%% collect labels
_label(DECL,LBL) :- _passed(solve,LBL,DECL).
_label(DECL,LBL) :- ch_core(DECL,LBL).
