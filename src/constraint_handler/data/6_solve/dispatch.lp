_passed(compile,LBL,DECL) :- ch_solve(DECL,LBL), _engine(compile,LBL).
_passed(compile2,LBL,DECL) :- ch_solve(DECL,LBL), _engine(compile2,LBL).
_passed(ground,LBL,DECL) :- ch_solve(DECL,LBL), _engine(ground,LBL).
_passed(propagator,LBL,DECL) :- ch_solve(DECL,LBL), _engine(propagator,LBL).
