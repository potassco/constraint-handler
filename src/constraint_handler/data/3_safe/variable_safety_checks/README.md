### Input predicates

_operator_declared/1.
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
_statement_introduce/3.
_variable(sugar,VAR).
_variable_internal(X).
_variable_involve(defaultArgs,LBL,X,DECL).
_variable_involve(sugar,LBL,X,DECL).

### Intermediate predicates

_variable_declared/1.
_variable_exists/2.
_variable_multipleDeclarations/3.
_variable_multipleDefinitions/3.
_variable_multiple/2.
_variable_name(conflict,X).
_variable_name(confusing/1,X).
_variable_name(reserved,X).
_variable_strip/3.

### Output predicates

_passed(correction(REASON,add),LBL,variable_declare/2).
_passed(correction(REASON,add),LBL,variable_define/2).
_passed(correction(REASON,rem),LBL,DECL).
_passed(sugar,LBL,variable_declare/2).
_warning/3.
