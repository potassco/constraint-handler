#include "includeAll.lp".

capacity(6).
item(a,4,5).
item(b,3,3).
item(c,3,3).

multimap_declare(dummy,taken).
{ multimap_assign(dummy,taken,val(symbol,X),val(int,W)) } :- item(X,W,V).

optimize_maximizeSum(dummy_opt,EXPR,X) :- item(X,W,V),
  ITEM = val(symbol,X),
  COND = operation(isin,(ITEM,(variable(taken),()))),
  VALU = val(int,V),
  EXPR = operation(if,(COND,(VALU,()))).


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
