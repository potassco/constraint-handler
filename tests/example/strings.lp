#include "includeAll.lp".

%% x = "foo" or "bar"
%% y = "bla" or "bar" or "foobar"

%% f = x == y
%% g = x != y

%%% All:
%%% |x| = 3
%%% f != g
%%% y + x == "barfoo" | |y| == |x| | y == "foobar" | y + y == "blabla"

1 { assign(a_x,x,val(str,"foo")) ; assign(a_x,x,val(str,"bar")) } 1.
1 { assign(a_y,y,val(str,"bla")) ; assign(a_y,y,val(str,"bar")) ; assign(a_y, y, val(str,"foobar")) } 1.
assign(a_f,f,operation(eq,(variable(x),(variable(y),())))).
assign(a_g,g,operation(neq,(variable(x),(variable(y),())))).

evaluate(neq,(variable(f),(variable(g),()))).
evaluate(length,(variable(x),())).
evaluate(disj,(operation(eq,(operation(concat,(variable(y),(variable(x),()))),(val(str,"barfoo"),()))),(operation(eq,(variable(x),(variable(y),()))),(operation(eq,(variable(y),(val(str,"foobar"),()))),(operation(eq,(operation(concat,(variable(y),(variable(y),()))),(val(str,"blabla"),()))),()))))).

assign(a_yy,yy,operation(add,(variable(y),(variable(y),())))).
