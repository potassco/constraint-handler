% Test case for optimization with priorities
% This example demonstrates multi-level optimization where:
% - Priority 1: Maximize total value
% - Priority 0: Minimize total weight (among solutions with max value)
%
% Expected result: All items (a, b, c) are selected
% - Total value: 5+3+4 = 12 (maximum possible)
% - Total weight: 2+4+3 = 9
% - This is the only solution with maximum value, so weight minimization doesn't apply

item(a,2,5).
item(b,4,3).
item(c,3,4).

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
