evaluate(geq,(val(int,3),(val(int,2),()))).
evaluate(geq,(val(int,2),(val(int,3),()))).
evaluate(geq,(val(int,2),(val(int,2),()))).
evaluate(geq,(val(int,2),(val(none,none),()))).
evaluate(geq,(val(int,2),(bad,()))).

phase_request(type_check,true).

variable_declare(x,fromFacts).
variable_domain(x,val(int,3)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(geq,(variable(x),(val(int,2),()))).
evaluate(geq,(variable(x),(val(none,none),()))).
evaluate(geq,(variable(x),(bad,()))).

