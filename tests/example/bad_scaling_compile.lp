#include "includeAll.lp".

%%% x in { 0,1, ... 9 }
%%% y = x+10(x+10(x+...))   with K occurrences of x if maxDepth(K).

digits(10).
domain(0..D-1) :- digits(D).
maxDepth(5).
depth(1..K) :- maxDepth(K).

variable_declare(assign_x,x,fromFacts).
variable_domain(x,val(int,I)) :- domain(I).

expr(1,variable(x)).
expr(K+1,NE) :- expr(K,E), depth(K+1), digits(D),
                NE=operation(add,(variable(x),(DE,()))),
                DE=operation(mult,(val(int,D),(E,()))).

variable_define(assign_y, y, E) :- expr(K,E), maxDepth(K).

requestEngine(assign_x,ground).
requestEngine(assign_y,ground).
%requestEngine(assign_y,ground).
#show value/3.

%%% the grounding of the compile engine scales exponentially in maxDepth
%%% the reason is that the correlation between multiple occurrences of x
%%% in different subexpressions is lost so the domain considered for
%%% subexpressions is unreasonably large.
%%% e1 = x     { 0, ,9 }
%%% e2 = 10e1 { 0, 10, 20, .. 90 }
%%% e3 = x+e2 { 0, 1, ... 9, 10, 11, ... 99 }
%%% e4 = 10e3
%%% e5 = x+e4 { 0, 1, ... 9, 10, 11, ... 999 }
%%% y = e5
