### Input predicates

_passed(sugar,LBL,DECL).
_passed(correction(REASON,add),LBL,DECL).
_passed(correction(REASON,rem),LBL,DECL).
_phase_active(solve).
_variable(sugar,X).
engine_default/1.
engine_request/2.

### Intermediate predicates

_label/1.
_engine_default/1.
_engine_defaultProvided/0.
_engine/1. _engine/2.
_engine_userRequest/1.
_engine_grounding/1.
_engine_propagator/1.
_preference_expressionScore/2.
_solve_conflictVariable/1.
_solve_firstLabel/2.
_variable_involve(presolve,LBL,X,DECL).
_passed(presolve,LBL,DECL).

### Output predicates

ch_core(DECL,LBL).
ch_solve(DECL,LBL).
