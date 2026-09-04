evaluate(operation(gt,(val(int,2),(val(float,float("1.5")),())))).
evaluate(operation(gt,(val(int,2),(val(float,float("2.5")),())))).
evaluate(operation(gt,(val(float,float("1.5")),(val(none,none),())))).
evaluate(operation(gt,(val(float,float("1.5")),(bad,())))).


variable_declare(x,fromFacts).
variable_domain(x,val(float,float("2.5"))).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(operation(gt,(variable(x),(val(float,float("1.5")),())))).
evaluate(operation(gt,(variable(x),(val(none,none),())))).
evaluate(operation(gt,(variable(x),(bad,())))).
