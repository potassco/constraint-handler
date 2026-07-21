% compile2 currently goes UNSAT here, while the other engines derive bad.

phase_request(type_check,true).

variable_declare(x,fromFacts).
variable_domain(x,val(bool,false)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(disj,(variable(x),(val(bool,false),()))).
evaluate(disj,(variable(x),(val(none,none),()))).
evaluate(disj,(variable(x),(bad,()))).


evaluate(disj,(val(none,none),(bad,()))).
