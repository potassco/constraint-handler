%%% float equality/inequality checks against domain-derived equivalent values
variable_define(x,val(float,float("5"))).
variable_define(y,val(float,float("2.5"))).
variable_define(z,val(float,float("2"))).

variable_declare(xx,fromFacts).
variable_declare(yy,fromFacts).
variable_declare(zz,fromFacts).
variable_domain(xx,val(float,float(5))).
variable_domain(yy,val(float,float("2.5"))).
variable_domain(zz,val(float,float("2.0"))).
variable_domain(xx,operation(float_div,(val(int,10),(val(int,2),())))).
variable_domain(yy,operation(float_div,(val(int,5),(val(int,2),())))).
variable_domain(zz,operation(float_div,(val(int,10),(val(int,5),())))).


variable_define(xe,operation(eq,(variable(x),(variable(xx),())))).
variable_define(ye,operation(eq,(variable(y),(variable(yy),())))).
variable_define(ze,operation(eq,(variable(z),(variable(zz),())))).
variable_define(xn,operation(neq,(variable(x),(variable(xx),())))).
variable_define(yn,operation(neq,(variable(y),(variable(yy),())))).
variable_define(zn,operation(neq,(variable(z),(variable(zz),())))).

#show value/2.
#show warning/3.
