### Input predicates

\_passed(sugar,variable_declare/3).
\_passed(sugar,variable_define/3).
\_passed(sugar,variable_domain/3).
\_passed(sugar,set_assign/3).
\_passed(sugar,set_baseDomain/3).
\_passed(sugar,multimap_assign/4).
\_passed(defaultArgs,variable_declare/3).
\_passed(defaultArgs,variable_domain/3).
\_passed(defaultArgs,variable_define/3).
\_passed(defaultArgs,set_declare/2).
\_passed(defaultArgs,set_assign/3).
\_passed(defaultArgs,set_baseDomain/3).
\_passed(defaultArgs,multimap_declare/2).
\_passed(defaultArgs,multimap_assign/4).
\_variable(sugar,VAR).
\_operator_declared/1.
\_se_value/2.
\_statement_internalVariable/1.
\_statement_introduce/3.

### Intermediate predicates

\_variable_hasDomain/2.
\_variable_exists/2.
\_variable_involve/3.
\_variable_confusingName/2.
\_variable_declared/1.
\_variable_reservedName/1.
\_variable_multipleDeclarations/3.
\_variable_multipleDefinitions/3.
\_variable_multiple/2.

### Output predicates

\_passed(correction(REASON,add),LBL,variable_declare/3).
\_passed(correction(REASON,add),LBL,variable_define/3).
\_passed(correction(REASON,rem),DECL).
\_passed(sugar,variable_declare/3).
\_warning/3.
