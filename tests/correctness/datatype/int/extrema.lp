variable_define(two,val(int,2)).
variable_define(ten,val(int,10)).

evaluate(operation(max,(variable(two),(variable(ten),())))).
evaluate(operation(min,(variable(two),(variable(ten),())))).
