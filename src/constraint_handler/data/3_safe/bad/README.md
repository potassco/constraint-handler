### Input predicates

\_expression(sugar,EXPR).
\_expression_operationIndex(sugar,EXPR,IDX,F).
\_expression_operationOperator(sugar,EXPR,OP).
\_expression_tupleIndex(sugar,EXPR,IDX,F).
\_operator_recoverable/1.
\_operator_safe/1.
\_passed(sugar,LBL,DECL).
\_variable(sugar,X).

### Intermediate predicates

\_deterministic/2.
\_main/1.
\_safe_bad/1.
\_variable_query/2.
\_variable_safe/1.

### Output predicates

\_expression_safe/1.
\_expression_safeQuery/1.
\_operator_unsafe/1.
\_passed(correction(constant,rem),LBL,DECL).
\_passed(correction(constant,add),LBL,DECL).
