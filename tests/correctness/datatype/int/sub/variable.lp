variable_define(two,val(int,2)).
variable_define(ten,val(int,10)).

variable_declare(x,fromFacts).
variable_domain(x,val(int,2)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(operation(sub,(variable(two),(variable(ten),())))).
evaluate(operation(sub,(variable(ten),(variable(two),())))).
evaluate(operation(sub,(variable(x),(val(int,3),())))).
evaluate(operation(sub,(variable(x),(val(none,none),())))).
evaluate(operation(sub,(variable(x),(bad,())))).
