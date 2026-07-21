
evaluate(lxor,(val(bool,false),(val(none,none),()))).
evaluate(lxor,(val(bool,true),(val(bool,false),()))).
evaluate(lxor,(val(bool,true),(bad,()))).

variable_declare(x,fromFacts).
variable_domain(x,val(bool,false)).
variable_domain(x,val(bool,true)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(lxor,(variable(x),(val(bool,false),()))).
evaluate(lxor,(variable(x),(val(none,none),()))).
evaluate(lxor,(variable(x),(bad,()))).
