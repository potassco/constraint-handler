### Input predicates

_engine/2.
_passed(compile,LBL,variable_declare/2).
_passed(compile,LBL,variable_domain/2).
_passed(ground,LBL,variable_declare/2).
_passed(ground,LBL,variable_domain/2).
_phase_active/1.
_se_value/2.
_shared_value/2.
ch_core(optimize_component/5,LBL).

### Intermediate predicates

_optimize_component/6.

### Output predicates

_ge_assign/2.
_se_value/2.
ch_solve(share_value/1,LBL).
propagator_optimize_maximizeSum/4.
