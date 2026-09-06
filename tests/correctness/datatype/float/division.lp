%%% float division equality/inequality checks
variable_define(x,val(float,float("5"))).
variable_define(y,val(float,float("2.5"))).
variable_define(z,val(float,float("2"))).

evaluate(operation(eq,(variable(y),(operation(float_div,(variable(x),(variable(z),()))),())))).
evaluate(operation(eq,(variable(z),(operation(float_div,(variable(x),(variable(y),()))),())))).
evaluate(operation(neq,(variable(z),(operation(float_div,(variable(x),(variable(z),()))),())))).
evaluate(operation(neq,(variable(y),(operation(float_div,(variable(x),(variable(y),()))),())))).
