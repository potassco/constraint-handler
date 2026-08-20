phase_request(constantFolding,false).

evaluate(length,(bad,())).

variable_declare(x,fromFacts).
variable_domain(x,val(string,"ab")).
variable_domain(x,bad).
evaluate(length,(variable(x),())).
