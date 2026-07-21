evaluate(max,(val(int,2),(val(int,3),()))).
evaluate(max,(val(int,3),(val(int,2),()))).
evaluate(max,(val(int,2),(val(none,none),()))).
evaluate(max,(val(int,2),(bad,()))).

phase_request(type_check,true).

variable_declare(x,fromFacts).
variable_domain(x,val(int,2)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(max,(variable(x),(val(int,3),()))).
evaluate(max,(variable(x),(val(none,none),()))).
evaluate(max,(variable(x),(bad,()))).

