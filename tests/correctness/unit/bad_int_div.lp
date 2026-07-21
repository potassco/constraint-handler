
evaluate(int_div,(val(int,4),(val(int,2),()))).
evaluate(int_div,(val(int,4),(val(none,none),()))).
evaluate(int_div,(val(int,4),(bad,()))).

variable_declare(x,fromFacts).
variable_domain(x,val(int,4)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(int_div,(variable(x),(val(int,2),()))).
evaluate(int_div,(variable(x),(val(none,none),()))).
evaluate(int_div,(variable(x),(bad,()))).
