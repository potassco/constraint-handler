phase_request(type_check,true).

variable_declare(x,fromFacts).
variable_domain(x,val(bool,true)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(leqv,(variable(x),(val(bool,false),()))).
evaluate(leqv,(variable(x),(val(none,none),()))).
evaluate(leqv,(variable(x),(bad,()))).


evaluate(leqv,(val(bool,true),(val(bool,false),()))).
evaluate(leqv,(val(bool,false),(val(bool,false),()))).
evaluate(leqv,(val(bool,true),(val(bool,false),(val(bool,false),())))).
evaluate(leqv,(val(bool,true),(val(bool,true),(val(bool,false),())))).
evaluate(leqv,(val(bool,true),(bad,()))).
