preference_maximizeScore.

label(a;b).
word("over";"take").
variable_declare(X,fromFacts) :- label(X).
variable_domain(X,val(str,W)) :- label(X), word(W).
variable_define(compound,STR) :- STR = operation(concat,(variable(a),(variable(b),()))).

preference_holds(operation(neq,(variable(a),(variable(b),()))),1).

evaluate(disj,(operation(eq,(variable(compound),(val(str,"takeover"),()))),(operation(eq,(variable(compound),(val(str,"overtake"),()))),()))).

variable_declare(X,fromFacts) :- vertex(X).
variable_domain(X,val(symbol,C)) :- vertex(X), color(C).
ensure(operation(neq,(variable(X),(variable(Y),())))) :- edge(X,Y).

color(red;green;blue).
vertex(x0;y0;z0;t0).
edge(x0,y0).
edge(x0,z0).
edge(x0,t0).

preference_variableValue(x0,val(symbol,red),5).
preference_variableValue(y0,val(symbol,red),1).
preference_variableValue(z0,val(symbol,red),1).
preference_variableValue(t0,val(symbol,red),1).

vertex(x1;y1;z1;t1).
edge(x1,y1).
edge(x1,z1).
edge(x1,t1).

preference_variableValue(x1,val(symbol,red),2).
preference_variableValue(y1,val(symbol,red),1).
preference_variableValue(z1,val(symbol,red),1).
preference_variableValue(t1,val(symbol,red),1).

vertex(x2;y2;z2;t2).
edge(x2,y2).
edge(x2,z2).
edge(x2,t2).

preference_variableValue(x2,val(symbol,red),3).
preference_variableValue(y2,val(symbol,red),1).
preference_variableValue(z2,val(symbol,red),1).
preference_variableValue(t2,val(symbol,red),-1).


number(p;q).
smallInt(1..4).
variable_declare(X,fromFacts) :- number(X).
variable_domain(X,val(int,N)) :- number(X), smallInt(N).
ensure(operation(neq,(variable(p),(variable(q),())))).

preference_holds(operation(leq,(variable(p),(variable(q),()))),10).
preference_variableValue(p,val(int,3),3).
preference_variableValue(p,val(int,2),2).
preference_variableValue(q,val(int,N),N) :- smallInt(N).


#show evaluated/3.
#show value/2.
#show preference_score/1.
