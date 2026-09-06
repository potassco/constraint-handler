evaluate(operation(leq,(val(float,float("1.5")),(val(int,2),())))).
evaluate(operation(leq,(val(float,float("2.5")),(val(int,2),())))).
evaluate(operation(leq,(val(float,float("1.5")),(val(none,none),())))).
evaluate(operation(leq,(val(float,float("1.5")),(bad,())))).


variable_declare(x,fromFacts).
variable_domain(x,val(float,float("2.5"))).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(operation(leq,(variable(x),(val(float,float("1.5")),())))).
evaluate(operation(leq,(variable(x),(val(none,none),())))).
evaluate(operation(leq,(variable(x),(bad,())))).
