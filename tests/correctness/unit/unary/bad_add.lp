
evaluate(add,(val(int,-2),())).
evaluate(add,(val(none,none),())).
evaluate(add,(bad,())).

variable_declare(x,fromFacts).
variable_domain(x,val(int,-2)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(add,(variable(x),())).
