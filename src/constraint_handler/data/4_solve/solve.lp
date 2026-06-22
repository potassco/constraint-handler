_passed(correction(dummy,rem),dummy,dummy).

_label(LBL,DECL) :- _passed(correction(REASON,add),LBL,DECL).

_solve_removed(LBL,DECL) :- _passed(correction(REASON,rem),LBL,DECL).
_passed(presolve,LBL,DECL) :- _passed(sugar,LBL,DECL), not _solve_removed(LBL,DECL).
_passed(presolve,LBL,DECL) :- _passed(correction(REASON,add),LBL,DECL).

_variable_involve(presolve,LBL,X,DECL) :- _passed(presolve,LBL,DECL), DECL=variable_declare(X,D).
_variable_involve(presolve,LBL,X,DECL) :- _passed(presolve,LBL,DECL), DECL=variable_define(X,D).
_variable_involve(presolve,LBL,X,DECL) :- _passed(presolve,LBL,DECL), DECL=variable_domain(X,D).
_variable_involve(presolve,LBL,X,DECL) :- _passed(presolve,LBL,DECL), DECL=set_assign(X,D).
_variable_involve(presolve,LBL,X,DECL) :- _passed(presolve,LBL,DECL), DECL=set_baseDomain(X,D).
_variable_involve(presolve,LBL,X,DECL) :- _passed(presolve,LBL,DECL), DECL=multimap_assign(X,D,E).

_solve_conflictVariable(X) :- _variable_exists(sugar,X),
  1 < #count { LBL0,DECL : _passed(presolve,LBL0,DECL),
               DECL=(variable_define(X,E);variable_declare(X,(fromFacts;set;multimap))) }.

_passed(solve,LBL,DECL) :- _passed(presolve,LBL,DECL), #false : _variable_involve(presolve,LBL,X,DECL), _solve_conflictVariable(X).

_solve_firstLabel(X,LBL) :-_solve_conflictVariable(X), _variable_involve(presolve,LBL,X,DECL), 0 = #count { LBL2 : _variable_involve(presolve,LBL2,X,DECL2), LBL2 < LBL }.
_passed(solve,LBL,variable_declare(X,definition)) :- _solve_firstLabel(X,LBL).
_passed(solve,LBL,variable_define(X,bad)) :- _solve_firstLabel(X,LBL).

:- _passed(solve,L1,variable_define(X,E1)), _passed(solve,L2,variable_define(X,E2)), (L1,E1)!=(L2,E2).


_passed(compile,LBL,DECL) :- _phase_active(solve), _passed(solve,LBL,DECL), _label(LBL,DECL), engine(LBL,compile), #false: DECL=warning_forbid(KIND); #false: DECL=warning_ignore(KIND).
_passed(compile2,LBL,DECL) :- _phase_active(solve), _passed(solve,LBL,DECL), _label(LBL,DECL), engine(LBL,compile2), #false: DECL=warning_forbid(KIND); #false: DECL=warning_ignore(KIND).
_passed(ground,LBL,DECL) :- _phase_active(solve), _passed(solve,LBL,DECL), _label(LBL,DECL), engine(LBL,ground), #false: DECL=warning_forbid(KIND); #false: DECL=warning_ignore(KIND).
_passed(propagator,LBL,DECL) :- _phase_active(solve), _passed(solve,LBL,DECL), _label(LBL,DECL), engine(LBL,propagator), #false: DECL=warning_forbid(KIND); #false: DECL=warning_ignore(KIND).

_passed((compile;compile2;ground;propagator;none),LBL,warning_forbid(W)) :- _passed(solve,LBL,warning_forbid(W)).
_passed((compile;compile2;ground;propagator;none),LBL,warning_ignore(W)) :- _passed(solve,LBL,warning_ignore(W)).

_optimize_component(LBL,E,PREC,ID,PRIO) :- _phase_active(solve), _passed(solve,LBL,optimize_component(E,PREC,ID,PRIO)), engine(LBL,ENG), _engine_supportOptimization(ENG).
