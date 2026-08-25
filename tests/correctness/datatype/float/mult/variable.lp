phase_request(constantFolding,false).

variable_declare(x,fromFacts).
variable_domain(x,val(float,float("2.5"))).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(mult,(variable(x),(val(int,2),()))).
evaluate(mult,(variable(x),(val(float,float("5.75")),()))).
evaluate(mult,(val(float,float("3.875")),(variable(x),()))).
evaluate(mult,(variable(x),(val(none,none),()))).
evaluate(mult,(variable(x),(bad,()))).
