evaluate(operation(minus,(val(float,float("1.5")),()))).
evaluate(operation(minus,(val(none,none),()))).
evaluate(operation(minus,(bad,()))).


variable_declare(x,fromFacts).
variable_domain(x,val(float,float("1.5"))).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(operation(minus,(variable(x),()))).
