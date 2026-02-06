# GitHub Issue: Propagator doesn't handle optimization priorities correctly

**Labels**: bug, enhancement  
**Assignee**: @kstrauch94

## Problem

The propagator's `OptimizationSum` class in `PropagatorVariables.py` doesn't track or handle optimization priorities. Currently:

1. In `propagator.py` line 671, the priority is unpacked from `Propagator_optimize_maximizeSum` atoms but not used
2. `OptimizationSum.add_value()` doesn't accept or store priority information  
3. `OptimizationSum.get_value()` returns a single summed value instead of a vector of values per priority

## Current Code

```python
# propagator.py line 670-673
maxSums = myClorm.findInPropagateInit(ctl, atom.Propagator_optimize_maximizeSum)
for (_, expr, symbol, priority), literal in maxSums.items():
    self.using_optimization = True
    self.optimization_sum.add_value(symbol, expr, literal)  # priority not used!
```

## Expected Behavior

When multiple priorities are used (e.g., priority 1 and priority 0), the propagator should:
- Track expressions grouped by priority level
- Return optimization values as a vector/tuple ordered by priority
- Allow clingo's multi-criteria optimization to work correctly

## Potential Solutions

1. **Separate OptimizationSum per priority**: Maintain a dict mapping priority → OptimizationSum
2. **Extend OptimizationSum**: Add priority tracking and return values as a priority-ordered vector
3. **Delegate to ASP layer**: Since priorities are handled correctly in `optimize.lp` using clingo's `@P` syntax, maybe the propagator doesn't need to handle them?

## Impact

Currently the compile engine (ASP-only) handles priorities correctly via `#maximize { I@P,X : ... }`. However, if the propagator engine is used, priorities are not properly handled.

## Test Case

See `tests/example/optimize_priority.lp` for a test with competing priorities.

@kstrauch94 Could you review this and determine the best approach?
