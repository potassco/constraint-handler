variable_declare((x;y;z),fromFacts).
variable_domain(x,val(int,(2;20))).
variable_domain(y,val(int,(3;300))).
variable_domain(z,val(int,(5;500))).

variable_define(s,operation(mult,(variable(x),(variable(y),(variable(z),()))))).
ensure(operation(geq,(variable(s),(val(int,60000),())))).
