% This encoding is supposed to collect and define the basis for other features

% Expressions are defined in assignments and ensures
cs__expression(E) :- assign(_,X,E).
cs__expression(E) :- ensure(_,E).

% Expressions can be lists of sub-expressions
cs__expressionList(ES) :- cs__expression(E), E=operation(O,ES).
cs__expression(HEAD) :- cs__expressionList(ES), ES=(HEAD,TAIL).
cs__expressionList(TAIL) :- cs__expressionList(ES), ES=(HEAD,TAIL).

% An expression is a sub-expression 
% if it is either the head
% or a sub-expression of the tail in a list of expressions
cs__subExprs(ES,HEAD) :- cs__expressionList(ES), ES=(HEAD,TAIL).
cs__subExprs(ES,E) :- cs__expressionList(ES), ES=(HEAD,TAIL), cs__subExprs(TAIL,E).

% An expression depends on a variable
% if the expression itself uses the variable
% or if it depends on a sub-expression that depends on the variable
cs__dependExpr(E,Y) :- cs__expression(E), E=variable(Y).
cs__dependExpr(E,Y) :- cs__expression(E), E=operation(O,ES), cs__dependExpr(SUB,Y), cs__subExprs(ES,SUB).

% Variable dependency
cs__depend(X,Y) :- assign(_,X,E), cs__dependExpr(E,Y).
cs__depend(X,Y) :- cs__depend(X,Z), cs__depend(Z,Y).




