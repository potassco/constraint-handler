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

## Optimization Normalization

Normalize each optimization independently; never group statements by expression
or priority. Each objective receives a fresh expression ID containing
`linear_integer((coefficient, term), ..., offset)`, with an explicit integer
offset. A bare variable becomes coefficient one plus offset zero. A constant
becomes a zero-term linear integer containing only its offset. The optimization
record is updated to the fresh root; guards, priorities, and labels are retained.
Other roles sharing the original ID are not replaced with the objective wrapper.

Objective normalization retains zero-coefficient dependencies, including
cancelled terms and multiplication by zero. Thus `x-x+5` contributes zero, not
five, when `x` is absent. Ordinary non-objective normalization is unchanged.
Evaluation-order, static-type, domain, splitting, and dispatch passes visit all
stored roots, including the new objectives and their conditions.

## TODO

- see [Splitting](Preprocessing/Splitting.md)
