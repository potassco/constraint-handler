%%% binary conjunction/disjunction with none involved

phase_request(constantFolding,false).

evaluate(conj,(val(bool,false),(val(none,none),()))).
evaluate(conj,(val(none,none),(val(bool,false),()))).
evaluate(conj,(val(bool,true),(val(none,none),()))).
evaluate(conj,(val(none,none),(val(bool,true),()))).
evaluate(conj,(val(none,none),(val(none,none),()))).

evaluate(disj,(val(bool,false),(val(none,none),()))).
evaluate(disj,(val(none,none),(val(bool,false),()))).
evaluate(disj,(val(bool,true),(val(none,none),()))).
evaluate(disj,(val(none,none),(val(bool,true),()))).
evaluate(disj,(val(none,none),(val(none,none),()))).

variable_declare(x,fromFacts).
variable_domain(x,val(bool,true)).
variable_domain(x,val(bool,false)).
variable_domain(x,val(none,none)).
evaluate(conj,(variable(x),(val(bool,true),()))).
evaluate(conj,(variable(x),(val(none,none),()))).
evaluate(disj,(variable(x),(val(bool,false),()))).
evaluate(disj,(variable(x),(val(none,none),()))).
