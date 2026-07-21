
evaluate(lxor,(val(bool,true),())).
evaluate(lxor,(val(none,none),())).
evaluate(lxor,(bad,())).

variable_declare(x,fromFacts).
variable_domain(x,val(bool,true)).
variable_domain(x,val(bool,false)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(lxor,(variable(x),())).
