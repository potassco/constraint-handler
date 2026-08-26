phase_request(constantFolding,false).

variable_define(x,val(int,20)).
variable_define(two,val(int,2)).
variable_define(ten,val(int,10)).

evaluate(mult,()).
evaluate(mult,(val(int,-3),())).
evaluate(mult,(val(bool,true),())).
evaluate(mult,(val(bool,false),())).
evaluate(mult,(val(int,3),(val(int,2),(val(int,4),())))).
evaluate(mult,(val(int,10),(val(int,2),(val(int,10),(val(int,10),()))))).
evaluate(mult,(val(int,-3),(val(int,2),(val(bool,true),())))).
