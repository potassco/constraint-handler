evaluate(conj,(val(bool,true),(val(bool,true),()))).
evaluate(conj,(val(bool,true),(val(none,none),()))).
evaluate(conj,(val(bool,true),(bad,()))).
evaluate(conj,(val(bool,false),(val(bool,true),()))).
evaluate(conj,(val(bool,false),(val(none,none),()))).
evaluate(conj,(val(bool,false),(bad,()))).
evaluate(conj,(val(none,none),(val(bool,true),()))).
evaluate(conj,(val(none,none),(bad,()))).

variable_declare(x,fromFacts).
variable_domain(x,val(bool,true)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(conj,(variable(x),(val(bool,false),()))).
evaluate(conj,(variable(x),(val(bool,true),()))).
evaluate(conj,(variable(x),(val(none,none),()))).
evaluate(conj,(variable(x),(bad,()))).
