### Input predicates

\_passed(sugar,variable_declare/3). \_passed(sugar,variable_domain/3).
\_passed(defaultArgs,variable_declare/3).
\_passed(defaultArgs,variable_domain/3).
\_passed(defaultArgs,variable_define/3). \_variable(sugar,VAR).
\_operator_declared/1. \_se_value/2. \_statement_internalVariable/1.

### Intermediate predicates

\_variable_hasDomain/2. \_variable_exists/2. \_variable_confusingName/2.
\_variable_declared/1.

### Output predicates

\_passed(correction(add),LBL,variable_declare/3).
\_passed(correction(add),LBL,variable_define/3).
\_passed(sugar,variable_declare/3). \_warning/3.
