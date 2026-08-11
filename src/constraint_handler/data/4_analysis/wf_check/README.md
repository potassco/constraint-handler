### Input predicates

_phase_active(wf_check).
_expression(sugar,EXPR).
_expression(sugar,LBL,DECL,EXPR).
_number(sugar,N).
_passed(defaultArgs,LBL,execution_declare/4).

### Intermediate predicates

_expression_wfQuery/1.
_expression_wellformed/1.

### Output predicates

_correction_expression(wf_check,EXPR,bad).
_correction_number(wf_check,N,0).
_warning/3.
