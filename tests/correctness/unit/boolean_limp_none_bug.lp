% compile2 currently goes UNSAT for these left-none implication cases.

phase_request(type_check,true).

variable_declare(x,fromFacts).
variable_domain(x,val(bool,true)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(limp,(variable(x),(val(bool,false),()))).
evaluate(limp,(variable(x),(val(none,none),()))).
evaluate(limp,(variable(x),(bad,()))).


evaluate(limp,(val(none,none),(val(bool,false),()))).
evaluate(limp,(val(none,none),(val(none,none),()))).
