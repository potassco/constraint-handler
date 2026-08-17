
variable_declare(x,fromFacts).
variable_domain(x,val(bool,true)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(if,(variable(x),(val(int,1),()))).


evaluate(if,(val(bool,true),(val(int,1),()))).
evaluate(if,(val(bool,true),(bad,()))).
evaluate(if,(val(bool,false),(val(int,1),()))).
evaluate(if,(val(bool,false),(bad,()))).
evaluate(if,(val(none,none),(val(int,1),()))).
evaluate(if,(bad,(val(int,1),()))).
