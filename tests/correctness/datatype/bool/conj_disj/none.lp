%%% binary conjunction/disjunction with none involved

evaluate(operation(conj,(val(bool,false),(val(none,none),())))).
evaluate(operation(conj,(val(none,none),(val(bool,false),())))).
evaluate(operation(conj,(val(bool,true),(val(none,none),())))).
evaluate(operation(conj,(val(none,none),(val(bool,true),())))).
evaluate(operation(conj,(val(none,none),(val(none,none),())))).

evaluate(operation(disj,(val(bool,false),(val(none,none),())))).
evaluate(operation(disj,(val(none,none),(val(bool,false),())))).
evaluate(operation(disj,(val(bool,true),(val(none,none),())))).
evaluate(operation(disj,(val(none,none),(val(bool,true),())))).
evaluate(operation(disj,(val(none,none),(val(none,none),())))).

variable_declare(x,fromFacts).
variable_domain(x,val(bool,true)).
variable_domain(x,val(bool,false)).
variable_domain(x,val(none,none)).
evaluate(operation(conj,(variable(x),(val(bool,true),())))).
evaluate(operation(conj,(variable(x),(val(none,none),())))).
evaluate(operation(disj,(variable(x),(val(bool,false),())))).
evaluate(operation(disj,(variable(x),(val(none,none),())))).
