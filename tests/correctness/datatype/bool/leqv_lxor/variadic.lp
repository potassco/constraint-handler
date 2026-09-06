evaluate(operation(leqv,())).
evaluate(operation(leqv,(val(bool,true),()))).
evaluate(operation(leqv,(val(bool,false),()))).
evaluate(operation(leqv,(val(bool,true),(val(bool,true),(val(bool,true),()))))).
evaluate(operation(leqv,(val(bool,true),(val(bool,false),(val(bool,true),()))))).
evaluate(operation(leqv,(val(bool,false),(val(bool,false),(val(bool,false),()))))).

evaluate(operation(lxor,())).
evaluate(operation(lxor,(val(bool,true),()))).
evaluate(operation(lxor,(val(bool,false),()))).
evaluate(operation(lxor,(val(bool,true),(val(bool,true),(val(bool,true),()))))).
evaluate(operation(lxor,(val(bool,true),(val(bool,false),(val(bool,true),()))))).
evaluate(operation(lxor,(val(bool,false),(val(bool,false),(val(bool,false),()))))).
