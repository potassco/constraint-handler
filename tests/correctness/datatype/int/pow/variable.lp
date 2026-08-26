phase_request(constantFolding,false).

variable_declare(x,fromFacts).
variable_domain(x,val(int,2)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(pow,(variable(x),(val(int,3),()))).
evaluate(pow,(variable(x),(val(none,none),()))).
evaluate(pow,(variable(x),(bad,()))).
