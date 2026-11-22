### Input predicates

_bool_evaluated/2.
_expression(compile,variable/1).
_passed(ENG,LBL,share_value/1).
_se_value/2.
_set_contains/2.
ch_post(variable_interface/1,LBL).
ch_post(evaluate/2,LBL).
_warning/3.
ch_core(variable_declare/3,LBL).
ch_core(warning_forbid/1,LBL).
ch_core(warning_ignore/1,LBL).

### Intermediate predicates

_se_value1/1.
_shared_value/2.
_variable_typed/2.
_variable_declared/1.
_warning_forbid/2.
_warning_ignore/2.
_warning_raised/2.
warning_raised/0.

### Output predicates

set_value/2.
variable_typed/2.
value/2.
variable_declared/1.
variable_defined/1.
warning/3.
evaluated/2.
