% Test case for optimization with competing priorities
% This example demonstrates multi-level optimization where priority 0 breaks ties:
% - Priority 1: Maximize total value
% - Priority 0: Minimize total weight (among solutions with same value)
%
% Items: a(weight=6,value=12), b(weight=3,value=10), c(weight=4,value=11), d(weight=5,value=11)
% Capacity: 11 (can only take 2 items max)
%
% Multiple feasible solutions:
% - Take 'a' and 'b': value=22, weight= 9
% - Take 'a' and 'c': value=23, weight=10
% - Take 'a' and 'd': value=23, weight=11
% - Take 'b' and 'c': value=21, weight= 7
% - Take 'b' and 'd': value=21, weight= 8
% - Take 'c' and 'd': value=22, weight= 9
% - All the single-item or zero-item solutions.
%
% Expected: Take 'a' and 'c' (value=23, weight=10)

capacity(11).
item(a,6,12).
item(b,3,10).
item(c,4,11).
item(d,5,11).

multimap_declare(taken).
{ multimap_assign(taken,val(symbol,X),val(int,W)) } :- item(X,W,V).

% Maximize value with priority 1 (higher priority)
optimize_maximizeSum(EXPR,X,1) :- item(X,W,V),
  ITEM = val(symbol,X),
  COND = operation(multimap_isin,(ITEM,(variable(taken),()))),
  VALU = val(int,V),
  EXPR = operation(if,(COND,(VALU,()))).

% Minimize weight with priority 0 (lower priority) by maximizing negative weight
optimize_maximizeSum(EXPR,X) :- item(X,W,V),
  ITEM = val(symbol,X),
  COND = operation(multimap_isin,(ITEM,(variable(taken),()))),
  WGHT = val(int,-W),
  EXPR = operation(if,(COND,(WGHT,()))).

% Capacity constraint
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
