evaluate(leqv,()).
evaluate(leqv,(val(bool,true),())).
evaluate(leqv,(val(bool,false),())).
evaluate(leqv,(val(bool,true),(val(bool,true),(val(bool,true),())))).
evaluate(leqv,(val(bool,true),(val(bool,false),(val(bool,true),())))).
evaluate(leqv,(val(bool,false),(val(bool,false),(val(bool,false),())))).

evaluate(lxor,()).
evaluate(lxor,(val(bool,true),())).
evaluate(lxor,(val(bool,false),())).
evaluate(lxor,(val(bool,true),(val(bool,true),(val(bool,true),())))).
evaluate(lxor,(val(bool,true),(val(bool,false),(val(bool,true),())))).
evaluate(lxor,(val(bool,false),(val(bool,false),(val(bool,false),())))).
