evaluate(geq,(val(int,2),(val(float,float("1.5")),()))).
evaluate(geq,(val(int,2),(val(float,float("2.5")),()))).
evaluate(geq,(val(float,float("1.5")),(val(none,none),()))).
evaluate(geq,(val(float,float("1.5")),(bad,()))).

phase_request(type_check,true).

variable_declare(x,fromFacts).
variable_domain(x,val(float,float("2.5"))).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(geq,(variable(x),(val(float,float("1.5")),()))).
evaluate(geq,(variable(x),(val(none,none),()))).
evaluate(geq,(variable(x),(bad,()))).

