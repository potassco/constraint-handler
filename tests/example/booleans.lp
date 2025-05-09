#include "includeAll.lp".

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


1 { assign(a_x,x,constant(bool(false))) ; assign(a_x,x,constant(bool(true))) } 1.
1 { assign(a_y,y,constant(bool(false))) ; assign(a_y,y,constant(bool(true))) } 1.
assign(a_f,f,
    operation(conj,
             (operation(disj,(PX,(PY,()))),
             (operation(disj,(NX,(NY,()))),
             (operation(disj,(NX,(PY,()))),()))))) :-
    PX = variable(x),
    PY = variable(y),
    NX = operation(lnot,(PX,())),
    NY = operation(lnot,(PY,())).

assign(a_t,t,operation(lxor,(variable(x),(variable(y),())))).
assign(a_z,z,operation(ite,(variable(x),(variable(y),(operation(lnot,(variable(y),())),()))))).

evaluate(limp,(variable(f),(operation(lnot,(variable(x),())),()))).
evaluate(leqv,(variable(f),(operation(conj,(operation(lnot,(variable(x),())),(variable(y),()))),()))).
evaluate(eq,(variable(z),(operation(leqv,(variable(x),(variable(y),()))),()))).
evaluate(neq,(variable(z),(variable(t),()))).
evaluate(limp,(variable(f),(operation(lnot,(variable(y),())),()))).
evaluate(conj,(operation(limp,(variable(f),(operation(lnot,(variable(y),())),()))),(variable(f),()))).
