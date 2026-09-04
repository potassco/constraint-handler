evaluate(operation(min,(val(float,float("2.5")),(val(int,2),())))).
evaluate(operation(min,(val(float,float("2.5")),(val(none,none),())))).
evaluate(operation(min,(val(float,float("2.5")),(bad,())))).

variable_declare(x,fromFacts).
variable_domain(x,val(float,float("2.5"))).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(operation(min,(variable(x),(val(int,2),())))).
evaluate(operation(min,(variable(x),(val(none,none),())))).
evaluate(operation(min,(variable(x),(bad,())))).
