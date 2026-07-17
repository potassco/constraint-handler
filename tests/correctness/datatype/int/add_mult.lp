variable_define(x,val(int,20)).
variable_define(two,val(int,2)).
variable_define(ten,val(int,10)).

evaluate(add,(variable(x),(val(int,10),()))).
evaluate(add,()).
evaluate(add,(variable(ten),())).
evaluate(add,(variable(two),(variable(ten),()))).
evaluate(add,(variable(ten),(variable(two),()))).
evaluate(add,(variable(ten),(variable(two),(variable(two),(variable(ten),()))))).

evaluate(mult,()).
evaluate(mult,(variable(ten),())).
evaluate(mult,(variable(two),(variable(ten),()))).
evaluate(mult,(variable(ten),(variable(two),()))).
evaluate(mult,(variable(ten),(variable(two),(variable(two),(variable(ten),()))))).