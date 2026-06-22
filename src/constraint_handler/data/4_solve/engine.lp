%%%%%%%%%%%%%%%%% engines
_engine_supportOptimization(compile;compile2;ground;propagator).
_main_engine(compile;compile2;ground;propagator;none).

_main_defaultEngine(ENG) :- defaultEngine(ENG), _main_engine(ENG).
_main_defaultEngineProvided :- defaultEngine(ENG), _main_engine(ENG).
_main_defaultEngine(compile) :- not _main_defaultEngineProvided.

_label(LBL) :- _label(LBL,DECL).
_main_requestedEngine(LBL) :- requestEngine(LBL,ENG), _main_engine(ENG).
engine(LBL,ENG) :- requestEngine(LBL,ENG), _main_engine(ENG).
engine(LBL,ENG) :- _main_defaultEngine(ENG), not _main_requestedEngine(LBL), _label(LBL).
engine(_internal,compile).

%%%%%%%%%%%%%%%%% collect labels
_label(LBL,DECL) :- _passed(solve,LBL,DECL).
