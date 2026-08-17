phase_request(constantFolding,false).

variable_declare(x,fromFacts).
variable_domain(x,val(bool,false)).
variable_domain(x,val(bool,true)).
variable_domain(x,bad).
evaluate(conj,(variable(x),(val(bool,false),()))).
evaluate(conj,(variable(x),(val(bool,true),()))).
evaluate(conj,(variable(x),(bad,()))).
evaluate(disj,(variable(x),(val(bool,false),()))).
evaluate(disj,(variable(x),(val(bool,true),()))).
evaluate(disj,(variable(x),(bad,()))).
