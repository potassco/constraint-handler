variable_declare(x,fromFacts).
variable_domain(x,val(string,"ab")).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(operation(concat,(variable(x),(val(string,"c"),())))).
evaluate(operation(concat,(variable(x),(val(none,none),())))).
evaluate(operation(concat,(variable(x),(bad,())))).

variable_declare(y,fromFacts).
variable_domain(y,val(string,"ab")).
variable_domain(y,val(string,"ba")).
evaluate(operation(concat,(val(string,"c"),(variable(y),())))).
