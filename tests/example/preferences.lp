#include "includeAll.lp".

preference_maximizeScore.

label(a;b).
word("over";"take").
variable_declare(dummy,X,fromFacts) :- label(X).
variable_domain(X,val(str,W)) :- label(X), word(W).
variable_define(dummy,compound,STR) :- STR = operation(concat,(variable(a),(variable(b),()))).

preference_holds(dummy,operation(neq,(variable(a),(variable(b),())))).

evaluate(disj,(operation(eq,(variable(compound),(val(str,"takeover"),()))),(operation(eq,(variable(compound),(val(str,"overtake"),()))),()))).

%preference_variable(compound,val(str,"overover"),12).
%preference_variable(compound,val(str,"taketake"),100).
%preference_variable(compound,val(str,"helloworld"),20).

variable_declare(dummy,X,fromFacts) :- vertex(X).
variable_domain(X,val(symbol,C)) :- vertex(X), color(C).
ensure(dummy,operation(neq,(variable(X),(variable(Y),())))) :- edge(X,Y).

color(red;green;blue).
vertex(x0;y0;z0;t0).
edge(x0,y0).
edge(x0,z0).
edge(x0,t0).

preference_variable(x0,val(symbol,red),5).
preference_variable(y0,val(symbol,red)).
preference_variable(z0,val(symbol,red)).
preference_variable(t0,val(symbol,red)).

vertex(x1;y1;z1;t1).
edge(x1,y1).
edge(x1,z1).
edge(x1,t1).

preference_variable(x1,val(symbol,red),2).
preference_variable(y1,val(symbol,red),1).
preference_variable(z1,val(symbol,red),1).
preference_variable(t1,val(symbol,red)).

vertex(x2;y2;z2;t2).
edge(x2,y2).
edge(x2,z2).
edge(x2,t2).

preference_variable(x2,val(symbol,red),2).
preference_variable(y2,val(symbol,red),1).
preference_variable(z2,val(symbol,red),1).
preference_variable(t2,val(symbol,red),-1).


number(p;q).
smallInt(1..4).
variable_declare(dummy,X,fromFacts) :- number(X).
variable_domain(X,val(int,N)) :- number(X), smallInt(N).
ensure(dummy,operation(neq,(variable(p),(variable(q),())))).

preference_holds(dummy,operation(leq,(variable(p),(variable(q),()))),10).
preference_variable(p,val(int,3),3).
preference_variable(p,val(int,2),2).
preference_variable(q,val(int,N),N) :- smallInt(N).


#show evaluated/4.
#show value/3.
#show preference_score/1.
