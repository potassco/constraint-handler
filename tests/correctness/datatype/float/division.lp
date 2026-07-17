variable_define(x,val(float,float("5"))).
variable_define(y,val(float,float("2.5"))).
variable_define(z,val(float,float("2"))).

evaluate(eq,(variable(y),(operation(float_div,(variable(x),(variable(z),()))),()))).
evaluate(eq,(variable(z),(operation(float_div,(variable(x),(variable(y),()))),()))).
evaluate(neq,(variable(z),(operation(float_div,(variable(x),(variable(z),()))),()))).
evaluate(neq,(variable(y),(operation(float_div,(variable(x),(variable(y),()))),()))).
