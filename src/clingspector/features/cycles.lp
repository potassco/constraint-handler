% Collect variables involved in cyclic dependencies.
assign(1, a, variable(c)).
assign(1, b, operation(add, (variable(a), (variable(e), ())))).
assign(1, c, variable(b)).
assign(2, d, variable(b)).
assign(2, e, variable(d)).
assign(2, x, variable(y)).
assign(2, y, variable(x)).

assign(2, k, variable(o)).
assign(2, o, variable(i)).
assign(2, i, variable(t)).
assign(2, t, variable(k)).

cs__cycle(X, Y) :- cs__depend(X,Y), cs__depend(Y,X).
cs__cycle_deduplicated(X, Y) :- cs__cycle(X, Y), cs__cycle(Y, X), X < Y, not cs__cycle_deduplicated(_,X).
cs__cycle_order(X, Y, N) :- cs__cycle_deduplicated(X, Y), #count{Z : cs__cycle_deduplicated(X, Z), Z < Y} = N.

% Prepare lists of involved variables
cs__cycle_dependeny_lists(X,(X, ()), 0) :- cs__cycle_deduplicated(X,_).
cs__cycle_dependeny_lists(X,(Y, Z), N+1) :- cs__cycle_dependeny_lists(X,Z, N), cs__cycle_order(X, Y, N).

% Only get the largest list
cs_cyclic_dependency(X,Z) :- cs__cycle_dependeny_lists(X,Z, N), not cs__cycle_dependeny_lists(X,_, N+1).

#show cs_cyclic_dependency/2.