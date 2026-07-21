% compile2 currently goes UNSAT for lxor with none-valued operands.

phase_request(type_check,true).

variable_declare(x,fromFacts).
variable_domain(x,val(bool,true)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(lxor,(variable(x),(val(bool,false),()))).
evaluate(lxor,(variable(x),(val(none,none),()))).
evaluate(lxor,(variable(x),(bad,()))).


evaluate(lxor,(val(none,none),())).
evaluate(lxor,(val(bool,false),(val(none,none),()))).
