variable_define(x,val(int,20)).
variable_define(two,val(int,2)).
variable_define(ten,val(int,10)).

evaluate(operation(mult,())).
evaluate(operation(mult,(val(int,-3),()))).
evaluate(operation(mult,(val(bool,true),()))).
evaluate(operation(mult,(val(bool,false),()))).
evaluate(operation(mult,(val(int,3),(val(int,2),(val(int,4),()))))).
evaluate(operation(mult,(val(int,10),(val(int,2),(val(int,10),(val(int,10),())))))).
evaluate(operation(mult,(val(int,-3),(val(int,2),(val(bool,true),()))))).
