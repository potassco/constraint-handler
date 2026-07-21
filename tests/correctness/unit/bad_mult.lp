phase_request(type_check,true).

evaluate(mult,(val(int,2),(val(int,3),()))).
evaluate(mult,(val(int,2),(val(none,none),()))).
evaluate(mult,(val(int,2),(bad,()))).

variable_declare(x,fromFacts).
variable_domain(x,val(int,2)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(mult,(variable(x),(val(int,3),()))).
evaluate(mult,(variable(x),(val(none,none),()))).
evaluate(mult,(variable(x),(bad,()))).
