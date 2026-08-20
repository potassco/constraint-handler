variable_declare((x;y;z),fromFacts).
variable_domain(x,val(int,(2;22))).
variable_domain(y,val(int,(3;33))).
variable_domain(z,val(int,(5;55))).

variable_define(s,operation(add,(variable(x),(variable(y),(variable(z),()))))).
ensure(operation(geq,(variable(s),(val(int,90),())))).
