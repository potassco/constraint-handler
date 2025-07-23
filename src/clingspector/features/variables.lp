% Collect variables that are used but not defined.

% A variable is defined if it has an assignment
cs__defined(X) :- assign(_,X,E).

% A variable is undefined if it is used but not defined
cs_undefined_variable(X,Y) :- cs__depend(X,Y), not cs__defined(Y).

#show cs_undefined_variable/2.
