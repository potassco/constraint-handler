
variable_declare(x,fromFacts).
variable_domain(x,val(string,"ab")).
variable_domain(x,val(string,"")).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(length,(variable(x),())).

evaluate(length,(val(string,"ab"),())).
evaluate(length,(val(string,""),())).
evaluate(length,(val(none,none),())).
evaluate(length,(bad,())).
