evaluate(operation(geq,(val(int,2),(val(int,1),())))).
evaluate(operation(geq,(val(int,1),(val(int,2),())))).
evaluate(operation(geq,(val(none,none),(val(int,2),())))).
evaluate(operation(geq,(val(int,1),(val(none,none),())))).
evaluate(operation(geq,(val(int,1),(bad,())))).

variable_declare(x,fromFacts).
variable_domain(x,val(int,2)).
variable_domain(x,val(int,1)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(operation(geq,(variable(x),(val(int,1),())))).
evaluate(operation(geq,(variable(x),(val(int,2),())))).
evaluate(operation(geq,(variable(x),(val(none,none),())))).
evaluate(operation(geq,(variable(x),(bad,())))).
