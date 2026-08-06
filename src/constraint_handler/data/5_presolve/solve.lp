_label(LBL,DECL) :- _passed(correction(REASON,add),LBL,DECL).

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

_passed(solve,LBL,DECL) :- _passed(presolve,LBL,DECL), #false : _variable_involve(presolve,LBL,X,DECL), _solve_conflictVariable(X).

_solve_firstLabel(X,LBL) :-_solve_conflictVariable(X), _variable_involve(presolve,LBL,X,DECL), 0 = #count { LBL2 : _variable_involve(presolve,LBL2,X,DECL2), LBL2 < LBL }.
_passed(solve,LBL,variable_declare(X,definition)) :- _solve_firstLabel(X,LBL).
_passed(solve,LBL,variable_define(X,bad)) :- _solve_firstLabel(X,LBL).

:- _passed(solve,L1,variable_define(X,E1)), _passed(solve,L2,variable_define(X,E2)), (L1,E1)!=(L2,E2).

_passed(skip,DECL) :- _phase_active(solve), _passed(solve,LBL,DECL), DECL=(warning_forbid(KIND,TGT);warning_ignore(KIND,TGT)).
_passed(compile,LBL,DECL) :- _phase_active(solve), _passed(solve,LBL,DECL), _label(LBL,DECL), engine(LBL,compile), not _passed(skip,DECL).
_passed(compile2,LBL,DECL) :- _phase_active(solve), _passed(solve,LBL,DECL), _label(LBL,DECL), engine(LBL,compile2), not _passed(skip,DECL).
_passed(ground,LBL,DECL) :- _phase_active(solve), _passed(solve,LBL,DECL), _label(LBL,DECL), engine(LBL,ground), not _passed(skip,DECL).
_passed(propagator,LBL,DECL) :- _phase_active(solve), _passed(solve,LBL,DECL), _label(LBL,DECL), engine(LBL,propagator), not _passed(skip,DECL).

_passed((compile;compile2;ground;propagator;none),LBL,warning_forbid(W,TGT)) :- _passed(solve,LBL,warning_forbid(W,TGT)).
_passed((compile;compile2;ground;propagator;none),LBL,warning_ignore(W,TGT)) :- _passed(solve,LBL,warning_ignore(W,TGT)).

_optimize_component(LBL,E,ORIG,PREC,ID,PRIORITY) :- _phase_active(solve), _passed(solve,LBL,optimize_component(E,ORIG,PREC,ID,PRIORITY)), engine(LBL,ENG), _engine_supportOptimization(ENG).
_passed(solve,LBL,share_value(E;O;P)) :- _phase_active(solve), _passed(solve,LBL,optimize_component(E,O,P,ID,PRIORITY)).

_preference_expressionScore(E,K) :- _phase_active(solve), _passed(solve,LBL,preference_holds(E,K)), engine(LBL,(compile;compile2;ground)).
_passed(solve,LBL,share_value(E)) :- _phase_active(solve), _passed(solve,LBL,preference_holds(E,K)).

_evaluate(operation(OP,ARGS)) :- _phase_active(solve), _passed(solve,LBL,evaluate(OP,ARGS)), engine(LBL,(compile;compile2;ground)).
_passed(solve,LBL,share_value(operation(OP,ARGS))) :- _phase_active(solve), _passed(solve,LBL,evaluate(OP,ARGS)).

_passed(solve,LBL,share_value(E)) :- _phase_active(solve), _passed(solve,LBL,bool_evaluate(E)).
_passed(solve,LBL,share_value(E)) :- _phase_active(solve), _passed(solve,LBL,ensure(E)), engine(LBL,(compile;compile2;ground)).
