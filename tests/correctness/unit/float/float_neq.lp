evaluate(operation(neq,(val(float,float("2.5")),(val(float,float("2.5")),())))).
evaluate(operation(neq,(val(int,2),(val(float,float("2.0")),())))).
evaluate(operation(neq,(val(none,none),(val(none,none),())))).
evaluate(operation(neq,(val(float,float("1.5")),(val(none,none),())))).
evaluate(operation(neq,(val(float,float("1.5")),(bad,())))).


variable_declare(x,fromFacts).
variable_domain(x,val(float,float("2.5"))).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(operation(neq,(variable(x),(val(float,float("2.5")),())))).
evaluate(operation(neq,(variable(x),(val(none,none),())))).
evaluate(operation(neq,(variable(x),(bad,())))).
