### Input predicates

_expression(compile,variable/1).
_evaluate/1.
_passed(compile,LBL,bool_evaluate/1).
_passed(compile,LBL,evaluate/2).
_passed(compile,LBL,ensure/1).
_passed(compile,LBL,share_value/1).
_passed(compile2,LBL,bool_evaluate/1).
_passed(compile2,LBL,share_value/1).
_passed(ground,LBL,bool_evaluate/1).
_passed(ground,LBL,share_value/1).
_passed(propagator,LBL,bool_evaluate/1).
_passed(solve,LBL,variable_interface/1).
_se_value/2.
_set_contains/2.
_warning/3.

### Intermediate predicates

_shared_value/2.
_warning_forbid/2.
_warning_ignore/2.
_warning_raised/2.
type_variableD/2.
warning_raised/0.

### Output predicates

bool_evaluated/2.
set_value/2.
value/2.
warning/3.
evaluated/3.
