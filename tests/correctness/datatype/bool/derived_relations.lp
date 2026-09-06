%%% boolean derived relation checks over x/y/f/t/z

variable_declare(x,boolDomain).
variable_declare(y,boolDomain).

variable_define(f,
    operation(conj,
             (operation(disj,(PX,(PY,()))),
             (operation(disj,(NX,(NY,()))),
             (operation(disj,(NX,(PY,()))),()))))) :-
    PX = variable(x),
    PY = variable(y),
    NX = operation(lnot,(PX,())),
    NY = operation(lnot,(PY,())).

variable_define(t,operation(lxor,(variable(x),(variable(y),())))).
variable_define(z,operation(ite,(variable(x),(variable(y),(operation(lnot,(variable(y),())),()))))).

evaluate(operation(limp,(variable(f),(operation(lnot,(variable(x),())),())))).
evaluate(operation(leqv,(variable(f),(operation(conj,(operation(lnot,(variable(x),())),(variable(y),()))),())))).
evaluate(operation(leqv,(val(bool,true),(val(bool,false),(val(bool,false),()))))).
evaluate(operation(leqv,(val(bool,true),(val(bool,true),(val(bool,false),()))))).
evaluate(operation(eq,(variable(z),(operation(leqv,(variable(x),(variable(y),()))),())))).
evaluate(operation(neq,(variable(z),(variable(t),())))).
evaluate(operation(limp,(variable(f),(operation(lnot,(variable(y),())),())))).
evaluate(operation(conj,(operation(limp,(variable(f),(operation(lnot,(variable(y),())),()))),(variable(f),())))).
