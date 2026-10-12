## Information

Relational expressions have been rewritten so that one side is the zero
constant. A relation is of the form `lhs relation 0`.

## ASP Format

## Python Datastructure

As before, but all Operation expressions that have operator: eq, neq, lt, le, gt, ge are rewritten so that the first argument is zero. For example, `a + b == c` would be rewritten as `0 == c - (a + b)`, equally:
```python
Expr(operator="eq", arguments=(Expr(operator="add", arguments=(a, b)), c))
```
becomes
```python
Expr(operator="eq", arguments=(0, Expr(operator="sub", arguments=(c, Expr(operator="add", arguments=(a, b))))))
```

## TODO
