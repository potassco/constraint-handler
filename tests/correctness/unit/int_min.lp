evaluate(min,(val(int,2),(val(int,3),()))).
evaluate(min,(val(int,3),(val(int,2),()))).
evaluate(min,(val(int,2),(val(none,none),()))).
evaluate(min,(val(int,2),(bad,()))).


variable_declare(x,fromFacts).
variable_domain(x,val(int,2)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(min,(variable(x),(val(int,3),()))).
evaluate(min,(variable(x),(val(none,none),()))).
evaluate(min,(variable(x),(bad,()))).
