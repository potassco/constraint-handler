phase_request(constantFolding,false).

evaluate(add,()).
variable_define(two,val(int,2)).
variable_define(ten,val(int,10)).
evaluate(add,(variable(ten),())).
evaluate(add,(val(int,20),())).
evaluate(add,(val(int,-3),())).
evaluate(add,(val(bool,true),())).
evaluate(add,(val(none,none),())).
evaluate(add,(bad,())).
evaluate(add,(variable(two),(variable(ten),()))).
evaluate(add,(variable(ten),(variable(two),(val(int,2),(variable(ten),()))))).
evaluate(add,(val(int,-3),(val(int,2),(val(bool,true),())))).
