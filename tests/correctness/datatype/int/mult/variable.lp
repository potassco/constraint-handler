phase_request(constantFolding,false).

variable_declare(x,fromFacts).
variable_domain(x,val(int,2)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(mult,(val(int,5),(variable(x),()))).
evaluate(mult,(variable(x),(val(int,3),()))).
evaluate(mult,(variable(x),(val(none,none),()))).
evaluate(mult,(variable(x),(bad,()))).
