## Description

Splitting introduces auxiliary variables for nested operations when doing so
reduces the estimated grounding complexity of the enclosing expression. The
estimate depends on the operation's encoding, not just on input combinations.

For example, `concat(x, y)` enumerates pairs and costs `|D(x)| * |D(y)|`. An
n-ary addition with more than two arguments can use an aggregate guarded by its
result domain and costs `|D(add(...))|`. Set union uses membership rules and
costs the sum of the numbers of potential members in its two input sets,
without enumerating pairs of complete sets.

After splitting, convert every remaining non-trivial expression into a lambda
application. Trivial operations remain available for specialized encodings.

## Definitions

The input is the `ConstraintStore` from
[InternalInput](../Inputs/InternalInput.md), with domains from
[Domains](Domains.md) computed using [DomainComputation](DomainComputation.md).

- `params(e)` is the ordered sequence of direct parameters. Repeated parameters
  retain their separate positions.
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
document. The complexity of any operation `e` is:

```text
complexity(e) = trivial_cost(e)                    if e is trivial
complexity(e) = product(|D(v)| for v in vars(e))   otherwise
```

For a non-trivial operation, count each distinct free variable once, even if it
occurs in several parameters. This matches evaluation of the expression as a
lambda, rather than assuming intermediate results have already been computed.

These are grounding estimates, not solver runtime bounds. Aggregate costs count
candidate result instances; aggregate elements still require grounding work. An
opaque callable's runtime is not included. An unknown cardinality has cost
infinity; do not enumerate an unknown domain to obtain its size. A product is
zero if any factor is zero, even if another factor is unknown.

## Algorithm

Start with the top-level expressions of variable definitions and constraints.
For each expression, test every subset of direct parameters containing
operations. Parameters that are already leaves remain unchanged. Process newly
introduced auxiliary definitions in the same way.

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
worklist = top_level_expressions(store)

while worklist is not empty:
  e = worklist.pop()
  if e is trivial:
    continue

  parameters = [p for p in params(e) if p contains an operation]
  best_subset = empty_set
  best_cost = complexity(e)

  for selected in powerset(parameters):
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
lambda conversion may change the eventual cost.

For `n` parameters containing operations, test `2 ** n` subsets. This is
exhaustive for the direct parameters of one expression, not a global search
over recursive splitting decisions. Given that the number of parameters is
usually small, the exhaustive search over all subsets is typically feasible.
Maybe we need a guard for very large numbers of parameters to avoid
combinatorial explosion. I've seen disjunctions with 100 members, maybe then
just testing all or nothing is more practical.

### Examples

Unless specified otherwise, each variable ranges over `{0, ..., 9}`. Costs
include the auxiliary definitions. "First" and "second" refer to the nested
direct parameter occurrences, in their original order. Bold marks the lowest
cost in each row.

| Case                       | Expression               | Nothing | First only | Second only | Both    |
| -------------------------- | ------------------------ | ------- | ---------- | ----------- | ------- |
| One replacement helps      | `add(add(a,b),c)`        | 1000    | **290**    | N/A         | N/A     |
| All is best                | `sub(add(a,b),add(c,d))` | 10000   | 2000       | 2000        | **561** |
| Only all helps             | `add(abs(a),abs(b),c)`   | 1000    | 1010       | 1010        | **48**  |
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
  non-trivial, costing `1000 + 10 = 1010`. Replacing both enables the n-ary sum
  aggregate over the result domain `{0, ..., 27}`, costing `28 + 10 + 10 = 48`.
- **Only a proper subset helps:** replacing `add(a,b)` costs `4 + 3 * 10 = 34`,
  compared with `2 * 2 * 10 = 40` unsplit. Replacing only `abs(c)` costs
  `10 + 2 * 2 * 10 = 50`; replacing both costs `4 + 10 + 3 * 10 = 44`.
- **Shared variables:** count `a` and `b` once each in the unsplit expression,
  giving `10 * 10 = 100`. Replacing one occurrence leaves both original
  variables in the other, giving `100 + 19 * 10 * 10 = 2000`. Replacing both
  costs `100 + 100 + 19 * 19 = 561`. This assumes separate auxiliaries per
  occurrence, without algebraic simplification or shared-expression reuse.

### Final Step: Lambda Conversion

After splitting, convert each non-trivial top-level expression in variable
definitions and constraints, including auxiliary definitions, into a lambda
application. Bind its distinct free variables in a deterministic order, retain
the expression as the body, and pass the corresponding variables as arguments.
Respect existing lambda scopes; do not capture their bound variables.

For example:

```text
sub(add(a, b), add(a, b))

becomes

lambda_(Lambda((u, v), sub(add(u, v), add(u, v))), a, b)
```

Here `u` and `v` are fresh bound variables. Constants and collection structure
remain in the body. A closed expression uses a zero-argument lambda. Preserve
the original result domain on the application.

Treat the resulting application as an opaque call; do not split or wrap it
again. Its body may remain nested. Its call cost is the product of the domains
of its distinct actual arguments, matching the free-variable cost used for
non-trivial expressions above.

## Complexity of Trivial Operations

The tables cover scalar, set, and call operators from
[PythonInput](../Inputs/PythonInput.md). Costs refer to the proposed encoding
strategy. Where no specialized encoding is specified, use complete-value
enumeration as a conservative fallback.

Notation:

- `d(x) = |D(x)|`, for any input or result expression.
- `C(args) = product(d(x) for x in args)`, excluding callable descriptors and
  lambda bodies. The product over no arguments is 1.
- `p(s) = |P(s)|`.

### Scalar and Boolean Operations

| Trivial operation                                                                                                        | Complexity                   | Encoding strategy                                                                                                    |
| ------------------------------------------------------------------------------------------------------------------------ | ---------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `concat(x, y)`                                                                                                           | `d(x) * d(y)`                | Enumerate pairs of values.                                                                                           |
| `length(x)` for a string or tuple                                                                                        | `d(x)`                       | One length per possible complete value.                                                                              |
| `abs`, `sqrt`, `cos`, `sin`, `tan`, `acos`, `asin`, `atan`, `minus`, `floor`, `ceil`, `float_from_int`, `int_from_float` | `d(x)`                       | Unary value enumeration.                                                                                             |
| `add(x1, ..., xn)`, `n > 2`                                                                                              | `d(e)`                       | Result-domain-guarded sum aggregate.                                                                                 |
| `add(x, y)`, `sub`, `int_div`, `float_div`, `pow`                                                                        | `d(x) * d(y)`                | Binary value enumeration.                                                                                            |
| `add(x1, ..., xn)`, `n < 2`                                                                                              | `C(args)`                    | Degenerate argument enumeration.                                                                                     |
| `mult(x1, ..., xn)`                                                                                                      | `C(args)`                    | No product aggregate is assumed.                                                                                     |
| `min(x1, ..., xn)`, `max(x1, ..., xn)`                                                                                   | `C(args)`                    | Conservative enumeration until a specialized aggregate encoding is specified.                                        |
| `eq(x, y)`, `neq(x, y)`                                                                                                  | `2 * min(d(x), d(y))`        | Scan the smaller scalar domain, joining or negating membership in the other input; see the set specialization below. |
| `leq`, `lt`, `geq`, `gt`                                                                                                 | `d(x) * d(y)`                | Binary value enumeration.                                                                                            |
| `get_or_else(x, y)`, `if_(x, condition)`                                                                                 | `C(args)`                    | Enumerate value and fallback or condition combinations.                                                              |
| `has_value(x)`                                                                                                           | `d(x)`                       | Test each possible value for `None`.                                                                                 |
| `conj(x1, ..., xn)`, `disj(x1, ..., xn)`                                                                                 | `n + 1`                      | Linear estimate: independent argument checks plus fixed result rules; no input Cartesian product.                    |
| `ite(condition, x, y)`                                                                                                   | `d(condition) * d(x) * d(y)` | Enumerate condition and branch values.                                                                               |
| `leqv`, `limp`, `lxor`                                                                                                   | `d(x) * d(y)`                | Binary truth-table enumeration.                                                                                      |
| `lnot`, `snot`, `wnot`                                                                                                   | `d(x)`                       | Unary truth-table enumeration.                                                                                       |

### Set Operations

Membership encodings operate on potential members rather than enumerating
`D(s)`. These estimates assume valid set inputs; nullable or invalid inputs
also need scalar validity guards.

| Trivial operation                   | Complexity                  | Encoding strategy                                                               |
| ----------------------------------- | --------------------------- | ------------------------------------------------------------------------------- |
| `union(s1, s2)`                     | `p(s1) + p(s2)`             | One membership rule per input; shared members contribute to both rules.         |
| `inter(s1, s2)`                     | `min(p(s1), p(s2))`         | Join membership on the same element, not pairs of distinct elements.            |
| `diff(s1, s2)`                      | `p(s1)`                     | Check right-hand membership for each potential left-hand member.                |
| `subset(s1, s2)`                    | `p(s1)`                     | Search for a left-hand member missing from the right-hand set.                  |
| `eq(s1, s2)`, `neq(s1, s2)`         | `p(s1) + p(s2)`             | Compare membership in both directions.                                          |
| `set_make(x1, ..., xn)`             | `sum(d(xi) for xi in args)` | Derive membership independently from each argument.                             |
| `set_isin(x, s)`, `set_notin(x, s)` | `d(x)`                      | Check each candidate `x`; never enumerate complete sets.                        |
| `cardinality(s)`, `length(s)`       | `d(e) + p(s)`               | Candidate count results and membership elements.                                |
| `set_fold(f, s, z)`                 | `d(s) * d(z)`               | Fallback: one fold per complete set and initial value; body work is additional. |

### Call Operations

| Trivial operation          | Complexity | Encoding strategy                              |
| -------------------------- | ---------- | ---------------------------------------------- |
| `python_eval(fn, args...)` | `C(args)`  | One opaque evaluation per argument tuple.      |
| `lambda_(lambda, args...)` | `C(args)`  | One evaluation of the body per argument tuple. |
