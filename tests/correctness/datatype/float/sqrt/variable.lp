variable_declare(x,fromFacts).
variable_domain(x,val(float,float("4.0"))).
variable_domain(x,bad).

variable_declare(y,definition).
variable_define(y,operation(sqrt,(variable(x),()))).
