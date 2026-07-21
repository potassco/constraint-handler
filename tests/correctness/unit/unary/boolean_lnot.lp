
variable_declare(x,fromFacts).
variable_domain(x,val(bool,false)).
variable_domain(x,val(bool,true)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(lnot,(variable(x),())).

evaluate(lnot,(val(bool,false),())).
evaluate(lnot,(val(bool,true),())).
evaluate(lnot,(val(none,none),())).
evaluate(lnot,(bad,())).
