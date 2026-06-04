### Input predicates

\_phase_active(wf_check).
\_expression(sugar,EXPR).
\_passed(sugar,LBL,DECL).
\_passed(defaultArgs,LBL,execution_declare/4).
\_statement_wellformed/1.

### Intermediate predicates

\_expression_wfQuery/1.
\_expression_wellformed/1.
\_illformed/1. \_illformed/2.

### Output predicates

\_passed(correction(wf_check,rem),LBL,DECL).
\_passed(correction(wf_check,add),LBL,DECL).
\_warning/3.
