evaluate(operation(float_div,(val(int,3),(val(int,2),())))).
evaluate(operation(float_div,(val(int,3),(val(none,none),())))).
evaluate(operation(float_div,(val(int,3),(bad,())))).


variable_declare(x,fromFacts).
variable_domain(x,val(float,float("3.0"))).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(operation(float_div,(variable(x),(val(int,2),())))).
evaluate(operation(float_div,(variable(x),(val(none,none),())))).
evaluate(operation(float_div,(variable(x),(bad,())))).
