%%% v1, v2, ... v4 in { 0, ... 9 }
%%% y = max(v4,max(v3,max(v2,v1) ))

digits(10).
domain(0..D-1) :- digits(D).
maxDepth(4).
depth(1..K) :- maxDepth(K).
var(v(K)) :- depth(K).
variable_declare(def(V),V,fromFacts) :- var(V).
variable_domain(V,val(int,I)) :- var(V), domain(I).

expr(1,variable(v(1))).
expr(K+1,NE) :- expr(K,E), depth(K+1), digits(D),
                NE=operation(max,(variable(v(K+1)),(E,()))).

variable_define(assign_y, y, E) :- expr(K,E), maxDepth(K).

requestEngine(assign_y,compile).
%requestEngine(assign_y,ground).
#show value/3.

%%% e1 = max(v2,v1) { 0, ... 9 }
%%% e2 = max(v3,e1) { 0, ... 9 }
%%% e3 = max(v4,e2) { 0, ... 9 }
