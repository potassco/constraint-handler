phase_request(type_check,true).

evaluate(floor,(val(int,2),())).
evaluate(floor,(val(none,none),())).
evaluate(floor,(bad,())).

variable_declare(x,fromFacts).
variable_domain(x,val(int,2)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(floor,(variable(x),())).