### Input predicates

\_phase_active(wf_check).
\_expression(sugar,EXPR).
\_passed(sugar,DECL).
\_passed(defaultArgs,execution_declare/5).
\_statement_wellformed/1.

### Intermediate predicates

\_expression_wfQuery/1.
\_expression_wellformed/1.
\_illformed/1. \_illformed/2.

### Output predicates

\_passed(correction(change,wf),OLD,NEW).
\_warning/3.
