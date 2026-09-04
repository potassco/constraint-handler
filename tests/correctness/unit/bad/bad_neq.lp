evaluate(operation(neq,(val(int,1),(val(int,1),())))).
evaluate(operation(neq,(val(int,1),(val(int,2),())))).
evaluate(operation(neq,(val(none,none),(val(int,1),())))).
evaluate(operation(neq,(val(int,1),(bad,())))).

variable_declare(x,fromFacts).
variable_domain(x,val(int,1)).
variable_domain(x,val(int,2)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(operation(neq,(variable(x),(val(int,1),())))).
evaluate(operation(neq,(variable(x),(val(int,2),())))).
evaluate(operation(neq,(variable(x),(val(none,none),())))).
evaluate(operation(neq,(variable(x),(bad,())))).
