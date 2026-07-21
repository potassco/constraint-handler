
variable_declare(x,fromFacts).
variable_domain(x,val(string,"ab")).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(leq,(variable(x),(val(string,"aa"),()))).
evaluate(leq,(variable(x),(val(none,none),()))).
evaluate(leq,(variable(x),(bad,()))).


evaluate(leq,(val(string,"aa"),(val(string,"ab"),()))).
evaluate(leq,(val(string,"ab"),(val(string,"aa"),()))).
evaluate(leq,(val(string,"aa"),(val(string,"aa"),()))).
evaluate(leq,(val(none,none),(val(string,"ab"),()))).
evaluate(leq,(val(string,"aa"),(val(none,none),()))).
evaluate(leq,(val(string,"aa"),(bad,()))).
