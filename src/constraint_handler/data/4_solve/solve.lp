_passed(correction(dummy,rem),dummy).

_solve_corrected(DECL) :- _passed(correction(REASON,rem),DECL).
_passed(solve,DECL) :- _passed(sugar,DECL), not _solve_corrected(DECL).
_passed(solve,NDECL) :- _passed(correction(REASON,add),LBL,NDECL).
_label(LBL,DECL) :- _passed(correction(REASON,add),LBL,DECL).



_passed(compile,DECL) :- _phase_active(solve), _passed(solve,DECL), _label(LBL,DECL), engine(LBL,compile), #false: DECL=warning_forbid(LBL,KIND); #false: DECL=warning_ignore(LBL,KIND).
_passed(ground,DECL) :- _phase_active(solve), _passed(solve,DECL), _label(LBL,DECL), engine(LBL,ground), #false: DECL=warning_forbid(LBL,KIND); #false: DECL=warning_ignore(LBL,KIND).
_passed(propagator,DECL) :- _phase_active(solve), _passed(solve,DECL), _label(LBL,DECL), engine(LBL,propagator), #false: DECL=warning_forbid(LBL,KIND); #false: DECL=warning_ignore(LBL,KIND).

_passed((compile;ground;propagator;none),warning_forbid(LBL,W)) :- _passed(solve,warning_forbid(LBL,W)).
_passed((compile;ground;propagator;none),warning_ignore(LBL,W)) :- _passed(solve,warning_ignore(LBL,W)).
