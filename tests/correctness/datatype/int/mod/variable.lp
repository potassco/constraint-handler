variable_declare(x,fromFacts).
variable_domain(x,val(int,7)).
variable_domain(x,val(int,8)).

variable_declare(y,definition).
variable_define(y,operation(mod,(variable(x),(val(int,3),())))).
