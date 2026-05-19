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

multimap_declare(taken).
{ multimap_assign(taken,val(symbol,X),val(int,W)) } :- item(X,W,PROFIT,BONUS).

% Maximize total profit under the explicit label profit.
optimize_maximizeSum(profit,EXPR,X,1) :- item(X,W,PROFIT,BONUS),
  ITEM = val(symbol,X),
  COND = operation(multimap_isin,(ITEM,(variable(taken),()))),
  VALU = val(float,PROFIT),
  EXPR = operation(if,(COND,(VALU,()))).

% Maximize a second float-valued bonus label on the same priority.
optimize_maximizeSum(bonus,EXPR,X,1) :- item(X,W,PROFIT,BONUS),
  ITEM = val(symbol,X),
  COND = operation(multimap_isin,(ITEM,(variable(taken),()))),
  VALU = val(float,BONUS),
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
