### Input predicates

_passed(ground,LBL,variable_assign/3).
_passed(ground,LBL,variable_choice/3).
_passed(ground,LBL,variable_declare/3).
_passed(ground,LBL,variable_default/4).
_passed(ground,LBL,variable_define/3).
_passed(ground,LBL,variable_domain/3).
_passed(ground,LBL,set_assign/3).
_passed(ground,LBL,share_value/1).
_se_value/2.
_direct_exploded/2.
_direct_imploded/2.
_expression_tupleLength(implode,EXPR,N).
_main_solverIdentifiers/1.

### Intermediate predicates

_expression(ground,EXPR).
_variable(ground,VAR).
_ge_eval_expression/1.
_ge_enumeratedVariables/2.
_ge_mapAux/3.
_ge_mapped/2.
_ge_eval_exec/3.

### Output predicates

_se_value/2.
_set_contains/2.
_set_candidate/2.
_direct_explode/1.
_direct_implode/1.
_direct_imploded/2.
_warning/3.
