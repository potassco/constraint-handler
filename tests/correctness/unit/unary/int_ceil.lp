evaluate(ceil,(val(int,-3),())).
evaluate(ceil,(val(int,2),())).
evaluate(ceil,(val(none,none),())).
evaluate(ceil,(bad,())).

phase_request(type_check,true).

variable_declare(x,fromFacts).
variable_domain(x,val(int,-3)).
variable_domain(x,val(int,2)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(ceil,(variable(x),())).