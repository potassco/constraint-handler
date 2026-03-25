capacity(6).
item(a,4).
item(b,3).
item(c,3).

multimap_declare(taken).
{ multimap_assign(taken,val(symbol,X),val(int,W)) } :- item(X,W).

optimize_maximizeSum(EXPR,X,0) :- item(X,W),
  ITEM = val(symbol,X),
  EXPR = operation(isin,(ITEM,(variable(taken),()))).

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
