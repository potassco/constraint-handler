variable_define(two,val(int,2)).
variable_define(ten,val(int,10)).

evaluate(sub,(variable(two),(variable(ten),()))).
evaluate(sub,(variable(ten),(variable(two),()))).