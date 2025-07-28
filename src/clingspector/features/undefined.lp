% Collect variables that are used but not defined.

cs_undefined_dependency(X,Y) :- cs__depend(X,Y), not cs__defined(Y).
cs_undefined_assignment(X) :- set_assign(_,X,_), not cs__defined(X).

#show cs_undefined_dependency/2.
#show cs_undefined_assignment/1.
