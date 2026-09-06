variable_declare(x,fromFacts).
variable_domain(x,val(int,1)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(operation(getOrElse,(variable(x),(val(int,2),())))).
evaluate(operation(getOrElse,(variable(x),(val(none,none),())))).
evaluate(operation(getOrElse,(variable(x),(bad,())))).
