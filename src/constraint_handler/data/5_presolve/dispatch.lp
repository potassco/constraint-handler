_optimize_component(E,ORIG,PREC,ID,PRIORITY,LBL) :- _passed(solve,LBL,optimize_component(E,ORIG,PREC,ID,PRIORITY)), _engine(ENG,LBL), _engine_supportOptimization(ENG).

_preference_expressionScore(E,K) :- _passed(solve,LBL,preference_holds(E,K)), _engine(ENG,LBL), _engine_grounding(ENG).

_evaluate(REF,E) :- _passed(solve,LBL,evaluate(REF,E)), _engine(ENG,LBL), _engine_grounding(ENG).

_passed(skip,bla) :- _never.
_passed(compile,LBL,DECL) :- _passed(solve,LBL,DECL), _label(DECL,LBL), _engine(compile,LBL), not _passed(skip,DECL).
_passed(compile2,LBL,DECL) :- _passed(solve,LBL,DECL), _label(DECL,LBL), _engine(compile2,LBL), not _passed(skip,DECL).
_passed(ground,LBL,DECL) :- _passed(solve,LBL,DECL), _label(DECL,LBL), _engine(ground,LBL), not _passed(skip,DECL).
_passed(propagator,LBL,DECL) :- _passed(solve,LBL,DECL), _label(DECL,LBL), _engine(propagator,LBL), not _passed(skip,DECL).
