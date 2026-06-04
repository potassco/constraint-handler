### Input predicates

\_passed(propagator,LBL,bool_evaluate/1).
\_passed(propagator,LBL,ensure/1).
\_passed(propagator,LBL,evaluate/2).
\_passed(propagator,LBL,variable_declare/2).
\_passed(propagator,LBL,variable_domain/2).
\_passed(propagator,LBL,variable_define/2).
\_passed(propagator,LBL,set_assign/2).
\_passed(propagator,LBL,set_baseDomain/2).
\_passed(propagator,LBL,multimap_assign/3).
\_passed(propagator,LBL,optimize_maximizeSum/3).
\_passed(propagator,LBL,optimize_precision/2).
\_passed(solve,LBL,warning_forbid/1).
\_passed(solve,LBL,warning_ignore/1).

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
