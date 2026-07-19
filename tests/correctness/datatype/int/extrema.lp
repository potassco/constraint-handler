variable_define(two,val(int,2)).
variable_define(ten,val(int,10)).

evaluate(max,(variable(two),(variable(ten),()))).
evaluate(min,(variable(two),(variable(ten),()))).
