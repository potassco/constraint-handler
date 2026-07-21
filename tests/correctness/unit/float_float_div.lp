evaluate(float_div,(val(int,3),(val(int,2),()))).
evaluate(float_div,(val(int,3),(val(none,none),()))).
evaluate(float_div,(val(int,3),(bad,()))).

phase_request(type_check,true).

variable_declare(x,fromFacts).
variable_domain(x,val(float,float("3.0"))).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(float_div,(variable(x),(val(int,2),()))).
evaluate(float_div,(variable(x),(val(none,none),()))).
evaluate(float_div,(variable(x),(bad,()))).

