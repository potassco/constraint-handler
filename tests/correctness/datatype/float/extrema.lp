%%% float min/max checks
variable_define(x,val(float,float("5"))).
variable_define(y,val(float,float("2.5"))).

evaluate(operation(max,(variable(x),(variable(y),())))).
evaluate(operation(min,(variable(x),(variable(y),())))).
