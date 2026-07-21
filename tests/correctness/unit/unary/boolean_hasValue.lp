phase_request(type_check,true).

variable_declare(x,fromFacts).
variable_domain(x,val(bool,false)).
variable_domain(x,val(bool,true)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(hasValue,(variable(x),())).

evaluate(hasValue,(val(bool,false),())).
evaluate(hasValue,(val(bool,true),())).
evaluate(hasValue,(val(none,none),())).
evaluate(hasValue,(bad,())).