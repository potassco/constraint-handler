
evaluate(leq,(val(int,1),(val(int,2),()))).
evaluate(leq,(val(int,2),(val(int,1),()))).
evaluate(leq,(val(none,none),(val(int,2),()))).
evaluate(leq,(val(int,1),(val(none,none),()))).
evaluate(leq,(val(int,1),(bad,()))).

variable_declare(x,fromFacts).
variable_domain(x,val(int,1)).
variable_domain(x,val(int,2)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(leq,(variable(x),(val(int,2),()))).
evaluate(leq,(variable(x),(val(int,1),()))).
evaluate(leq,(variable(x),(val(none,none),()))).
evaluate(leq,(variable(x),(bad,()))).
