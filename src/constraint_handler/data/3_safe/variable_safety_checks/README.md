### Input predicates

_variable_internal(X).
_passed(sugar,LBL,variable_declare/2).
_passed(sugar,LBL,variable_define/2).
_passed(sugar,LBL,variable_domain/2).
_passed(sugar,LBL,set_assign/2).
_passed(sugar,LBL,set_baseDomain/2).
_passed(sugar,LBL,multimap_assign/3).
_passed(defaultArgs,LBL,variable_declare/2).
_passed(defaultArgs,LBL,variable_domain/2).
_passed(defaultArgs,LBL,variable_define/2).
_passed(defaultArgs,LBL,set_declare/1).
_passed(defaultArgs,LBL,set_assign/2).
_passed(defaultArgs,LBL,set_baseDomain/2).
_passed(defaultArgs,LBL,multimap_declare/1).
_passed(defaultArgs,LBL,multimap_assign/3).
_variable(sugar,VAR).
_operator_declared/1.
_statement_introduce/3.

### Intermediate predicates

_variable_exists/2.
_variable_involve/3.
_variable_confusingName/2.
_variable_declared/1.
_variable_reservedName/1.
_variable_multipleDeclarations/3.
_variable_multipleDefinitions/3.
_variable_multiple/2.

### Output predicates

_passed(correction(REASON,add),LBL,variable_declare/2).
_passed(correction(REASON,add),LBL,variable_define/2).
_passed(correction(REASON,rem),LBL,DECL).
_passed(sugar,LBL,variable_declare/2).
_warning/3.
