capacity(6).
item(a,4,5).
item(b,2,1).
item(c,2,1).
item(d,3,3).

variable_declare(take(X),boolDomain) :- item(X,W,V).
optimize_maximizeSum(EXPR,X) :- item(X,W,V), EXPR=operation(if,(variable(take(X)),(val(int,V),()))).

item_idx(IDX,X,W) :- item(X,W,V), IDX = #count { Y : item(Y,Z,V2), Y < X }.
weight_list_aux(N,()) :- N = #count { Y : item(Y,Z,V) }.
weight_list_aux(IDX,(EXPR,L)) :- weight_list_aux(IDX+1,L), item_idx(IDX,X,W), EXPR = operation(ite,(variable(take(X)),(val(int,W),(val(int,0),())))).
carried_weight(operation(add,L)) :- weight_list_aux(0,L).

ensure(operation(leq,(W,(val(int,C),())))) :- capacity(C), carried_weight(W).
