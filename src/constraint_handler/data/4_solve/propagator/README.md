### Input predicates

_passed(propagator,bool_evaluate/2).
_passed(propagator,ensure/2).
_passed(propagator,evaluate/3).
_passed(propagator,variable_declare/3).
_passed(propagator,variable_domain/3).
_passed(propagator,variable_define/3).
_passed(propagator,set_assign/3).
_passed(propagator,set_baseDomain/3).
_passed(propagator,multimap_assign/4).
_passed(propagator,optimize_maximizeSum/4).
_passed(propagator,optimize_precision/3).
_passed(solve,warning_forbid/2).
_passed(solve,warning_ignore/2).

### Intermediate predicates

order/4.
higher_assigned_domain/3.

### Output predicates

propagator_bool_evaluate/2.
propagator_ensure/2.
propagator_evaluate/3.
propagator_variable_declare/3.
propagator_variable_domain/3.
propagator_variable_define/3.
propagator_set_declare/2.
propagator_set_assign/3.
propagator_set_baseDomain/3.
propagator_multimap_assign/4.
propagator_multimap_declare/2.
propagator_optimize_maximizeSum/4.
propagator_optimize_precision/2.
propagator_warning_forbid/2.
propagator_warning_ignore/2.