evaluate(minus,(val(int,-3),())).
evaluate(minus,(val(int,2),())).
evaluate(minus,(val(none,none),())).
evaluate(minus,(bad,())).

phase_request(type_check,true).

variable_declare(x,fromFacts).
variable_domain(x,val(int,-3)).
variable_domain(x,val(int,2)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(minus,(variable(x),())).