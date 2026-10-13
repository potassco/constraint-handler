## Description

Splitting breaks down nested expressions into simpler components. For example,
start with the binary expression `(((a + b) + c) + d)`, where each variable has
domain `{0, ..., 9}`. Evaluating it directly requires `10⁴ = 10000` input
combinations. Fully splitting the expression by repeatedly applying the rule
introduces auxiliary variables:

```text
s1 = a + b
s2 = s1 + c
s3 = s2 + d
```

The domains of `s1`, `s2`, and `s3` contain 19, 28, and 37 values,
respectively. Grounding the three definitions takes
`10*10 + 19*10 + 28*10 = 570` combinations: 100 for `s1`, 190 for `s2`, and 280
for `s3`.

## Algorithms

Input: Domains from Domain.md

ConstraintStore with variables, constraints and expressions from
InternalInput.md

The algorithm uses the domain computation from DomainComputation.md

Given a nested expression `e`: `expr(expr(a, b), expr(a,c))` and

- let `vars(e)` denote the set of variables occurring in `e`
- let `params(e)` denote the set of direct parameters of `e` so in our examples
  `vars(e)` = {a, b, c} `params(e)` = {expr(a, b), expr(a, c)}

```
if any(unknown(D(p)) for p in params(e)) or product(|D(v)| for v in vars(e)) > product(|D(p)| for p in params(e)):
    for all non-trivial parameters p of `e`:
        replace `p` new_var := p
        update domain of new_var to be D(p)
```

After processing `e`, recursively apply the same rule to each newly introduced
auxiliary definition. Stop when a pass introduces no new auxiliaries.

This splitting should be applied only to the top level expressions of variables
and constraints.

### Example: Recursive Application

Let `e = add(add(add(a, b), c), d)`, with
`D(a) = D(b) = D(c) = D(d) = {0, ..., 9}`.

1. `vars(e) = {a, b, c, d}`, so the left side is `10*10*10*10 = 10000`.
1. `params(e) = {add(add(a, b), c), d}`. The first parameter has domain
   `{0, ..., 27}` (28 values), and `d` has 10 values, so the right side is
   `28*10 = 280`.
1. Since `10000 > 280`, the rule applies. The only non-trivial direct parameter
   is `add(add(a, b), c)`. Introduce `s = add(add(a, b), c)` with
   `D(s) = {0, ..., 27}`.
1. The rewritten expression is `add(s, d)`. This application does not split the
   definition of `s`; evaluating it directly takes `10*10*10 = 1000`
   combinations. The rewritten outer addition takes `28*10 = 280`, for a total
   of `1280` combinations after this one application.

Apply the rule again to the definition `s = add(add(a, b), c)`:

1. Its variables are `{a, b, c}`, so the left side is `10*10*10 = 1000`.
1. Its parameters are `{add(a, b), c}`, whose domain sizes are 19 and 10, so
   the right side is `19*10 = 190`.
1. Since `1000 > 190`, introduce `t = add(a, b)` with `D(t) = {0, ..., 18}`.
   The definition of `s` becomes `s = add(t, c)`.

The resulting additions take `100` combinations for `t`, `190` for `s`, and
`280` for `add(s, d)`, for a total of `570`.

Finally, apply the rule to `t = add(a, b)`. Its variables and direct parameters
are both `{a, b}`, so both products are `10*10 = 100`. Since `100 > 100` is
false, no auxiliary is introduced and the recursion stops.

### Example: Splitting Can Increase the Total

Let `e = add(add(a, b), c)`, with `D(a) = D(b) = D(c) = {0, 1}`. The unsplit
expression takes `2*2*2 = 8` combinations. The rule compares this with
`3*2 = 6` combinations for the direct parameters and therefore introduces an
auxiliary `s = add(a, b)`. Evaluating the definition of `s` takes `2*2 = 4`
combinations, and evaluating `add(s, c)` takes `3*2 = 6`, for a total of 10.

Although splitting increases the total in this example, this tradeoff should be
acceptable for most cases.

## TODO

- for n-ary sums, balanced grouping of terms may reduce the number of
  combinations Example: (a+b) + (c+d) results in 100 + 100 + 19\*19 = 561
  combinations, a little less than the 570 combinations for the left-heavy
  grouping.
