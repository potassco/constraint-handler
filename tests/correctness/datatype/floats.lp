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

%%% f0 = floor(5) f2 = floor(5.2) f6 = floor(5.6)
%%% c0 = ceil(5)  c2 = ceil(5.2)  c6 = ceil(5.6)

variable_define(x,val(float,float("5"))).
variable_define(y,val(float,float("2.5"))).
variable_define(z,val(float,float("2"))).

evaluate(eq,(variable(y),(operation(float_div,(variable(x),(variable(z),()))),()))).
evaluate(eq,(variable(z),(operation(float_div,(variable(x),(variable(y),()))),()))).
evaluate(neq,(variable(z),(operation(float_div,(variable(x),(variable(z),()))),()))).
evaluate(neq,(variable(y),(operation(float_div,(variable(x),(variable(y),()))),()))).

evaluate(int_div,(variable(x),(variable(z),()))).
evaluate(int_div,(variable(x),(variable(y),()))).
evaluate(int_div,(variable(x),(val(int,2),()))).
evaluate(int_div,(val(int,5),(variable(z),()))).
evaluate(int_div,(val(int,5),(variable(y),()))).

evaluate(max,(variable(x),(variable(y),()))).
evaluate(min,(variable(x),(variable(y),()))).

evaluate(python("int"),(variable(y),())).

variable_define(f0,operation(floor,(val(float,float("5")),()))).
variable_define(f6,operation(floor,(val(float,float("5.2")),()))).
variable_define(f2,operation(floor,(val(float,float("5.6")),()))).

variable_define(c0,operation(ceil,(val(float,float("5")),()))).
variable_define(c2,operation(ceil,(val(float,float("5.2")),()))).
variable_define(c6,operation(ceil,(val(float,float("5.6")),()))).
