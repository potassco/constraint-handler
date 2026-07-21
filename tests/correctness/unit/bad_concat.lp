
evaluate(concat,(val(string,"ab"),(val(string,"c"),()))).
evaluate(concat,(val(none,none),(val(string,"c"),()))).
evaluate(concat,(bad,(val(string,"c"),()))).

variable_declare(x,fromFacts).
variable_domain(x,val(string,"ab")).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(concat,(variable(x),(val(string,"c"),()))).
evaluate(concat,(variable(x),(val(none,none),()))).
evaluate(concat,(variable(x),(bad,()))).
