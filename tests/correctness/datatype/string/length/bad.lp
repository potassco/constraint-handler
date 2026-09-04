evaluate(operation(length,(bad,()))).

variable_declare(x,fromFacts).
variable_domain(x,val(string,"ab")).
variable_domain(x,bad).
evaluate(operation(length,(variable(x),()))).
