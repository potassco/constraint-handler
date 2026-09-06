variable_declare(x,fromFacts).
variable_domain(x,val(int,2)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(operation(mult,(val(int,5),(variable(x),())))).
evaluate(operation(mult,(variable(x),(val(int,3),())))).
evaluate(operation(mult,(variable(x),(val(none,none),())))).
evaluate(operation(mult,(variable(x),(bad,())))).
