evaluate(operation(leqv,(val(bool,true),(val(none,none),())))).
evaluate(operation(leqv,(val(bool,false),(val(none,none),())))).
evaluate(operation(leqv,(val(none,none),(val(bool,true),())))).
evaluate(operation(leqv,(val(none,none),(val(bool,false),())))).
evaluate(operation(leqv,(val(none,none),(val(none,none),())))).
evaluate(operation(lxor,(val(bool,true),(val(none,none),())))).
evaluate(operation(lxor,(val(bool,false),(val(none,none),())))).
evaluate(operation(lxor,(val(none,none),(val(bool,true),())))).
evaluate(operation(lxor,(val(none,none),(val(bool,false),())))).
evaluate(operation(lxor,(val(none,none),(val(none,none),())))).

evaluate(operation(leqv,(val(none,none),()))).
evaluate(operation(lxor,(val(none,none),()))).

variable_declare(x,fromFacts).
variable_domain(x,val(bool,true)).
variable_domain(x,val(bool,false)).
variable_domain(x,val(none,none)).
evaluate(operation(leqv,(val(none,none),(variable(x),())))).
evaluate(operation(lxor,(val(none,none),(variable(x),())))).
