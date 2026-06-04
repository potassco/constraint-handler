_passed(correction(dummy,rem),dummy).

_label(LBL,DECL) :- _passed(correction(REASON,add),LBL,DECL).

_solve_removed(DECL) :- _passed(correction(REASON,rem),DECL).
_passed(presolve,DECL) :- _passed(sugar,DECL), not _solve_removed(DECL).
_passed(presolve,DECL) :- _passed(correction(REASON,add),LBL,DECL).

_variable_involve(presolve,LBL,X,DECL) :- _passed(presolve,DECL), DECL=variable_declare(LBL,X,D).
_variable_involve(presolve,LBL,X,DECL) :- _passed(presolve,DECL), DECL=variable_define(LBL,X,D).
_variable_involve(presolve,LBL,X,DECL) :- _passed(presolve,DECL), DECL=variable_domain(LBL,X,D).
_variable_involve(presolve,LBL,X,DECL) :- _passed(presolve,DECL), DECL=set_assign(LBL,X,D).
_variable_involve(presolve,LBL,X,DECL) :- _passed(presolve,DECL), DECL=set_baseDomain(LBL,X,D).
_variable_involve(presolve,LBL,X,DECL) :- _passed(presolve,DECL), DECL=multimap_assign(LBL,X,D,E).

_solve_conflictVariable(X) :- _variable_exists(sugar,X),
  1 < #count { DECL : _passed(presolve,DECL),
               DECL=(variable_define(LBL,X,E);variable_declare(LBL,X,(fromFacts;set;multimap))) }.

_passed(solve,DECL) :- _passed(presolve,DECL), #false : _variable_involve(presolve,LBL,X,DECL), _solve_conflictVariable(X).

_solve_firstLabel(X,LBL) :-_solve_conflictVariable(X), _variable_involve(presolve,LBL,X,DECL), 0 = #count { LBL2 : _variable_involve(presolve,LBL2,X,DECL2), LBL2 < LBL }.
_passed(solve,variable_declare(LBL,X,definition)) :- _solve_firstLabel(X,LBL).
_passed(solve,variable_define(LBL,X,bad)) :- _solve_firstLabel(X,LBL).

:- _passed(solve,variable_define(L1,X,E1)), _passed(solve,variable_define(L2,X,E2)), (L1,E1)!=(L2,E2).


_passed(compile,DECL) :- _phase_active(solve), _passed(solve,DECL), _label(LBL,DECL), engine(LBL,compile), #false: DECL=warning_forbid(LBL,KIND); #false: DECL=warning_ignore(LBL,KIND).
_passed(ground,DECL) :- _phase_active(solve), _passed(solve,DECL), _label(LBL,DECL), engine(LBL,ground), #false: DECL=warning_forbid(LBL,KIND); #false: DECL=warning_ignore(LBL,KIND).
_passed(propagator,DECL) :- _phase_active(solve), _passed(solve,DECL), _label(LBL,DECL), engine(LBL,propagator), #false: DECL=warning_forbid(LBL,KIND); #false: DECL=warning_ignore(LBL,KIND).

_passed((compile;ground;propagator;none),warning_forbid(LBL,W)) :- _passed(solve,warning_forbid(LBL,W)).
_passed((compile;ground;propagator;none),warning_ignore(LBL,W)) :- _passed(solve,warning_ignore(LBL,W)).
