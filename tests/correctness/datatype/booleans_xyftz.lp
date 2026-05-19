%% x = true or false
%% y = true or false

%% f = (x | y) & (-x | -y) & (-x | y)
%% t = x xor y
%% z = if x then y else -y

%%% any:
%%% x     not x     y     not y     f     not f     t     not t     z     not z
%%% f->-y     -(f->-y)

%%% all:
%%% f->-x
%%% f<->-x&y
%%% z==(x<->y)
%%% z!=t
%%% not (f->-y)&f)

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

evaluate(limp,(variable(f),(operation(lnot,(variable(x),())),()))).
evaluate(leqv,(variable(f),(operation(conj,(operation(lnot,(variable(x),())),(variable(y),()))),()))).
evaluate(leqv,(val(bool,true),(val(bool,false),(val(bool,false),())))).
evaluate(leqv,(val(bool,true),(val(bool,true),(val(bool,false),())))).
evaluate(eq,(variable(z),(operation(leqv,(variable(x),(variable(y),()))),()))).
evaluate(neq,(variable(z),(variable(t),()))).
evaluate(limp,(variable(f),(operation(lnot,(variable(y),())),()))).
evaluate(conj,(operation(limp,(variable(f),(operation(lnot,(variable(y),())),()))),(variable(f),()))).