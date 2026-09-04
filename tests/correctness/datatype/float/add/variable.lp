variable_declare(x,fromFacts).
variable_domain(x,val(float,float("2.5"))).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(operation(add,(variable(x),(val(int,2),())))).
evaluate(operation(add,(variable(x),(val(none,none),())))).
evaluate(operation(add,(variable(x),(bad,())))).
