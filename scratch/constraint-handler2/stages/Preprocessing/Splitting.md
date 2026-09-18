## Description

Splitting refers to breaking down complex expressions or constraints into
simpler components a,b,c,d in (0..9): `a + b + c + d` could become
`(((a + b) + c) + d)`

If we consider `a + b + c + d` we have to ground 10⁴ = 10000 combinations If we
split it as `(((a + b) + c) + d)` and reuse intermediate sums, the intermediate
sums have 19 and 28 possible values, so we only need to ground 10*10 + 19*10 +
28\*10 = 570 combinations.

## Algorithms

## TODO

- when to split, when not to split
- is it always good to split if no variables are shared between subexpressions?
  strong maybe!
- Caveat: Normalization is necessary. `10*a+b == 10*c+d` each side yields 100
  combinations, so the comparison would require 100\*100 = 10000 A
  normalization to `(((10*a + b) - 10*c) - d) == 0` and splitting into
  intermediate sums reduces the number of combinations significantly.
