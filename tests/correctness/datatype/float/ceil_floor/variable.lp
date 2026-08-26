phase_request(constantFolding,false).

variable_declare(x,fromFacts).
variable_domain(x,val(float,float("1.5"))).
variable_domain(x,val(float,float("2.5"))).
variable_domain(x,val(int,7)).
variable_domain(x,val(none,none)).
variable_domain(x,bad).
evaluate(ceil,(variable(x),())).
evaluate(floor,(variable(x),())).
