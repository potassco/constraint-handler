evaluate(pow,(val(float,float("2.5")),(val(int,2),()))).
evaluate(pow,(val(float,float("2.5")),(val(none,none),()))).
evaluate(pow,(val(float,float("2.5")),(bad,()))).

phase_request(type_check,true).

variable_declare(x,fromFacts).
variable_domain(x,val(float,float("2.5"))).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(pow,(variable(x),(val(int,2),()))).
evaluate(pow,(variable(x),(val(none,none),()))).
evaluate(pow,(variable(x),(bad,()))).

