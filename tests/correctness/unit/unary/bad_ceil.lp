
evaluate(ceil,(val(int,2),())).
evaluate(ceil,(val(none,none),())).
evaluate(ceil,(bad,())).

variable_declare(x,fromFacts).
variable_domain(x,val(int,2)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(ceil,(variable(x),())).
