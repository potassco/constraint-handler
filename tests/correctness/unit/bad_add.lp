phase_request(type_check,true).

evaluate(add,(val(int,1),(val(int,2),()))).

variable_declare(x,fromFacts).
variable_domain(x,val(int,1)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(add,(variable(x),(val(int,2),()))).
evaluate(add,(variable(x),(val(none,none),()))).
evaluate(add,(variable(x),(bad,()))).
