phase_request(constantFolding,false).

variable_define(two,val(int,2)).
variable_define(ten,val(int,10)).

variable_declare(x,fromFacts).
variable_domain(x,val(int,2)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(sub,(variable(two),(variable(ten),()))).
evaluate(sub,(variable(ten),(variable(two),()))).
evaluate(sub,(variable(x),(val(int,3),()))).
evaluate(sub,(variable(x),(val(none,none),()))).
evaluate(sub,(variable(x),(bad,()))).
