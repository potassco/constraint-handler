%%% x = 5.0     y = 2.5     z = 2.
%%% y == x / z = true
%%% z == x / y = true
%%% z != x / z = true
%%% y != x / y = true

%%% x // z = 2
%%% x // y = 2
%%% x // 2 = 2
%%% 5 // z = 2
%%% 5 // y = 2

variable_define(a_float, x, val(float,float("5"))).
variable_define(a_float, y, val(float,float("2.5"))).
variable_define(a_float, z, val(float,float("2"))).

evaluate(eq,(variable(y),(operation(float_div,(variable(x),(variable(z),()))),()))).
evaluate(eq,(variable(z),(operation(float_div,(variable(x),(variable(y),()))),()))).
evaluate(neq,(variable(z),(operation(float_div,(variable(x),(variable(z),()))),()))).
evaluate(neq,(variable(y),(operation(float_div,(variable(x),(variable(y),()))),()))).

evaluate(int_div,(variable(x),(variable(z),()))).
evaluate(int_div,(variable(x),(variable(y),()))).
evaluate(int_div,(variable(x),(val(int,2),()))).
evaluate(int_div,(val(int,5),(variable(z),()))).
evaluate(int_div,(val(int,5),(variable(y),()))).

evaluate(max,(variable(x), (variable(y),()))).
evaluate(min,(variable(x), (variable(y),()))).

evaluate(python("int"),(variable(y),())).
