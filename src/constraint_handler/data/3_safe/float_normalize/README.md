### Input predicates

_phase_active(float_normalize).
_expression(sugar,EXPR).
_passed(sugar,LBL,DECL).

### Intermediate predicates

_float_normalizeQuery/1.
_float_normal/2.
_float_normalized/2.

### Output predicates

_passed(correction(float_normalize,rem),LBL,DECL).
_passed(correction(float_normalize,add),LBL,DECL).
_warning/3.
