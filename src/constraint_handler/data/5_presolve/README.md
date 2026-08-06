### Input predicates

_passed(sugar,LBL,DECL).
_passed(correction(REASON,add),LBL,DECL).
_passed(correction(REASON,rem),LBL,DECL).
_phase_active(solve).
_variable(sugar,X).
defaultEngine/1.
requestEngine/2.

### Intermediate predicates

_engine_supportOptimization/1.
_label/1. _label/2.
_main_defaultEngine/1.
_main_defaultEngineProvided/0.
_main_engine/1.
_main_requestedEngine/1.
_preference_expressionScore/2.
_solve_conflictVariable/1.
_solve_firstLabel/2.
_variable_involve(presolve,LBL,X,DECL).
engine/2.
_passed(presolve,LBL,DECL).
_passed(skip,DECL).
_passed(solve,LBL,DECL).

### Output predicates

_evaluate/1.
_optimize_component/6.
_passed(compile,LBL,DECL).
_passed(compile2,LBL,DECL).
_passed(ground,LBL,DECL).
_passed(none,LBL,warning_forbid/2).
_passed(none,LBL,warning_ignore/2).
_passed(propagator,LBL,DECL).
_passed(solve,LBL,share_value/1).
