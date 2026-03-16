% Regression: eq/neq where one side is a compound int expression
% Ensures generic equality does not depend on type inference.

variable_define(d,x,val(int,2)).
variable_define(d,y,operation(mult,(variable(x),(val(int,2),())))).

variable_define(d,eq_ok,operation(eq,(variable(y),(val(int,4),())))).
variable_define(d,neq_ok,operation(neq,(variable(y),(val(int,4),())))).
