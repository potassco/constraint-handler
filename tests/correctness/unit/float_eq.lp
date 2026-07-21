evaluate(eq,(val(float,float("2.5")),(val(float,float("2.5")),()))).
evaluate(eq,(val(int,2),(val(float,float("2.0")),()))).
evaluate(eq,(val(none,none),(val(none,none),()))).
evaluate(eq,(val(float,float("1.5")),(val(none,none),()))).
evaluate(eq,(val(float,float("1.5")),(bad,()))).

phase_request(type_check,true).

variable_declare(x,fromFacts).
variable_domain(x,val(float,float("2.5"))).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(eq,(variable(x),(val(float,float("2.5")),()))).
evaluate(eq,(variable(x),(val(none,none),()))).
evaluate(eq,(variable(x),(bad,()))).

