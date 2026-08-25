phase_request(constantFolding,false).

variable_declare(x,fromFacts).
variable_domain(x,val(float,float("-1.5"))).
variable_domain(x,val(float,float("3.7"))).
variable_domain(x,val(float,float("4.0"))).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(abs,(variable(x),())).
