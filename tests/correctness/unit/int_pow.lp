evaluate(pow,(val(int,2),(val(int,3),()))).
evaluate(pow,(val(int,-3),(val(int,2),()))).
evaluate(pow,(val(none,none),(val(int,0),()))).
evaluate(pow,(bad,(val(int,0),()))).
evaluate(pow,(val(int,2),(val(none,none),()))).
evaluate(pow,(val(int,2),(bad,()))).
evaluate(pow,(bad,(val(int,3),()))).


variable_declare(x,fromFacts).
variable_domain(x,val(int,2)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(pow,(variable(x),(val(int,3),()))).
evaluate(pow,(variable(x),(val(none,none),()))).
evaluate(pow,(variable(x),(bad,()))).
