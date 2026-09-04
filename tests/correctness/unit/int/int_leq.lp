evaluate(operation(leq,(val(int,2),(val(int,3),())))).
evaluate(operation(leq,(val(int,3),(val(int,2),())))).
evaluate(operation(leq,(val(int,2),(val(int,2),())))).
evaluate(operation(leq,(val(int,2),(val(none,none),())))).
evaluate(operation(leq,(val(int,2),(bad,())))).


variable_declare(x,fromFacts).
variable_domain(x,val(int,2)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(operation(leq,(variable(x),(val(int,3),())))).
evaluate(operation(leq,(variable(x),(val(none,none),())))).
evaluate(operation(leq,(variable(x),(bad,())))).
