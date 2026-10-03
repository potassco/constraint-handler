_passed(skip,bla) :- _never.
_passed(compile,LBL,DECL) :- ch_solve(DECL,LBL), _label(DECL,LBL), _engine(compile,LBL), not _passed(skip,DECL).
_passed(compile2,LBL,DECL) :- ch_solve(DECL,LBL), _label(DECL,LBL), _engine(compile2,LBL), not _passed(skip,DECL).
_passed(ground,LBL,DECL) :- ch_solve(DECL,LBL), _label(DECL,LBL), _engine(ground,LBL), not _passed(skip,DECL).
_passed(propagator,LBL,DECL) :- ch_solve(DECL,LBL), _label(DECL,LBL), _engine(propagator,LBL), not _passed(skip,DECL).
