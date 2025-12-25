#include "includeAll.lp".

%%% x = 5.0     y = 2.5     z = 2.
%%% y == x / z = true
%%% z == x / y = true
%%% z != x / z = true
%%% y != x / y = true

variable_define(a_float, x, val(float,float("5"))).
variable_define(a_float, y, val(float,float("2.5"))).
variable_define(a_float, z, val(float,float("2"))).

evaluate(eq,(variable(y),(operation(fdiv,(variable(x),(variable(z),()))),()))).
evaluate(eq,(variable(z),(operation(fdiv,(variable(x),(variable(y),()))),()))).
evaluate(neq,(variable(z),(operation(fdiv,(variable(x),(variable(z),()))),()))).
evaluate(neq,(variable(y),(operation(fdiv,(variable(x),(variable(y),()))),()))).

evaluate(python("int"),(variable(y),())).
