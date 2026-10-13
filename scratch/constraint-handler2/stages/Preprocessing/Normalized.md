## Information

Linear arithmetic expressions are normalized by combining constant coefficients
of the same variable and collecting constant terms. For example, `a + a`
becomes `2*a`, and `a + a - b + 3` becomes `2*a - b + 3`. This applies only to
linear expressions; normalization does not distribute multiplication over
addition or rewrite nonlinear products.

Relational expressions are also rewritten so that one side is the zero
constant. A relation is of the form `lhs relation 0`.

Normalization is useful because `10*a+b == 10*c+d` yields 100 combinations for
each side, so comparing the sides directly would require `100*100 = 10000`
combinations. Rewriting it as `(((10*a + b) - 10*c) - d) == 0` and splitting
into intermediate sums reduces the number of combinations significantly.

## ASP Format

## Python Datastructure

As before, but all Operation expressions that have operator: eq, neq, lt, le,
gt, ge are rewritten so that the first argument is zero. For example,
`a + b == c` would be rewritten as `0 == c - a - b`, equally:

```python
Expr(operator="eq", arguments=(Expr(operator="add", arguments=(a, b)), c))
```

becomes

```python
Expr(operator="eq", arguments=(0, Expr(operator="sub", arguments=(c, Expr(operator="add", arguments=(a, b))))))
```

## TODO
