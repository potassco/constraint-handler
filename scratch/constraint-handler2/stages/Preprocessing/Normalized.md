## Information

Integer linear arithmetic expressions are normalized by combining constant
coefficients of the same variable and collecting constant terms. For example,
`a + a` becomes `2*a`, and `a + a - b + 3` becomes `2*a - b + 3`. This applies
only to linear expressions; normalization does not distribute multiplication
over addition or rewrite nonlinear products. Coefficients and offsets must be
integer literals, and every term must be known to have only integer values.
Real-valued, mixed integer/real, and unknown operands are not eligible for
these rewrites.

Lambda calls are normalized separately using the static types of their bound
arguments. For example, `lambda p: p + p` called with an integer is rewritten
to use `2*p`; a real-valued call is left unchanged. A shared lambda can
therefore have different normalized bodies at different call sites. If one call
can bind a parameter to either integers or reals, its body is rewritten only
where the rewrite is valid for every possible binding. Nested calls retain
captured parameter types, while inner parameters shadow outer bindings. Unknown
binding types never inherit an unrelated outer variable's type.

Relational expressions are also rewritten so that one side is the zero constant
when both sides are known to be integer-valued. A relation is of the form
`lhs relation 0`. Relations involving reals are not moved to zero.

Normalization is useful because `10*a+b == 10*c+d` yields 100 combinations for
each side, so comparing the sides directly would require `100*100 = 10000`
combinations. Rewriting it as `(((10*a + b) - 10*c) - d) == 0` and splitting
into intermediate sums reduces the number of combinations significantly.

## ASP Format

## Python Datastructure

As before, with two normalizations applied:

1. **Linear expressions** are rewritten using `Operator.linear_integer` with
   tuple pairs `(coefficient, term)` and a trailing constant offset `c`:

   ```python
   Operation(Operator.linear_integer, ((c1, x1), (c2, x2), ..., c))
   ```

   representing `c1*x1 + c2*x2 + ... + c`, where each `ci` and `c` is an
   integer constant (`ValueDef` of `integer`) and every `xi` is integer-valued.
   Zero coefficients are removed, including for `mult(0, x)`. For example,
   `a + a - b + 3` becomes:

   ```python
   Operation(
       Operator.linear_integer,
       (
           (ValueDef(ValueType.integer, 2), VariableRef("a")),
           (ValueDef(ValueType.integer, -1), VariableRef("b")),
           ValueDef(ValueType.integer, 3),
       ),
   )
   ```

1. **Relational expressions** (`eq`, `neq`, `lt`, `leq`, `gt`, `geq`) are
   rewritten so that one side is zero. For example, `a + b == c` would be
   rewritten as `0 == c - a - b`, equally:

```python
Expr(operator="eq", arguments=(Expr(operator="add", arguments=(a, b)), c))
```

becomes

```python
Expr(operator="eq", arguments=(0, Expr(operator="sub", arguments=(c, Expr(operator="add", arguments=(a, b))))))
```

(or with `Operator.linear_integer` on the non-zero side after linear
normalization).

Canceling terms or dropping zero products is allowed even if eliminated
expressions could be undefined. Such rewrites may suppress potential errors or
warnings, e.g. division by zero in `0 * (1 // 0)`.

## TODO
