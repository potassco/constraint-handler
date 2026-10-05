## Description

Normalization rewrites relational expressions into a canonical form with zero
on one side. For a relation `lhs relation rhs`, the normalized expression is
`lhs - rhs relation 0`.

This preserves the relation while giving later preprocessing stages a uniform
expression shape to inspect and transform.

## Algorithms

For each relational expression:

1. Move the right-hand side to the left by subtracting it from both sides.
1. Keep the relation operator unchanged.
1. Represent the resulting relation with the zero constant on the right.

## TODO

- see [Splitting](Preprocessing/Splitting.md)
