evaluate(ceil,(val(float,float("1.5")),())).
evaluate(ceil,(val(none,none),())).
evaluate(ceil,(bad,())).

phase_request(type_check,true).

variable_declare(x,fromFacts).
variable_domain(x,val(float,float("1.5"))).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(ceil,(variable(x),())).