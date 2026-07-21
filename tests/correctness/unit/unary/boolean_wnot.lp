
variable_declare(x,fromFacts).
variable_domain(x,val(bool,false)).
variable_domain(x,val(bool,true)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(wnot,(variable(x),())).

evaluate(wnot,(val(bool,false),())).
evaluate(wnot,(val(bool,true),())).
evaluate(wnot,(val(none,none),())).
evaluate(wnot,(bad,())).
