evaluate(abs,(val(float,float("-1.5")),())).
evaluate(abs,(val(none,none),())).
evaluate(abs,(bad,())).


variable_declare(x,fromFacts).
variable_domain(x,val(float,float("-1.5"))).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(abs,(variable(x),())).
