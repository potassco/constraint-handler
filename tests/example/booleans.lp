#include "includeAll.lp".

%% x = true or false
%% y = true or false
%% a = false or nothing
%% b = true or nothing


%% f = (x | y) & (-x | -y) & (-x | y)
%% t = x xor y
%% z = if x then y else -y

%%% any:
%%% x     not x     y     not y     f     not f     t     not t     z     not z
%%% f->-y     -(f->-y)
%%% snot a == true   snot a == false
%%% wnot b == true   wnot b == false

%%% all:
%%% f->-x
%%% f<->-x&y
%%% z==(x<->y)
%%% z!=t
%%% not (f->-y)&f)
%%% snot b == false
%%% not (snot b) == true
%%% wnot a == true

1 { assign(a_x,x,val(bool,false)) ; assign(a_x,x,val(bool,true)) } 1.
1 { assign(a_y,y,val(bool,false)) ; assign(a_y,y,val(bool,true)) } 1.
{ assign(a_a,a,val(bool,false)) }.
{ assign(a_b,b,val(bool,true))  }.
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
evaluate(snot,(variable(a),())).
evaluate(snot,(variable(b),())).
evaluate(lnot,(operation(snot,(variable(b),())),())).
evaluate(wnot,(variable(a),())).
evaluate(wnot,(variable(b),())).
