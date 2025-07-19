% Collect variables involved in cyclic dependencies.

cs__cycle(X, Y) :- cs__depend(X,Y), cs__depend(Y,X).
cs_cycle_involved(X, Y) :- cs__cycle(X, Y), cs__cycle(Y, X), X < Y, not cs_cycle_involved(_,X).

#show cs__cycle/2.
#show cs_cycle_involved/2.