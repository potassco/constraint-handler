phase_request(constantFolding,false).

variable_declare(x,fromFacts).
variable_domain(x,val(float,float("2.5"))).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(add,(variable(x),(val(int,2),()))).
evaluate(add,(variable(x),(val(none,none),()))).
evaluate(add,(variable(x),(bad,()))).
