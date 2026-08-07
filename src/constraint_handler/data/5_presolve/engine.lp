#defined engine_default/1.
#defined engine_request/2.

%%%%%%%%%%%%%%%%% engines
_engine_supportOptimization(compile;compile2;ground;propagator).
_engine(compile;compile2;ground;propagator;none).

_engine_default(ENG) :- engine_default(ENG), _engine(ENG).
_engine_defaultProvided :- engine_default(ENG), _engine(ENG).
_engine_default(compile) :- not _engine_defaultProvided.

_label(LBL) :- _label(LBL,DECL).
_engine_userRequest(LBL) :- engine_request(LBL,ENG), _engine(ENG).
_engine(LBL,ENG) :- engine_request(LBL,ENG), _engine(ENG).
_engine(LBL,ENG) :- _engine_default(ENG), not _engine_userRequest(LBL), _label(LBL).

%%%%%%%%%%%%%%%%% collect labels
_label(LBL,DECL) :- _passed(solve,LBL,DECL).
