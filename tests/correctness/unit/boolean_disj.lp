phase_request(type_check,true).

variable_declare(x,fromFacts).
variable_domain(x,val(bool,true)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(disj,(variable(x),(val(bool,false),()))).
evaluate(disj,(variable(x),(val(none,none),()))).
evaluate(disj,(variable(x),(bad,()))).


evaluate(disj,(val(bool,false),(val(bool,false),()))).
evaluate(disj,(val(bool,false),(val(none,none),()))).
evaluate(disj,(val(bool,true),(val(bool,false),()))).
evaluate(disj,(val(bool,true),(val(none,none),()))).
evaluate(disj,(val(bool,false),(bad,()))).
evaluate(disj,(val(bool,true),(bad,()))).
