variable_define(x,val(float,float("5"))).
variable_define(y,val(float,float("2.5"))).

evaluate(max,(variable(x),(variable(y),()))).
evaluate(min,(variable(x),(variable(y),()))).
