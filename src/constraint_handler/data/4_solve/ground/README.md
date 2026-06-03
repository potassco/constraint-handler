### Input predicates

\_passed(ground,bool_evaluate/2). \_passed(ground,ensure/2).
\_passed(ground,evaluate/3). \_passed(ground,variable_define/3).
\_passed(ground,variable_domain/3). \_passed(ground,variable_declare/3).
\_passed(ground,set_assign/3). \_passed(ground,set_baseDomain/3). evaluated/3.
\_direct_imploded/2. \_main_solverIdentifiers/1.

### Intermediate predicates

\_expression(ground,EXPR). \_ge_set_assign/3. \_ge_set_declare/2. ge_value/2.
\_variable(ground,VAR). \_ge_setAssignsAux/3. \_ge_setAssigns/2.
\_ge_enumeratedVariables/2. \_ge_mapAux/3. \_ge_mapped/2. \_ge_eval_exec/3.
ge_result/2.

### Output predicates

\_ge_assign/3. \_se_assign/3. \_se_value/2. \_set_declare/2. \_set_assign/3.
\_direct_implode/1. \_warning/3.
