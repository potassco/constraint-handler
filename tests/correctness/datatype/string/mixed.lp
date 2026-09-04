%% x = "foo" or "bar"
%% y = "bla" or "bar" or "foobar"

%% f = x == y
%% g = x != y

%%% All:
%%% |x| = 3
%%% f != g
%%% y + x == "barfoo" | |y| == |x| | y == "foobar" | y + y == "blabla"

variable_declare(x,fromFacts).
variable_domain(x,val(string,("foo";"bar"))).
variable_declare(y,fromFacts).
variable_domain(y,val(string,("bla";"bar";"foobar"))).

variable_define(f,operation(eq,(variable(x),(variable(y),())))).
variable_define(g,operation(neq,(variable(x),(variable(y),())))).

evaluate(operation(neq,(variable(f),(variable(g),())))).
evaluate(operation(length,(variable(x),()))).
evaluate(operation(disj,(operation(eq,(operation(concat,(variable(y),(variable(x),()))),(val(string,"barfoo"),()))),(operation(eq,(variable(x),(variable(y),()))),(operation(eq,(variable(y),(val(string,"foobar"),()))),(operation(eq,(operation(concat,(variable(y),(variable(y),()))),(val(string,"blabla"),()))),())))))).
