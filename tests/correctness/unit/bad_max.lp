phase_request(type_check,true).

evaluate(max,(val(int,1),(val(int,2),()))).
evaluate(max,(val(int,1),(val(none,none),()))).
evaluate(max,(val(int,1),(bad,()))).

variable_declare(x,fromFacts).
variable_domain(x,val(int,1)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(max,(variable(x),(val(int,2),()))).
evaluate(max,(variable(x),(val(none,none),()))).
evaluate(max,(variable(x),(bad,()))).
