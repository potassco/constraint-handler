variable_declare(x,fromFacts).
variable_domain(x,val(int,1)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(getOrElse,(variable(x),(val(int,2),()))).
evaluate(getOrElse,(variable(x),(val(none,none),()))).
evaluate(getOrElse,(variable(x),(bad,()))).
