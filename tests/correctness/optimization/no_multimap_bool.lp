capacity(7).
item(a,5).
item(b,4).
item(c,3).
item(d,3).

variable_declare(take(X),boolDomain) :- item(X,W).
optimize_maximizeSum(variable(take(X)),X) :- item(X,W).

item_idx(IDX,X,W) :- item(X,W), IDX = #count { Y : item(Y,Z), Y < X }.
weight_list_aux(N,()) :- N = #count { Y : item(Y,Z) }.
weight_list_aux(IDX,(EXPR,L)) :- weight_list_aux(IDX+1,L), item_idx(IDX,X,W), EXPR = operation(ite,(variable(take(X)),(val(int,W),(val(int,0),())))).
carried_weight(operation(add,L)) :- weight_list_aux(0,L).

ensure(operation(leq,(W,(val(int,C),())))) :- capacity(C), carried_weight(W).
