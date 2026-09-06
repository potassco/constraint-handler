evaluate(operation(geq,(val(int,3),(val(int,2),())))).
evaluate(operation(geq,(val(int,2),(val(int,3),())))).
evaluate(operation(geq,(val(int,2),(val(int,2),())))).
evaluate(operation(geq,(val(int,2),(val(none,none),())))).
evaluate(operation(geq,(val(int,2),(bad,())))).


variable_declare(x,fromFacts).
variable_domain(x,val(int,3)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(operation(geq,(variable(x),(val(int,2),())))).
evaluate(operation(geq,(variable(x),(val(none,none),())))).
evaluate(operation(geq,(variable(x),(bad,())))).
