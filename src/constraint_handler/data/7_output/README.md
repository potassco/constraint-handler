### Input predicates

_expression(compile,variable/1).
_engine_grounding/1.
_passed(ENG,LBL,share_value/1).
_se_value/2.
_set_contains/2.
ch_post(variable_interface/2).
_warning/3.
ch_core(warning_forbid/1,LBL).
ch_core(warning_ignore/1,LBL).

### Intermediate predicates

_se_value1/1.
_shared_value/2.
_type_variableD/2.
_warning_forbid/2.
_warning_ignore/2.
_warning_raised/2.
warning_raised/0.

### Output predicates

set_value/2.
type_variableD/2.
value/2.
warning/3.
