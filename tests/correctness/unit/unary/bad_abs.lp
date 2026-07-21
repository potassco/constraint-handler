
evaluate(abs,(val(int,-2),())).
evaluate(abs,(val(none,none),())).
evaluate(abs,(bad,())).

variable_declare(x,fromFacts).
variable_domain(x,val(int,-2)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(abs,(variable(x),())).
