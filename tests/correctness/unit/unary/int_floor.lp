evaluate(floor,(val(int,-3),())).
evaluate(floor,(val(int,2),())).
evaluate(floor,(val(none,none),())).
evaluate(floor,(bad,())).

phase_request(type_check,true).

variable_declare(x,fromFacts).
variable_domain(x,val(int,-3)).
variable_domain(x,val(int,2)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(floor,(variable(x),())).