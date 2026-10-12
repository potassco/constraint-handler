%%%%%%%%%%%%%%%%% engines
_engine(compile;compile2;ground;propagator;none).

_engine_default(ENG) :- ch_core(engine_request(ENG),_label_anonymous).
_engine_defaultProvided :- ch_core(engine_request(ENG),_label_anonymous).
_engine_default(compile) :- not _engine_defaultProvided.

_label(LBL) :- ch_core(DECL,LBL).
_engine_userRequest(LBL) :- ch_core(engine_request(ENG),LBL).
_engine(ENG,LBL) :- ch_core(engine_request(ENG),LBL).
_engine(ENG,LBL) :- _engine_default(ENG), not _engine_userRequest(LBL), _label(LBL).

_engine_grounding(LBL) :- _engine((compile;compile2;ground),LBL).
_engine_propagator(LBL) :- _engine(propagator,LBL).
