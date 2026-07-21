evaluate(mult,(val(float,float("2.5")),(val(int,2),()))).
evaluate(mult,(val(float,float("0.0")),(bad,()))).
evaluate(mult,(val(float,float("2.5")),(val(none,none),()))).
evaluate(mult,(val(float,float("2.5")),(bad,()))).


variable_declare(x,fromFacts).
variable_domain(x,val(float,float("2.5"))).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(mult,(variable(x),(val(int,2),()))).
evaluate(mult,(variable(x),(val(none,none),()))).
evaluate(mult,(variable(x),(bad,()))).
