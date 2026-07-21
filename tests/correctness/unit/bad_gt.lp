
evaluate(gt,(val(int,2),(val(int,1),()))).
evaluate(gt,(val(int,1),(val(int,2),()))).
evaluate(gt,(val(none,none),(val(int,2),()))).
evaluate(gt,(val(int,1),(val(none,none),()))).
evaluate(gt,(val(int,1),(bad,()))).

variable_declare(x,fromFacts).
variable_domain(x,val(int,2)).
variable_domain(x,val(int,1)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(gt,(variable(x),(val(int,1),()))).
evaluate(gt,(variable(x),(val(int,2),()))).
evaluate(gt,(variable(x),(val(none,none),()))).
evaluate(gt,(variable(x),(bad,()))).
