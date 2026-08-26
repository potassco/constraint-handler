phase_request(constantFolding,false).

variable_declare(x,fromFacts).
variable_domain(x,val(int,2)).
variable_domain(x,val(int,5)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(add,(variable(x),(val(int,3),()))).
evaluate(add,(variable(x),(val(int,7),()))).
evaluate(add,(variable(x),(val(none,none),()))).
evaluate(add,(variable(x),(bad,()))).
