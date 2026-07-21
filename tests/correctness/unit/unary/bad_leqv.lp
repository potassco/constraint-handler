phase_request(type_check,true).

evaluate(leqv,(val(bool,true),())).
evaluate(leqv,(val(none,none),())).
evaluate(leqv,(bad,())).

variable_declare(x,fromFacts).
variable_domain(x,val(bool,true)).
variable_domain(x,val(bool,false)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(leqv,(variable(x),())).