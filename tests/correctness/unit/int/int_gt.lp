evaluate(operation(gt,(val(int,3),(val(int,2),())))).
evaluate(operation(gt,(val(int,2),(val(int,3),())))).
evaluate(operation(gt,(val(int,2),(val(int,2),())))).
evaluate(operation(gt,(val(int,2),(val(none,none),())))).
evaluate(operation(gt,(val(int,2),(bad,())))).


variable_declare(x,fromFacts).
variable_domain(x,val(int,3)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(operation(gt,(variable(x),(val(int,2),())))).
evaluate(operation(gt,(variable(x),(val(none,none),())))).
evaluate(operation(gt,(variable(x),(bad,())))).
