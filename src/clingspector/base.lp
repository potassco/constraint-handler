% This encoding is supposed to collect and define the basis for other features

%
% Expressions
%

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

%
% Dependencies
%

% An expression depends on a variable
% if the expression itself uses the variable
% or if it depends on a sub-expression that depends on the variable
cs__dependExpr(E,Y) :- cs__expression(E), E=variable(Y).
cs__dependExpr(E,Y) :- cs__expression(E), E=operation(O,ES), cs__dependExpr(SUB,Y), cs__subExprs(ES,SUB).

% Variable dependency
cs__depend(X,Y) :- assign(_,X,E), cs__dependExpr(E,Y).
cs__depend(X,Y) :- cs__depend(X,Z), cs__depend(Z,Y).

%
% Types
%
cs__base_type(int; float; str; symbol; bool).
cs__type(T) :- cs__base_type(T).

%
% Operators
%
cs__unary_operator(abs; sqrt; cos; sin; tan; acos; asin; atan; minus).
cs__logic_operator(conj; disj; ite; leqv; limp; lnot; lxor).
cs__comparison_operator(eq; neq; leq; lt; geq; gt).
cs__binary_operator(add; sub; mult; div; pow).
cs__set_operator(makeSet; isin; notin; union; inter; subset).
cs__other_operator(minus; max; min; length; concat).

cs__operator(O) :- cs__unary_operator(O).
cs__operator(O) :- cs__logic_operator(O).
cs__operator(O) :- cs__binary_operator(O).
cs__operator(O) :- cs__set_operator(O).
cs__operator(O) :- cs__other_operator(O).

%
% Operations
%

% Valid operations for bools
cs__valid_operation(lnot, (bool, ()), bool).
cs__valid_operation(eq;neq, (bool, (bool, ())), bool).
cs__valid_operation(O, (bool, (bool, ())), bool) :- cs__logic_operator(O), O != (lnot, ite).

% Valid operations for ints
cs__valid_operation(max;min;abs;minus, (int, ()), int).
cs__valid_operation(O, (int, (int, ())), int) :- cs__binary_operator(O).
cs__valid_operation(O, (int, (int, ())), bool) :- cs__comparison_operator(O).

% Valid operations for floats
cs__valid_operation(O, (float, ()), float) :- cs__unary_operator(O).
cs__valid_operation(O, (float, (float, ())), float) :- cs__binary_operator(O).
cs__valid_operation(O, (float, (float, ())), bool) :- cs__comparison_operator(O).

% Valid operations for str
cs__valid_operation(eq;neq, (str, ()), bool).
cs__valid_operation(length, (str, ()), int).
cs__valid_operation(concat, (str, (str, ())), str).