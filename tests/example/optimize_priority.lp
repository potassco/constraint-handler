% Test case for optimization with competing priorities
% This example demonstrates multi-level optimization where priority 0 breaks ties:
% - Priority 1: Maximize total value
% - Priority 0: Minimize total weight (among solutions with same value)
%
% Items: a(weight=5,value=10), b(weight=3,value=10), c(weight=2,value=10)
% Capacity: 8 (can only take 2 items max)
%
% Multiple solutions achieve maximum value of 20:
% - Take 'a' and 'b': value=20, weight=8
% - Take 'a' and 'c': value=20, weight=7
% - Take 'b' and 'c': value=20, weight=5 (BEST - minimum weight!)
%
% Expected: Take 'b' and 'c' (value=20, weight=5)
% All three solutions have value=20, but 'b'+'c' has minimum weight

capacity(8).
item(a,5,10).
item(b,3,10).
item(c,2,10).

multimap_declare(dummy,taken).
{ multimap_assign(dummy,taken,val(symbol,X),val(int,W)) } :- item(X,W,V).

% Maximize value with priority 1 (higher priority)
optimize_maximizeSum(opt_value,EXPR,X,1) :- item(X,W,V),
  ITEM = val(symbol,X),
  COND = operation(isin,(ITEM,(variable(taken),()))),
  VALU = val(int,V),
  EXPR = operation(if,(COND,(VALU,()))).

% Minimize weight with priority 0 (lower priority) by maximizing negative weight
optimize_maximizeSum(opt_weight,EXPR,X,0) :- item(X,W,V),
  ITEM = val(symbol,X),
  COND = operation(isin,(ITEM,(variable(taken),()))),
  WGHT = val(int,-W),
  EXPR = operation(if,(COND,(WGHT,()))).

% Capacity constraint
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
