% Collect variables that are used but not defined.

% A variable is undefined if it is used but not defined
cs_undefined_variable(X,Y) :- cs__depend(X,Y), not cs__defined(Y).
cs__assign_undefined(X) :- set_assign(_,X,_), not cs__defined(X).

#show cs_undefined_variable/2.
