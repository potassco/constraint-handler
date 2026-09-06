ensure((absent,prop),operation(eq,(operation(hasValue,(variable(prop),())),(val(bool,false),())))).

evaluate(operation(hasValue,(variable(prop),()))).
evaluate(operation(eq,(variable(prop),(val(string,"compact"),())))).
evaluate(operation(neq,(variable(prop),(val(string,"compact"),())))).

variable_declare(prop,prop,fromFacts).
variable_domain(prop,val(none,none)).
variable_domain(prop,val(string,"wrapped")).
