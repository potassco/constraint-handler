phase_request(type_check,true).

evaluate(minus,(val(int,2),())).
evaluate(minus,(val(none,none),())).
evaluate(minus,(bad,())).

variable_declare(x,fromFacts).
variable_domain(x,val(int,2)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(minus,(variable(x),())).