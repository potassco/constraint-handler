capacity(6).
item(a,4,5).
item(b,2,1).
item(c,2,1).
item(d,3,3).
multimap_declare(taken).
{ multimap_assign(taken,val(symbol,X),val(int,W)) } :- item(X,W,V).

optimize_maximizeSum(EXPR,X) :- item(X,W,V),
  ITEM = val(symbol,X),
  COND = operation(multimap_isin,(ITEM,(variable(taken),()))),
  VALU = val(int,V),
  EXPR = operation(if,(COND,(VALU,()))).


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
