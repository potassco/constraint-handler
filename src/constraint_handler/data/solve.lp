_main(solve).
_passed(solve,DECL) :- _passed(sugar,DECL), not _solve_corrected(DECL).
_solve_corrected(DECL) :- _passed(correction(change,REASON),DECL,NDECL).
_solve_corrected(DECL) :- _passed(correction(rem),DECL).
_passed(solve,NDECL) :- _passed(correction(change,REASON),DECL,NDECL).
_passed(solve,NDECL) :- _passed(correction(add),LBL,NDECL).
_label(LBL,NDECL) :- _label(LBL,DECL), _passed(correction(change,REASON),DECL,NDECL).
_label(LBL,DECL) :- _passed(correction(add),LBL,DECL).

_passed(compile,DECL) :- _main(solve), _passed(solve,DECL), _label(LBL,DECL), engine(LBL,compile), #false: DECL=warning_forbid(LBL,KIND); #false: DECL=warning_ignore(LBL,KIND).
_passed(ground,DECL) :- _main(solve), _passed(solve,DECL), _label(LBL,DECL), engine(LBL,ground), #false: DECL=warning_forbid(LBL,KIND); #false: DECL=warning_ignore(LBL,KIND).
_passed(propagator,DECL) :- _main(solve), _passed(solve,DECL), _label(LBL,DECL), engine(LBL,propagator), #false: DECL=warning_forbid(LBL,KIND); #false: DECL=warning_ignore(LBL,KIND).

_passed(ENGINE,warning_forbid(LBL,W)) :- _main(solve), _passed(solve,warning_forbid(LBL,W)), _main_engine(ENGINE).
_passed(ENGINE,warning_ignore(LBL,W)) :- _main(solve), _passed(solve,warning_ignore(LBL,W)), _main_engine(ENGINE).
