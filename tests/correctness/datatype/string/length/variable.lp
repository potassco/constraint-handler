phase_request(constantFolding,false).

variable_declare(x,fromFacts).
variable_domain(x,val(string,"ab")).
variable_domain(x,val(string,"")).
variable_domain(x,bad).
evaluate(length,(variable(x),())).

variable_declare(y,fromFacts).
variable_domain(y,val(string,"abc")).
variable_domain(y,val(string,"abcd")).
evaluate(length,(variable(y),())).
