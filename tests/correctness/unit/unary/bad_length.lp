phase_request(type_check,true).

evaluate(length,(val(string,"ab"),())).
evaluate(length,(val(none,none),())).
evaluate(length,(bad,())).

variable_declare(x,fromFacts).
variable_domain(x,val(string,"ab")).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(length,(variable(x),())).