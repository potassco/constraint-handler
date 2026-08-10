_optimize_component(LBL,E,ORIG,PREC,ID,PRIORITY) :- _passed(solve,LBL,optimize_component(E,ORIG,PREC,ID,PRIORITY)), _engine(LBL,ENG), _engine_supportOptimization(ENG).

_preference_expressionScore(E,K) :- _passed(solve,LBL,preference_holds(E,K)), _engine(LBL,(compile;compile2;ground)).

_evaluate(operation(OP,ARGS)) :- _passed(solve,LBL,evaluate(OP,ARGS)), _engine(LBL,(compile;compile2;ground)).

%_passed(skip,DECL) :- _passed(solve,LBL,DECL), DECL=(warning_forbid(KIND,TGT);warning_ignore(KIND,TGT)).
_passed(compile,LBL,DECL) :- _passed(solve,LBL,DECL), _label(LBL,DECL), _engine(LBL,compile), not _passed(skip,DECL).
_passed(compile2,LBL,DECL) :- _passed(solve,LBL,DECL), _label(LBL,DECL), _engine(LBL,compile2), not _passed(skip,DECL).
_passed(ground,LBL,DECL) :- _passed(solve,LBL,DECL), _label(LBL,DECL), _engine(LBL,ground), not _passed(skip,DECL).
_passed(propagator,LBL,DECL) :- _passed(solve,LBL,DECL), _label(LBL,DECL), _engine(LBL,propagator), not _passed(skip,DECL).
