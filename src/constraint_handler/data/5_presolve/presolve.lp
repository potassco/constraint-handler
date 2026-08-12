_passed(presolve,LBL,DECL) :- _passed(sugar,LBL,DECL), #false : _passed(correction(REASON,rem),LBL,DECL).
_passed(presolve,LBL,DECL) :- _passed(correction(REASON,add),LBL,DECL).

_variable_involve(presolve,LBL,X,DECL) :- _passed(presolve,LBL,DECL), DECL=variable_declare(X,D).
_variable_involve(presolve,LBL,X,DECL) :- _passed(presolve,LBL,DECL), DECL=variable_define(X,D).
_variable_involve(presolve,LBL,X,DECL) :- _passed(presolve,LBL,DECL), DECL=variable_domain(X,D).
_variable_involve(presolve,LBL,X,DECL) :- _passed(presolve,LBL,DECL), DECL=variable_default(X,V,COND).
_variable_involve(presolve,LBL,X,DECL) :- _passed(presolve,LBL,DECL), DECL=set_assign(X,D).
_variable_involve(presolve,LBL,X,DECL) :- _passed(presolve,LBL,DECL), DECL=set_baseDomain(X,D).
_variable_involve(presolve,LBL,X,DECL) :- _passed(presolve,LBL,DECL), DECL=multimap_assign(X,D,E).

_solve_conflictVariable(X) :- _variable(sugar,X),
  1 < #count { LBL0,DECL : _passed(presolve,LBL0,DECL),
               DECL=(variable_define(X,E);variable_declare(X,(fromFacts;set;multimap))) }.

_passed(solve,LBL,DECL) :- _phase_active(solve), _passed(presolve,LBL,DECL), #false : _variable_involve(presolve,LBL,X,DECL), _solve_conflictVariable(X).

_solve_firstLabel(X,LBL) :-_solve_conflictVariable(X), _variable_involve(presolve,LBL,X,DECL), 0 = #count { LBL2 : _variable_involve(presolve,LBL2,X,DECL2), LBL2 < LBL }.
_passed(solve,LBL,variable_declare(X,definition)) :- _phase_active(solve), _solve_firstLabel(X,LBL).
_passed(solve,LBL,variable_define(X,bad)) :- _phase_active(solve), _solve_firstLabel(X,LBL).
