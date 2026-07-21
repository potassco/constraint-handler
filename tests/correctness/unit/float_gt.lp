evaluate(gt,(val(int,2),(val(float,float("1.5")),()))).
evaluate(gt,(val(int,2),(val(float,float("2.5")),()))).
evaluate(gt,(val(float,float("1.5")),(val(none,none),()))).
evaluate(gt,(val(float,float("1.5")),(bad,()))).

phase_request(type_check,true).

variable_declare(x,fromFacts).
variable_domain(x,val(float,float("2.5"))).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(gt,(variable(x),(val(float,float("1.5")),()))).
evaluate(gt,(variable(x),(val(none,none),()))).
evaluate(gt,(variable(x),(bad,()))).

