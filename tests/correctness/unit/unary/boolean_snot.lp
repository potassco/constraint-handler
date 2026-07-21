phase_request(type_check,true).

variable_declare(x,fromFacts).
variable_domain(x,val(bool,false)).
variable_domain(x,val(bool,true)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(snot,(variable(x),())).

evaluate(snot,(val(bool,false),())).
evaluate(snot,(val(bool,true),())).
evaluate(snot,(val(none,none),())).
evaluate(snot,(bad,())).