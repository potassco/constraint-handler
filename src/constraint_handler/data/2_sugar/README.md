### Input predicates

_passed(defaultArgs,LBL,bool_evaluate/1).
_passed(defaultArgs,LBL,ensure/1).
_passed(defaultArgs,LBL,evaluate/2).
_passed(defaultArgs,LBL,variable_define/2).
_passed(defaultArgs,LBL,variable_declare/2).
_passed(defaultArgs,LBL,variable_domain/2).
_passed(defaultArgs,LBL,variable_declareOptional/1).
_passed(defaultArgs,LBL,multimap_declare/1).
_passed(defaultArgs,LBL,multimap_assign/3).
_passed(defaultArgs,LBL,set_declare/1).
_passed(defaultArgs,LBL,set_assign/2).
_passed(defaultArgs,LBL,set_baseDomain/2).
_passed(defaultArgs,LBL,optimize_precision/2).
_passed(defaultArgs,LBL,optimize_maximizeSum/3).
_passed(defaultArgs,LBL,preference_holds/2).
_passed(defaultArgs,LBL,preference_variableValue/3).
_passed(defaultArgs,LBL,warning_forbid/1).
_passed(defaultArgs,LBL,warning_ignore/1).

### Intermediate predicates

None.

### Output predicates

_passed(sugar,LBL,bool_evaluate/1).
_passed(sugar,LBL,ensure/1).
_passed(sugar,LBL,evaluate/2).
_passed(sugar,LBL,variable_declare/2).
_passed(sugar,LBL,variable_define/2).
_passed(sugar,LBL,variable_domain/2).
_passed(sugar,LBL,variable_interface/1).
_passed(sugar,LBL,multimap_assign/3).
_passed(sugar,LBL,set_assign/2).
_passed(sugar,LBL,set_baseDomain/2).
_passed(sugar,LBL,optimize_component(EXPR,PRECISION,ID,PRIORITY)).
_passed(sugar,LBL,preference_holds/2).
_passed(sugar,LBL,warning_forbid/1).
_passed(sugar,LBL,warning_ignore/1).
_expression(sugar,val/2).
_expression(sugar,operation/2).
