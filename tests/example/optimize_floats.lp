#include "includeAll.lp".

capacity(6).
item(a,4,float("5")).
item(b,3,float("3.12")).
item(c,3,float("3.11")).
item(d,3,float("3.1")).
item(e,3,float("3")).

optimize_precision(val(int,10)).

multimap_declare(dummy,taken).
{ multimap_assign(dummy,taken,val(symbol,X),val(int,W)) } :- item(X,W,V).

optimize_maximizeSum(dummy_opt,EXPR,X) :- item(X,W,V),
  ITEM = val(symbol,X),
  COND = operation(isin,(ITEM,(variable(taken),()))),
  VALU = val(float,V),
  EXPR = operation(if,(COND,(VALU,()))).

variable_define(dummy,carried,EXPR) :-
  EXPR = operation(multimap_fold,(LAMB,(MAP,(STAR,())))),
  MAP  = variable(taken),
  ACCU = variable(accu),
  STAR = val(int,0),
  VARS = (w,(accu,())),
  WEIG = variable(w),
  PLUS = operation(add,(WEIG,(ACCU,()))),
  LAMB = lambda(VARS,PLUS).

ensure(dummy,operation(leq,(variable(carried),(val(int,C),())))) :- capacity(C).

evaluate(isin,(val(symbol,a),(variable(taken),()))).
evaluate(isin,(val(symbol,b),(variable(taken),()))).
evaluate(isin,(val(symbol,c),(variable(taken),()))).
evaluate(isin,(val(symbol,d),(variable(taken),()))).
evaluate(isin,(val(symbol,e),(variable(taken),()))).
