
variable_declare(x,fromFacts).
variable_domain(x,val(string,"ab")).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(concat,(variable(x),(val(string,"c"),()))).
evaluate(concat,(variable(x),(val(none,none),()))).
evaluate(concat,(variable(x),(bad,()))).


evaluate(concat,(val(string,"ab"),(val(string,"c"),()))).
evaluate(concat,(val(string,""),(val(string,"c"),()))).
evaluate(concat,(val(string,"ab"),(val(string,""),()))).
evaluate(concat,(val(none,none),(val(string,"c"),()))).
evaluate(concat,(val(string,"ab"),(val(none,none),()))).
evaluate(concat,(bad,(val(string,"c"),()))).
