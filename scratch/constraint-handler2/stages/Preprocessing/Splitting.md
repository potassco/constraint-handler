## Description

Splitting introduces auxiliary variables for nested operations when doing so
reduces the estimated grounding complexity of the enclosing expression. The
estimate depends on the operation's encoding, not just on input combinations.

For example, `concat(x, y)` enumerates pairs and costs `|D(x)| * |D(y)|`. A
`linear_integer` sum with more than two terms can use an aggregate guarded by its
result domain and costs `|D(linear_integer(...))|`. Set union uses membership rules and
costs the sum of the numbers of potential members in its two input sets,
without enumerating pairs of complete sets.

After splitting, retain supported flat native operations, including `leqv`,
`eq`, and `neq`.
Compile unsupported or still-nested operations into a `python_eval` call. Also
lower collections containing operations and existing lambda applications, even
when their arguments are already leaves. Constants and direct variable
references remain leaves.

## Definitions

The input is the `ConstraintStore` from
[InternalInput](../Inputs/InternalInput.md), with domains from
[Domains](Domains.md) computed using [DomainComputation](DomainComputation.md).

### Input Preconditions

The caller must supply structurally valid, type-checked internal expressions,
with domains, static types, and an evaluation order computed for the current
store. Recorded unknown domains and static types are allowed; missing metadata
for expressions inspected by the pass is not.

In particular, `linear_integer` must contain zero or more `(coefficient, term)`
pairs followed by an explicit integer literal offset. Each coefficient is also
an integer literal. The offset is required even when it is zero; a final term
pair is not an implicit zero offset. Shared input validation rejects malformed
linear forms before splitting. The pass does not validate or repair them.

`linear_comparison` has the same pairs and required offset, preceded by a
literal relation string (`eq`, `neq`, `lt`, `leq`, `gt`, `geq`). Its relation and
coefficients are structural constants, not split candidates. Parameter
extraction and replacement preserve these constants and their pair metadata.

The trivial cost of `linear_comparison` is `1`: one direct aggregate test,
without enumerating a numeric result domain. This unit cost models the
comparison itself, not the shared order-chain facts or weighted body size;
actual grounding still grows with parameter-domain thresholds. Nested
comparisons retain the ordinary Cartesian-product unsplit cost and compete
with extracted-parameter costs. No native operator forces a split.

The preprocessing pipeline runs normalization before computing the metadata
used by splitting. Direct callers need not normalize other arithmetic
operators, but must satisfy the same structural and metadata preconditions.

### Notation

- `params(e)` is the ordered sequence of direct parameters. Repeated parameters
  retain their separate positions. For `linear_integer`, expose each term
  expression without detaching its literal coefficient, followed by the
  constant offset. Callable descriptors and lambda bodies are not split
  candidates.
- `vars(e)` is the set of free variables occurring in `e`.
- `D(e)` is the domain of possible complete values of `e`.
- `P(s)` is the set of potential members of a set-valued expression:
  `P(s) = union(S for S in D(s))`. For an implicit set domain, `D(s)` is the
  power set of `P(s)`, including the empty set, so `|D(s)| = 2 ** |P(s)|`.

An operation is **trivial** if its parameters contain no suboperation. Its
parameters may be variables, scalar values, sets, or tuples. Collection
contents must also contain no operation; a collection does not hide a nested
operation. A literal value has a singleton domain. Variables and operation-free
collections are leaves for splitting.

Each trivial operation has an encoding-specific cost, listed at the end of this
document. The complexity of any expression `e` is:

```text
complexity(e) = trivial_cost(e)                    if e is trivial
complexity(e) = product(|D(v)| for v in vars(e))   otherwise
```

For a non-trivial operation, count each distinct free variable once, even if it
occurs in several parameters. This matches evaluation of the expression as a
Python callable, rather than assuming intermediate results have already been computed.
Collection-valued candidates also use the product over distinct free variables;
their domain cardinality still counts complete tuple or set values.

These are grounding estimates, not solver runtime bounds. Aggregate costs count
candidate result instances; aggregate elements still require grounding work. An
opaque callable's runtime is not included. An unknown cardinality has cost
infinity; do not enumerate an unknown domain to obtain its size. A product is
zero if any factor is zero, even if another factor is unknown.

## Algorithm

Start with every expression ID in the store, including values and conditions of
definitions, choices, defaults, and constraints. For each expression, test
subsets of direct parameters containing operations. Parameters that are already
leaves remain unchanged. Process newly introduced auxiliary definitions in the
same way. Actual arguments of existing `lambda_` applications participate in
this search; their callable bodies remain intact. Only operation roots undergo
subset search. Tuple and set roots containing operations are retained for the
final Python conversion, without introducing auxiliaries for their elements.

Let `trivial_cost(e)` be the encoding-specific cost from the tables below,
computed from the existing domains as if all parameters were leaves. For a
subset `selected`, let `remaining_vars(e, selected)` be the union of the free
variables in the unselected parameters. A variable shared with a selected
parameter remains in this union if an unselected parameter still uses it.

Replacing a parameter preserves its domain and potential members. Compute the
cost without creating candidate variables or rewriting the store:

```text
outer_cost(e, selected) = (
  trivial_cost(e) if every parameter containing an operation is selected
  else product(|D(v)| for v in remaining_vars(e, selected))
     * product(|D(p)| for p in selected)
)
split_cost(e, selected) = outer_cost(e, selected) + sum(
  complexity(p) for p in selected
)
```

If the outer expression remains non-trivial, each selected parameter
contributes one fresh auxiliary with domain `D(p)`. The unselected parameters
contribute their distinct free variables. If every nested parameter is
selected, use the specialized trivial-operation cost instead. The sum includes
all new auxiliary definitions. The empty subset costs `complexity(e)`.

```text
worklist = expression_ids(store)

while worklist is not empty:
  e = worklist.pop()
  if e is not an operation or e is trivial:
    continue

  parameters = [p for p in params(e) if p contains an operation]
  best_subset = empty_set
  best_cost = complexity(e)

  candidates = (
    powerset(parameters) if len(parameters) <= subset_limit
    else [empty_set, all_parameters]
  )
  for selected in candidates:
    cost = split_cost(e, selected)
    if cost < best_cost:
      best_subset = selected
      best_cost = cost

  for p in best_subset in parameter order:
    auxiliary = fresh_variable_with_domain(D(p))
    add_definition(auxiliary, p)
    replace this parameter occurrence in e with auxiliary
    worklist.push(definition_of(auxiliary))
```

Evaluate all subsets against the same unchanged expression. Enumerate them
deterministically, first by size and then by parameter order. Retain the first
candidate on equal costs, preferring no replacement to an equally costly split.
Only after the search, create and commit all replacements in the best subset.
Preserve each parameter's value kind and domain, including set membership
information. Repeated parameter occurrences remain separate candidates, each
with its own auxiliary and definition cost.

The comparison requires a strict reduction in the combined estimated cost of
the outer expression and the new definitions. Equality does not justify a
split, including `infinity > infinity`, which is false. Unknown domains do not
separately force splitting. These are local estimates; subsequent splitting and
Python conversion may change the eventual cost.

For `n` parameters containing operations, test `2 ** n` subsets when
`n <= subset_limit`. The default limit is 12, inclusive. Above the limit,
compare only no replacement with replacing all nested parameters. Thus an
expression with 12 nested parameters receives exhaustive search, while one with
13 receives all-or-nothing search.

This search is local to the direct parameters of one expression, not a global
search over recursive splitting decisions. Cache each parameter's complexity,
domain size, and free variables before enumerating subsets. Only mutate the
store after selecting the winning subset.

### Examples

Unless specified otherwise, each variable ranges over `{0, ..., 9}`. Costs
include the auxiliary definitions. "First" and "second" refer to the nested
direct parameter occurrences, in their original order. Bold marks the lowest
cost in each row.

| Case                       | Expression               | Nothing | First only | Second only | Both    |
| -------------------------- | ------------------------ | ------- | ---------- | ----------- | ------- |
| One replacement helps      | `add(add(a,b),c)`        | 1000    | **290**    | N/A         | N/A     |
| All is best                | `sub(add(a,b),add(c,d))` | 10000   | 2000       | 2000        | **561** |
| Only all helps             | `linear_integer((1,abs(a)),(1,abs(b)),(1,c),0)` | 1000 | 1010 | 1010 | **48** |
| Only a proper subset helps | `sub(add(a,b),abs(c))`   | 40      | **34**     | 50          | 44      |
| Shared variables           | `sub(add(a,b),add(a,b))` | **100** | 2000       | 2000        | 561     |

For the proper-subset row only, `D(a) = D(b) = {0, 1}`; `c` still ranges over
`{0, ..., 9}`. The cases illustrate:

- **One replacement:** `add(a,b)` costs `10 * 10 = 100` and has 19 results. The
  outer binary addition costs `19 * 10 = 190`, totaling 290 instead of
  `10 * 10 * 10 = 1000`.
- **All is best:** each inner addition costs 100 and has 19 results. Replacing
  one costs `100 + 19 * 10 * 10 = 2000`; replacing both costs
  `100 + 100 + 19 * 19 = 561`.
- **Only all helps:** replacing one `abs` leaves the outer expression
  non-trivial, costing `1000 + 10 = 1010`. Replacing both enables the linear integer sum
  aggregate over the result domain `{0, ..., 27}`, costing `28 + 10 + 10 = 48`.
- **Only a proper subset helps:** replacing `add(a,b)` costs `4 + 3 * 10 = 34`,
  compared with `2 * 2 * 10 = 40` unsplit. Replacing only `abs(c)` costs
  `10 + 2 * 2 * 10 = 50`; replacing both costs `4 + 10 + 3 * 10 = 44`.
- **Shared variables:** count `a` and `b` once each in the unsplit expression,
  giving `10 * 10 = 100`. Replacing one occurrence leaves both original
  variables in the other, giving `100 + 19 * 10 * 10 = 2000`. Replacing both
  costs `100 + 100 + 19 * 19 = 561`. This assumes separate auxiliaries per
  occurrence, without algebraic simplification or shared-expression reuse.

### Final Step: Python Conversion

After subset search, retain supported flat native operations. Native `leqv`
counts false operands by argument position and returns true for an even count;
all operands must be defined. Repeated operands retain their multiplicity.
Native support never forces a split. Compile other operations and each
collection containing operations, including auxiliary definitions, into a Python callable.
Flat `eq` and `neq` use native equality rules. Both operands must be defined;
set/set equality compares normalized member keys in both directions, while a
set and a scalar are unequal. Scalar matching joins the same keys instead of enumerating
pairs. The Python `convert` function is embedded in `eq.lp`; `@convert` is
called only for real payloads. An integral real in the ASP integer range
uses the corresponding integer term; other reals keep their real term.
Integers, Booleans, strings, and `None` remain unchanged. Tuple traversal
applies the same conversion only to real members, including tuples in sets.
Thus `1` and `1.0` are equal both as scalar values and as set members
without rounding, while Booleans remain distinct from numbers and strings are
not coerced. Stored set members and other set operations are unchanged.
Loaders enable embedded Python on their Clingo library before
parsing `eq.lp`; no external grounding context is needed. Pure integer relations still normalize to
`linear_comparison` before splitting.
Also compile every existing `lambda_` application, including calls with only
leaf arguments, and operations with callable descriptors such as `set_fold`.
An already-flat `python_eval` call remains unchanged. An existing call with
nested actual arguments is compiled as a whole. Translate
nested lambdas recursively while preserving lexical scopes. No internal lambda
application or descriptor remains in the output expression tree.

Pass the expression's distinct free variables in deterministic name order as
explicit actual inputs, including captured variables of existing lambdas.
Generate fresh bound names without capturing existing lambda parameters.

For example:

```text
sub(add(a, b), add(a, b))

becomes

python_eval(Python("lambda u, v: (u + v) - (u + v)"), a, b)
```

Here `u` and `v` stand for fresh Python parameter names. Constants and collection
structure remain in the callable body. A closed expression uses a zero-argument
Python callable. Preserve the original result domain and static type on the call.

For example, a user-written `lambda_(Lambda((u,), u), add(abs(x), 1))` that
does not benefit from auxiliary splitting becomes a Python call over `x`.
The existing lambda and its nested argument are compiled inside the callable,
not retained as nested actual inputs of the final store expression. Even
`lambda_(Lambda((u,), add(u, x)), y)` is lowered to a Python call over `x, y`.

Treat the resulting application as an opaque call; do not split or wrap it
again. Its Python body may remain nested. Its call cost is the product of the domains
of its distinct actual arguments, matching the free-variable cost used for
non-trivial expressions above. Dispatch runs after this conversion: Python
calls with known actual input domains select `complex`; an unknown actual
input selects `propagator`. The callable descriptor itself needs no domain.


### Pass and Metadata Contract

The caller supplies domains, static types, diagnostics, and an evaluation order
for the current store. Splitting mutates the store and metadata in place, uses
the supplied order only for traversal, and does not recompute dependency order,
domains, or static types. Existing diagnostics and metadata entries are
preserved. If diagnostics already contain errors, leave the input unchanged. A
negative subset limit is rejected.

New auxiliaries and rewritten applications retain their source domain and
static type. During Python conversion, copy available metadata to renamed body
nodes under the new parameter bindings, using each actual argument's complete
domain or static type. Preserve bindings of existing nested lambdas.

## Complexity of Trivial Operations

The tables cover scalar, set, and call operators from
[PythonInput](../Inputs/PythonInput.md). Costs refer to the proposed encoding
strategy. Where no specialized encoding is specified, use complete-value
enumeration as a conservative fallback.

Notation:

- `d(x) = |D(x)|`, for any input or result expression.
- `C(args) = product(d(x) for x in args)`, excluding callable descriptors and
  lambda bodies. The product over no arguments is 1.
- `F(f, args) = C(args) * product(d(v) for v in vars(f) if v not in args)`.
  This includes each distinct captured free variable once, except captures
  already supplied as direct variable arguments. A nested actual argument is
  treated as its prospective auxiliary, not as its free variables. Thus a
  capture used inside a selected argument remains a separate dependency.
- `p(s) = |P(s)|`.

For example, with `x` and `y` ranging over ten values,
`lambda_(Lambda((u,), add(x,u)), abs(y))` costs 100 unsplit. Splitting `abs(y)`
costs 100 for the call plus 10 for the auxiliary, not 20, so it is rejected.
Callable bodies remain opaque; their internal runtime is not included.

### Scalar and Boolean Operations

| Trivial operation                                                                                                      | Complexity                   | Encoding strategy                                                                                                    |
| ---------------------------------------------------------------------------------------------------------------------- | ---------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `concat(x, y)`                                                                                                         | `d(x) * d(y)`                | Enumerate pairs of values.                                                                                           |
| `length(x)` for a string or tuple                                                                                      | `d(x)`                       | One length per possible complete value.                                                                              |
| `abs`, `sqrt`, `cos`, `sin`, `tan`, `acos`, `asin`, `atan`, `minus`, `floor`, `ceil`, `real_from_int`, `int_from_real` | `d(x)`                       | Unary value enumeration.                                                                                             |
| `linear_integer((c1, x1), ..., (cn, xn), c)`, `n > 2`                                                                  | `d(e)`                       | Result-domain-guarded weighted sum aggregate.                                                                        |
| `linear_integer((c1, x1), ..., (cn, xn), c)`, `n <= 2`                                                                 | `C(x1, ..., xn)`             | Direct argument enumeration.                                                                                         |
| `sub`, `int_div`, `real_div`, `pow`                                                                                   | `d(x) * d(y)`                | Binary value enumeration.                                                                                            |
| `add(x1, ..., xn)`                                                                                                    | `C(args)`                    | Enumerate input combinations; integer sums normalize to `linear_integer` before splitting.                           |
| `mult(x1, ..., xn)`                                                                                                    | `C(args)`                    | No product aggregate is assumed.                                                                                     |
| `min(x1, ..., xn)`, `max(x1, ..., xn)`                                                                                 | `C(args)`                    | Conservative enumeration until a specialized aggregate encoding is specified.                                        |
| `eq(x, y)`, `neq(x, y)`                                                                                                | `2 * min(d(x), d(y))`        | Scan the smaller scalar domain, joining or negating membership in the other input; see the set specialization below. |
| `leq`, `lt`, `geq`, `gt`                                                                                               | `d(x) * d(y)`                | Binary value enumeration.                                                                                            |
| `get_or_else(x, y)`, `if_(x, condition)`                                                                               | `C(args)`                    | Enumerate value and fallback or condition combinations.                                                              |
| `has_value(x)`                                                                                                         | `d(x)`                       | Test each possible value for `None`.                                                                                 |
| `conj(x1, ..., xn)`, `disj(x1, ..., xn)`                                                                               | `n + 1`                      | Linear estimate: independent argument checks plus fixed result rules; no input Cartesian product.                    |
| `leqv(x1, ..., xn)`                                                                                                    | `n`                          | Aggregate counts `false` arguments; result is `true` iff the count is even.                                          |
| `ite(condition, x, y)`                                                                                                 | `d(condition) * d(x) * d(y)` | Enumerate condition and branch values.                                                                               |
| `limp`, `lxor`                                                                                                         | `d(x) * d(y)`                | Binary truth-table enumeration.                                                                                      |
| `lnot`, `snot`, `wnot`                                                                                                 | `d(x)`                       | Unary truth-table enumeration.                                                                                       |

The scalar equality estimate counts matching-value work, not shared
definedness and canonical-key rules. Those rules add linear work in the sum of
the input-domain sizes, never their Cartesian product. Tuples additionally
require traversing their elements during conversion.

### Set Operations

Membership encodings operate on potential members rather than enumerating
`D(s)`. These estimates assume valid set inputs; nullable or invalid inputs
also need scalar validity guards. Select the set specializations of `eq`,
`neq`, and `length` only when static types establish exclusively set-valued
inputs, rather than inferring the value kind from domain representation.

| Trivial operation                   | Complexity                  | Encoding strategy                                                                                  |
| ----------------------------------- | --------------------------- | -------------------------------------------------------------------------------------------------- |
| `union(s1, s2)`                     | `p(s1) + p(s2)`             | One membership rule per input; shared members contribute to both rules.                            |
| `inter(s1, s2)`                     | `min(p(s1), p(s2))`         | Join membership on the same element, not pairs of distinct elements.                               |
| `diff(s1, s2)`                      | `p(s1)`                     | Check right-hand membership for each potential left-hand member.                                   |
| `subset(s1, s2)`                    | `p(s1)`                     | Search for a left-hand member missing from the right-hand set.                                     |
| `eq(s1, s2)`, `neq(s1, s2)`         | `p(s1) + p(s2)`             | Compare membership in both directions.                                                             |
| `set_make(x1, ..., xn)`             | `sum(d(xi) for xi in args)` | Derive membership independently from each argument.                                                |
| `set_isin(x, s)`, `set_notin(x, s)` | `d(x)`                      | Check each candidate `x`; never enumerate complete sets.                                           |
| `cardinality(s)`, `length(s)`       | `d(e) + p(s)`               | Candidate count results and membership elements.                                                   |
| `set_fold(f, s, z)`                 | `F(f, (s, z))`              | One fold per complete set, initial value, and captured-input combination; body work is additional. |

### Call Operations

| Trivial operation          | Complexity        | Encoding strategy                                                 |
| -------------------------- | ----------------- | ----------------------------------------------------------------- |
| `python_eval(fn, args...)` | `C(args)`         | One opaque evaluation per argument tuple.                         |
| `lambda_(lambda, args...)` | `F(lambda, args)` | One evaluation per argument tuple and captured-input combination. |
