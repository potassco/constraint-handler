phase_request(constantFolding,false).

evaluate(leqv,(val(bool,true),(val(none,none),()))).
evaluate(leqv,(val(bool,false),(val(none,none),()))).
evaluate(leqv,(val(none,none),(val(bool,true),()))).
evaluate(leqv,(val(none,none),(val(bool,false),()))).
evaluate(leqv,(val(none,none),(val(none,none),()))).
evaluate(lxor,(val(bool,true),(val(none,none),()))).
evaluate(lxor,(val(bool,false),(val(none,none),()))).
evaluate(lxor,(val(none,none),(val(bool,true),()))).
evaluate(lxor,(val(none,none),(val(bool,false),()))).
evaluate(lxor,(val(none,none),(val(none,none),()))).

variable_declare(x,fromFacts).
variable_domain(x,val(bool,true)).
variable_domain(x,val(bool,false)).
variable_domain(x,val(none,none)).
evaluate(leqv,(val(none,none),(variable(x),()))).
evaluate(lxor,(val(none,none),(variable(x),()))).
