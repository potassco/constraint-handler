% Test case for optimization result output with explicit labels.
% Both labels use the same priority so the postprocessor has to emit two
% optimize_value atoms for one priority level.
% The optimum selects two items, so both labeled totals are real sums.

capacity(11).
item(a,6,float("4.5"),float("0.5")).
item(b,3,float("3.0"),float("0.25")).
item(c,4,float("4.0"),float("0.25")).
item(d,5,float("4.0"),float("0.0")).

optimize_precision(val(int,100),1).

variable_declare(take(X),boolDomain) :- item(X,W,V,B).

% Maximize total profit under the explicit label profit.
optimize_maximizeSum(profit,EXPR,X,1) :- item(X,W,V,B), EXPR=operation(if,(variable(take(X)),(val(float,V),()))).
% Maximize a second float-valued bonus label on the same priority.
optimize_maximizeSum(bonus,EXPR,X,1) :- item(X,W,V,B), EXPR=operation(if,(variable(take(X)),(val(float,B),()))).

item_idx(IDX,X,W) :- item(X,W,V,B), IDX = #count { Y : item(Y,Z,V2,B2), Y < X }.
weight_list_aux(N,()) :- N = #count { Y : item(Y,Z,V,B) }.
weight_list_aux(IDX,(EXPR,L)) :- weight_list_aux(IDX+1,L), item_idx(IDX,X,W), EXPR = operation(ite,(variable(take(X)),(val(int,W),(val(int,0),())))).
carried_weight(operation(add,L)) :- weight_list_aux(0,L).

ensure(operation(leq,(W,(val(int,C),())))) :- capacity(C), carried_weight(W).
