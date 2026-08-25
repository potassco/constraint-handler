phase_request(constantFolding,false).

variable_declare(x,fromFacts).
variable_domain(x,val(float,float("2.5"))).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(sub,(variable(x),(val(int,2),()))).
evaluate(sub,(val(int,6),(variable(x),()))).
evaluate(sub,(variable(x),(val(float,float("20.0")),()))).
evaluate(sub,(val(float,float("60.0")),(variable(x),()))).
evaluate(sub,(variable(x),(val(none,none),()))).
evaluate(sub,(variable(x),(bad,()))).
