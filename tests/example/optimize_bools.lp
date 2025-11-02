#include "includeAll.lp".

capacity(6).
item(a,4).
item(b,3).
item(c,3).

multimap_declare(dummy,taken).
{ multimap_assign(dummy,taken,val(symbol,X),val(int,W)) } :- item(X,W).

optimize_maximizeSum(dummy_opt,EXPR,X) :- item(X,W),
  ITEM = val(symbol,X),
  EXPR = operation(isin,(ITEM,(variable(taken),()))).

assign(dummy,carried,EXPR) :-
  EXPR = operation(fold,(LAMB,(MAP,(STAR,())))),
  MAP  = variable(taken),
  ACCU = variable(accu),
  STAR = val(int,0),
  VARS = (w,(accu,())),
  WEIG = variable(w),
  PLUS = operation(add,(WEIG,(ACCU,()))),
  LAMB = lambda(VARS,PLUS).

ensure(dummy,operation(leq,(variable(carried),(val(int,C),())))) :- capacity(C).
