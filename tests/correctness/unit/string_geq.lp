
variable_declare(x,fromFacts).
variable_domain(x,val(string,"ab")).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(geq,(variable(x),(val(string,"aa"),()))).
evaluate(geq,(variable(x),(val(none,none),()))).
evaluate(geq,(variable(x),(bad,()))).


evaluate(geq,(val(string,"ab"),(val(string,"aa"),()))).
evaluate(geq,(val(string,"aa"),(val(string,"ab"),()))).
evaluate(geq,(val(string,"aa"),(val(string,"aa"),()))).
evaluate(geq,(val(none,none),(val(string,"ab"),()))).
evaluate(geq,(val(string,"aa"),(val(none,none),()))).
evaluate(geq,(val(string,"aa"),(bad,()))).
