#include "includeAll.lp".

%% x = "foo" or "bar"
%% y = "bla" or "bar" or "foobar"

%% f = x == y
%% g = x != y

%%% All:
%%% |x| = 3
%%% f != g
%%% y + x == "barfoo" | |y| == |x| | y == "foobar" | y + y == "blabla"

variable_declare(a_x,x,fromFacts).
variable_domain(x,val(str,("foo";"bar"))).
variable_declare(a_y,y,fromFacts).
variable_domain(y,val(str,("bla";"bar";"foobar"))).

variable_define(a_f,f,operation(eq,(variable(x),(variable(y),())))).
variable_define(a_g,g,operation(neq,(variable(x),(variable(y),())))).

evaluate(neq,(variable(f),(variable(g),()))).
evaluate(length,(variable(x),())).
evaluate(disj,(operation(eq,(operation(concat,(variable(y),(variable(x),()))),(val(str,"barfoo"),()))),(operation(eq,(variable(x),(variable(y),()))),(operation(eq,(variable(y),(val(str,"foobar"),()))),(operation(eq,(operation(concat,(variable(y),(variable(y),()))),(val(str,"blabla"),()))),()))))).
