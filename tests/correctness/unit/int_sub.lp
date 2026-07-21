evaluate(sub,(val(int,2),(val(int,-3),()))).
evaluate(sub,(val(int,-3),(val(int,2),()))).
evaluate(sub,(val(none,none),(val(int,2),()))).
evaluate(sub,(val(int,2),(bad,()))).


variable_declare(x,fromFacts).
variable_domain(x,val(int,2)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(sub,(variable(x),(val(int,3),()))).
evaluate(sub,(variable(x),(val(none,none),()))).
evaluate(sub,(variable(x),(bad,()))).
