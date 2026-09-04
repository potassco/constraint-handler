variable_declare(x,fromFacts).
variable_domain(x,val(bool,false)).
variable_domain(x,val(bool,true)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(operation(hasValue,(variable(x),()))).

evaluate(operation(hasValue,(val(bool,false),()))).
evaluate(operation(hasValue,(val(bool,true),()))).
evaluate(operation(hasValue,(val(none,none),()))).
evaluate(operation(hasValue,(bad,()))).
