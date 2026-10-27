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

Relational expressions become `linear_comparison` when both sides are known to
be integer-valued. They compare a weighted integer sum plus its offset against
zero. Relations involving reals, mixed types, or unknown types are not fused.

Normalization is useful because `10*a+b == 10*c+d` yields 100 combinations for
each side, so comparing the sides directly would require `100*100 = 10000`
combinations. A fused comparison of `10*a + b - 10*c - d` against zero avoids
materializing either numeric side, or the domain of their difference.

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

2. **Integer relational expressions** (`eq`, `neq`, `lt`, `leq`, `gt`, `geq`)
   become `Operation(Operator.linear_comparison, (relation, (c1, x1), ..., c))`.
   The relation is a literal string `ValueDef`; coefficient/term pairs and the
   required offset have the same integer-only contract as `linear_integer`.
   The sum is always `lhs - rhs`, preserving the direction of ordered relations.
   For example, `a + b == c` becomes:

   ```python
   Operation(
       Operator.linear_comparison,
       (
           ValueDef(ValueType.string, "eq"),
           (ValueDef(ValueType.integer, 1), a),
           (ValueDef(ValueType.integer, 1), b),
           (ValueDef(ValueType.integer, -1), c),
           ValueDef(ValueType.integer, 0),
       ),
   )
   ```

   Numeric results consumed elsewhere still use `linear_integer`. Normal
   cost-based splitting decides whether nested terms become auxiliaries; a
   non-simple comparison left unsplit uses the complex Python fallback.

Canceling terms or dropping zero products is allowed even if eliminated
expressions could be undefined. Such rewrites may suppress potential errors or
warnings, e.g. division by zero in `0 * (1 // 0)`.

## TODO
