evaluate(floor,(val(float,float("2.5")),())).
evaluate(floor,(val(none,none),())).
evaluate(floor,(bad,())).

phase_request(type_check,true).

variable_declare(x,fromFacts).
variable_domain(x,val(float,float("2.5"))).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(floor,(variable(x),())).