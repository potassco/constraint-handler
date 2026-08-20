phase_request(constantFolding,false).

variable_declare(x,fromFacts).
variable_domain(x,val(string,"ab")).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(concat,(variable(x),(val(string,"c"),()))).
evaluate(concat,(variable(x),(val(none,none),()))).
evaluate(concat,(variable(x),(bad,()))).

variable_declare(y,fromFacts).
variable_domain(y,val(string,"ab")).
variable_domain(y,val(string,"ba")).
evaluate(concat,(val(string,"c"),(variable(y),()))).
