
variable_declare(x,fromFacts).
variable_domain(x,val(int,1)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(default,(variable(x),(val(int,2),()))).
evaluate(default,(variable(x),(val(none,none),()))).
evaluate(default,(variable(x),(bad,()))).


evaluate(default,(val(int,1),(val(int,2),()))).
evaluate(default,(bad,(val(int,2),()))).
evaluate(default,(val(none,none),(val(int,2),()))).
evaluate(default,(val(none,none),(bad,()))).
evaluate(default,(val(none,none),(val(none,none),()))).
