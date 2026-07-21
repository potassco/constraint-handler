phase_request(type_check,true).

evaluate(sub,(val(int,3),(val(int,2),()))).
evaluate(sub,(val(int,3),(val(none,none),()))).
evaluate(sub,(val(int,3),(bad,()))).

variable_declare(x,fromFacts).
variable_domain(x,val(int,3)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(sub,(variable(x),(val(int,2),()))).
evaluate(sub,(variable(x),(val(none,none),()))).
evaluate(sub,(variable(x),(bad,()))).
