capacity(7).
item(a,5).
item(b,4).
item(c,3).
item(d,3).

multimap_declare(taken).
{ multimap_assign(taken,val(symbol,X),val(int,W)) } :- item(X,W).

optimize_maximizeSum(EXPR,X) :- item(X,W),
  ITEM = val(symbol,X),
  EXPR = operation(multimap_isin,(ITEM,(variable(taken),()))).

variable_define(carried,EXPR) :-
  EXPR = operation(multimap_fold,(LAMB,(MAP,(STAR,())))),
  MAP  = variable(taken),
  ACCU = variable(accu),
  STAR = val(int,0),
  VARS = (w,(accu,())),
  WEIG = variable(w),
  PLUS = operation(add,(WEIG,(ACCU,()))),
  LAMB = lambda(VARS,PLUS).

ensure(operation(leq,(variable(carried),(val(int,C),())))) :- capacity(C).
