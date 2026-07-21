evaluate(max,(val(float,float("1.5")),(val(int,2),()))).
evaluate(max,(val(float,float("1.5")),(val(none,none),()))).
evaluate(max,(val(float,float("1.5")),(bad,()))).


variable_declare(x,fromFacts).
variable_domain(x,val(float,float("2.5"))).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(max,(variable(x),(val(int,2),()))).
evaluate(max,(variable(x),(val(none,none),()))).
evaluate(max,(variable(x),(bad,()))).
