
variable_declare(x,fromFacts).
variable_domain(x,val(string,"ab")).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(gt,(variable(x),(val(string,"aa"),()))).
evaluate(gt,(variable(x),(val(none,none),()))).
evaluate(gt,(variable(x),(bad,()))).


evaluate(gt,(val(string,"ab"),(val(string,"aa"),()))).
evaluate(gt,(val(string,"aa"),(val(string,"ab"),()))).
evaluate(gt,(val(string,"aa"),(val(string,"aa"),()))).
evaluate(gt,(val(none,none),(val(string,"ab"),()))).
evaluate(gt,(val(string,"aa"),(val(none,none),()))).
evaluate(gt,(val(string,"aa"),(bad,()))).
