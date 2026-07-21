evaluate(add,(val(int,2),(val(bool,true),()))).
evaluate(add,(val(int,2),(val(bool,false),()))).
evaluate(add,(val(int,-3),(val(int,2),(val(bool,true),())))).
evaluate(add,(val(int,2),(val(none,none),()))).
evaluate(add,(val(int,2),(bad,()))).

phase_request(type_check,true).

variable_declare(x,fromFacts).
variable_domain(x,val(int,2)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(add,(variable(x),(val(int,3),()))).
evaluate(add,(variable(x),(val(none,none),()))).
evaluate(add,(variable(x),(bad,()))).

