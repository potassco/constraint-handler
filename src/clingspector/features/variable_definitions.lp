% Collect variables that are used but not defined.

cs__defined(X) :- assign(_,X,E).
cs_suspicious_depend(X,Y) :- cs__depend(X,Y), not cs__defined(Y).

#show cs_suspicious_depend/2.