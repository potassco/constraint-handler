% Test case for optimization with priorities
% This example demonstrates multi-level optimization where:
% - Priority 2: Maximize total value
% - Priority 1: Minimize total weight (among solutions with max value)

item(a,2,5).
item(b,4,3).
item(c,3,4).

multimap_declare(dummy,taken).
{ multimap_assign(dummy,taken,val(symbol,X),val(int,W)) } :- item(X,W,V).

% Maximize value with priority 2 (higher priority)
optimize_maximizeSum(opt_value,EXPR,X,2) :- item(X,W,V),
  ITEM = val(symbol,X),
  COND = operation(isin,(ITEM,(variable(taken),()))),
  VALU = val(int,V),
  EXPR = operation(if,(COND,(VALU,()))).

% Minimize weight with priority 1 (lower priority) by maximizing negative weight
optimize_maximizeSum(opt_weight,EXPR,X,1) :- item(X,W,V),
  ITEM = val(symbol,X),
  COND = operation(isin,(ITEM,(variable(taken),()))),
  WGHT = val(int,-W),
  EXPR = operation(if,(COND,(WGHT,()))).
