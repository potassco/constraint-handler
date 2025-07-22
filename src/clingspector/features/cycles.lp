% Collect information about cyclic dependencies.

% if a variable depends on itself or on another variable that depends on it,
% then there is a cycle
cs__cycle(X, Y) :- cs__depend(X,Y), cs__depend(Y,X).

% Deduplicate cycles to avoid displaying the same cycle multiple times
cs__cycle_deduplicated(X, Y) :- cs__cycle(X, Y), cs__cycle(Y, X), X < Y, not cs__cycle_deduplicated(_,X).

% Collect involved variables in order
cs__cycle_order(X, Y, N) :- cs__cycle_deduplicated(X, Y), #count{Z : cs__cycle_deduplicated(X, Z), Z < Y} = N.

% Prepare lists of involved variables
cs__cycle_dependeny_lists(X,(X, ()), 0) :- cs__cycle_deduplicated(X,_).
cs__cycle_dependeny_lists(X,(Y, Z), N+1) :- cs__cycle_dependeny_lists(X,Z, N), cs__cycle_order(X, Y, N).

% Special case: A variable directly depends on itself
cs__cycle_dependeny_lists(X,(X, ()), 0) :- cs__cycle(X, X), #count {Z: cs__cycle(X, Z)} = 1.

% Only get the largest list
cs_cyclic_dependency(X,Z) :- cs__cycle_dependeny_lists(X,Z, N), not cs__cycle_dependeny_lists(X,_, N+1).

#show cs_cyclic_dependency/2.