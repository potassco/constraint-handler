phase_request(constantFolding,false).

variable_declare(x,fromFacts).
variable_domain(x,val(bool,false)).
variable_domain(x,val(bool,true)).
variable_domain(x,bad).

evaluate(leqv,(variable(x),(val(bool,false),()))).
evaluate(leqv,(variable(x),(val(bool,true),()))).
evaluate(leqv,(variable(x),(bad,()))).
evaluate(lxor,(variable(x),(val(bool,false),()))).
evaluate(lxor,(variable(x),(val(bool,true),()))).
evaluate(lxor,(variable(x),(bad,()))).
