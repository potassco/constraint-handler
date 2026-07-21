phase_request(type_check,true).

evaluate(eq,(val(int,1),(val(int,1),()))).
evaluate(eq,(val(int,1),(val(int,2),()))).
evaluate(eq,(val(none,none),(val(int,1),()))).
evaluate(eq,(val(int,1),(bad,()))).

variable_declare(x,fromFacts).
variable_domain(x,val(int,1)).
variable_domain(x,val(int,2)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(eq,(variable(x),(val(int,1),()))).
evaluate(eq,(variable(x),(val(int,2),()))).
evaluate(eq,(variable(x),(val(none,none),()))).
evaluate(eq,(variable(x),(bad,()))).
