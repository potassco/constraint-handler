variable_declare(x,fromFacts).
variable_domain(x,(val(int,1);val(int,2))).
variable_define(y,val(int,4),operation(eq,(variable(x),(val(int,1),())))).
variable_define(y,val(int,3),operation(eq,(variable(x),(val(int,2),())))).
variable_define(z,operation(add,(variable(x),(variable(y),())))).
variable_define(t,val(int,10),operation(neq,(variable(z),(val(int,5),())))).
