### Input predicates

_passed(defaultArgs,LBL,bool_evaluate/1).
_passed(defaultArgs,LBL,ensure/1).
_passed(defaultArgs,LBL,evaluate/2).
_passed(defaultArgs,LBL,variable_declare/2).
_passed(defaultArgs,LBL,variable_define/2).
_passed(defaultArgs,LBL,variable_domain/2).
_passed(defaultArgs,LBL,variable_default/4).
_passed(defaultArgs,LBL,multimap_assign/3).
_passed(defaultArgs,LBL,set_assign/2).
_passed(defaultArgs,LBL,set_baseDomain/2).
_passed(defaultArgs,LBL,optimize_precision/2).
_passed(defaultArgs,LBL,optimize_maximizeSum/3).
_passed(defaultArgs,LBL,preference_holds/2).
_passed(defaultArgs,LBL,preference_variableValue/3).
_passed(defaultArgs,LBL,warning_forbid/2).
_passed(defaultArgs,LBL,warning_ignore/2).
_passed(ssa,LBL,DECL).
_variable(ssa,VAR).

### Intermediate predicates

_variable_execution_outputVar/1.

### Output predicates

_passed(sugar,LBL,bool_evaluate/1).
_passed(sugar,LBL,ensure/1).
_passed(sugar,LBL,evaluate/2).
_passed(sugar,LBL,share_value(E)).
_passed(sugar,LBL,variable_declare/2).
_passed(sugar,LBL,variable_define/2).
_passed(sugar,LBL,variable_default/4).
_passed(sugar,LBL,variable_domain/2).
_passed(sugar,LBL,variable_interface/1).
_passed(sugar,LBL,multimap_assign/3).
_passed(sugar,LBL,set_assign/2).
_passed(sugar,LBL,set_baseDomain/2).
_passed(sugar,LBL,optimize_component/5).
_passed(sugar,LBL,preference_holds/2).
_passed(sugar,LBL,warning_forbid/2).
_passed(sugar,LBL,warning_ignore/2).
_passed(internal_declaration,LBL,DECL).
_variable(sugar,VAR).
