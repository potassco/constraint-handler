evaluate(minus,(val(float,float("1.5")),())).
evaluate(minus,(val(none,none),())).
evaluate(minus,(bad,())).


variable_declare(x,fromFacts).
variable_domain(x,val(float,float("1.5"))).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(minus,(variable(x),())).
