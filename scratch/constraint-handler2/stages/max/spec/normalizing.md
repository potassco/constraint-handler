# Normalizing

## Scope

[Operator Semantics](../../OperatorSemantics.md) is authoritative for operator
results and runtime behavior. [Normalized](../../Preprocessing/Normalized.md)
defines the linear expression representation. [Static Type Checking](type_checking.md)
and [Domain Computation](domain_computation.md) define the caches used here.

Normalize expressions using static types first and domain information only when
needed to justify an additional rewrite. Retain the existing normalization
algorithm wherever these rules do not apply. This document specifies the design,
not an implementation change.

## Public Interface

One public function in `src/constraint_handler/normalizing.py` is sufficient:

```python
normalize(expr: Expr, domains: DomainCache, types: TypeCache) -> Expr
```

The two caches belong to the same store and preprocessing session. Do not expose
a normalizer object, private inference objects, or mutable cache dictionaries.
Expressions need not have their own store ID. Return the original expression
when no rewrite applies; do not mutate the input expression or the store.

Visit nested expressions and normalize lambda bodies under their call-site
bindings. Binding environments are private traversal state, not additional
public methods. Use `get_type` and `get_domain` with the applicable bindings;
do not independently recompute their results.

## Linear Expressions

Combine coefficients of identical terms and collect constant offsets in integer
linear arithmetic. For example, `a + a - b + 3` becomes `2*a - b + 3` when the
terms are known to be integer-valued. Do not distribute multiplication over
addition or rewrite nonlinear products.

Use the representation from Normalized:

```python
Operation(Operator.linear_integer, ((c1, x1), (c2, x2), ..., offset))
```

Each coefficient and the offset are integer `ValueDef` literals. Remove zero
coefficients, including products with zero. Numeric results used elsewhere
remain numeric expressions rather than comparisons.

### Eligibility

Request the type of each term and coefficient needed by the candidate rewrite.
A known integer-only type needs no domain query to establish integer-valuedness.
It does not prove validity or definedness: checking still runs independently.

For a known integer/real union or real-only type, consult its domain. Integer
ranges are already integral; every explicit float must be finite and satisfy
`value == floor(value)`. Unknown domains or any nonintegral float disqualify the
candidate. Unknown types, nonnumeric alternatives, and empty type/domain results
do not establish eligibility. Do not enumerate large integer ranges or invoke a
separate evaluator merely for this test.

Apply the same test to constant coefficients and offsets. A finite integral
float literal can be represented as an integer coefficient only when the whole
rewrite also satisfies the preservation rule below. A varying expression does
not become a constant coefficient merely because all its values are integral;
the replacement needs a justified single constant value.

Integral float values alone are sufficient to justify integer arithmetic.
Do not care about overflow, rounding, etc..

The caches themselves retain their original types and float representations;
an integrality check is not a type refinement or a domain conversion.

## Linear Comparisons

Fuse `eq`, `neq`, `lt`, `leq`, `gt`, and `geq` when the operands satisfy the
eligibility and preservation rules above:

```python
Operation(
    Operator.linear_comparison,
    (ValueDef(ValueType.string, relation), (c1, x1), ..., offset),
)
```

The weighted sum is always `lhs - rhs`, compared with zero. Preserve the
direction of ordered relations. Coefficients and offset use the same integer
literal representation as `linear_integer`. Do not leave float-valued terms in
an integer-only operator: a domain-assisted candidate also needs a sound
integer-valued replacement for each such term, or it remains unfused.

For example, `a + b == c` becomes a comparison with coefficients `1`, `1`, and
`-1`, and offset `0`. This avoids materializing both numeric sides or their
difference. Ordinary cost-based splitting still decides whether nested terms
become auxiliaries; an unsplit non-simple comparison uses the complex Python
fallback.

## Lambda Bindings

Normalize a lambda body separately for each call site's argument types and,
where needed, argument domains. A shared lambda may yield different rewritten
bodies at different calls. A rewrite must hold for every possible binding at
that call, not just one domain value.

Nested calls retain captured bindings and shadow outer parameters. Bind every
parameter explicitly, including unknown types and domains, so an unknown
parameter never inherits a same-named global or outer variable's information.
Never cache or transfer a binding-specific result as an unbound result.

## Cache Transfers and Store Updates

Read facts about the original expression before replacing it. The saved type
belongs in `set_type`, not `set_domain`:

```python
known_type = types.get_type(expr)
rewritten = normalize(expr, domains, types)
types.set_type(rewritten, known_type)
```

Rewrites preserve the inferred type and domain.

Transfer an existing domain separately when it remains a sound bound:

```python
known_domain = domains.get_domain(expr)
rewritten = normalize(expr, domains, types)
domains.set_domain(rewritten, known_domain)
```

The snippets illustrate separate transfers, not two required normalization
passes. Do not eagerly compute every original domain just to populate the cache.
Use the same bindings on both sides of transfers inside lambda bodies. A
domain transfer does not create evaluation tables.

Keep original variable sources available to domain analysis, or register their
sound bounds before replacing them. Do not change the meaning of cached
variable references midway through normalization. Changes to source meaning or
the analysis context require new caches, not silent invalidation.

## Diagnostics and Fallback

Normalization can hide static errors, such as
`0 * (1 // 0)`. This permission does not justify otherwise unsound arithmetic
or transferring a domain that excludes newly possible results.

When a candidate lacks sufficient type or domain evidence, preserve it and use
the existing normalization algorithm. Domain thresholds remain in force;
normalization must not force unavailable tables or unbounded enumeration.