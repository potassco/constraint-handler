variable_declare(x,fromFacts).
variable_domain(x,val(bool,false)).
variable_domain(x,val(bool,true)).
variable_domain(x,bad).

evaluate(operation(leqv,(variable(x),(val(bool,false),())))).
evaluate(operation(leqv,(variable(x),(val(bool,true),())))).
evaluate(operation(leqv,(variable(x),(bad,())))).
evaluate(operation(lxor,(variable(x),(val(bool,false),())))).
evaluate(operation(lxor,(variable(x),(val(bool,true),())))).
evaluate(operation(lxor,(variable(x),(bad,())))).
