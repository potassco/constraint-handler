## Description

Internalizing converts user-facing `python_input.Expr` values from
[PythonInput](PythonInput.md) to the internal `Expr` representation stored by
[InternalInput](InternalInput.md). In particular, each scalar base-type value
becomes a `ValueDef` with an explicit `ValueType`. Conversion is recursive, so
scalar values nested in collections, operations, and lambdas are tagged too;
the expression structure is otherwise retained.

## Algorithms

## TODO
