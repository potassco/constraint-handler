variable_define(x,val(float,float("5"))).
variable_define(y,val(float,float("2.5"))).
variable_define(z,val(float,float("2"))).

evaluate(int_div,(variable(x),(variable(z),()))).
evaluate(int_div,(variable(x),(variable(y),()))).
evaluate(int_div,(variable(x),(val(int,2),()))).
evaluate(int_div,(val(int,5),(variable(z),()))).
evaluate(int_div,(val(int,5),(variable(y),()))).
