ensure((absent,prop),operation(eq,(operation(hasValue,(variable(prop),())),(val(bool,false),())))).

evaluate(hasValue,(variable(prop),())).
evaluate(eq,(variable(prop),(val(string,"compact"),()))).
evaluate(neq,(variable(prop),(val(string,"compact"),()))).

variable_declare(prop,prop,fromFacts).
variable_declareOptional(prop).
variable_domain(prop,val(string,"wrapped")).

#show value/2.
