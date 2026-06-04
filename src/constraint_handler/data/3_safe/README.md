### Input predicates

\_passed(defaultArgs,DECL).
\_passed(sugar,DECL).
\_expression(sugar,EXPR).
\_variable(sugar,VAR).
\_statement_wellformed/1.
\_statement_internalVariable/1.

### Intermediate predicates

\_deterministic/2.
\_expression_operationIndex/4.
\_expression_operationLength/3.
\_expression_operationOperator/3.
\_expression_sequence/2.
\_expression_sequenceIndex/4.
\_expression_sequenceLength/3.
\_expression_tupleIndex/4.
\_expression_typeQuery/1.
\_expression_wellformed/1.
\_expression_wfQuery/1.
\_illformed/1. \_illformed/2.
\_main/1.
\_operator_declared/1.
\_operator_recoverable/1.
\_operator_safe/1.
\_operator_unsafe/1.
\_phase_active/1.
\_safe_bad/1.
\_se_value/2.
\_type/1.
\_type_list/2.
\_type_listArgT/3.
\_type_listAux/3.
\_type_operator/2.
\_type_variable/2.
\_type_variadicListAux/5.
\_variable_confusingName/2.
\_variable_declared/1.
\_variable_exists/2.
\_variable_hasDomain/2.
\_variable_query/2.
\_variable_safe/1.
operator_declare/3.
operator_declare_variadic/4.
operator_variadic/2.
type_expressionTyped/1.
type_query/1.
type_variable/2.

### Output predicates

\_passed(correction(add),LBL,DECL).
\_passed(correction(change,REASON),OLD,NEW).
\_warning/3.
\_expression_safe/1.
\_expression_safeQuery/1.
type_expression/2.
