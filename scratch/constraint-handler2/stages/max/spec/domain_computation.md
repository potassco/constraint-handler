# Domain Computation

## Scope

[Operator Semantics](../../OperatorSemantics.md) is authoritative for operator
results, undefined values, and runtime failures. [Static Type Checking](type_checking.md)
defines the separate type cache and validation responsibilities.

`get_domain` returns a sound approximation of the values an expression can
produce. It is not a type checker, solver, or proof that a result exists.
Constraints do not narrow variable domains in this analysis. Correlations
between variable sources may be overapproximated.

The public interface has exactly three methods: `get_domain`, `set_domain`, and
`get_table`. Table access shares finite evaluation results with complex
constraints. This document specifies the design, not an implementation change.

## Public and Private Objects

All domain implementation files live in `src/constraint_handler/domains/`.
Import the public interface from `constraint_handler.domains`; production callers
must not import its implementation modules. The package exports `DomainCache`,
`DomainTable`, `Domain`, value type aliases, and domain constants. Only the cache
provides computation services, through the three methods below.

| File | Object | Responsibility |
| --- | --- | --- |
| `domain_cache.py` | `DomainCache` | Public memoized domain/table access and trusted domain transfers. |
| `_domain_computation.py` | `_DomainComputation` | Private computation, bindings, and finite evaluation reuse. |
| `_domain.py` | `Domain`, `_Range` | Immutable normalized domain values and interval storage. |
| `_integer.py`, `_symbolic.py`, `_sets.py` | Private rules | Non-enumerating symbolic bounds over locally filtered operands. |
| `_evaluation.py` | Private budgeting | Product availability checks before materializing axes. |

Simplify the immutable domain representation as specified below, reusing suitable
domain operator rules rather than retaining every existing representation.
Finite evaluation has one shared relation path; symbolic modules do not keep
independent callback loops or repeat static arity/type validation.
`_DomainComputation` is not exported or instantiated by normalization, splitting,
dispatching, or table encoding. Expose no mutable cache dictionaries.

```text
normalization / splitting / dispatching       complex constraint encoding
                  |                                      |
                  v                                      v
              DomainCache -------------------------- get_table
          get_domain / set_domain                        |
                  |                                      |
                  +----------------+---------------------+
                                   v
                          _DomainComputation
                         private evaluation rules
                                   |
                         shared relation entries
```

## DomainCache

### Public Interface

Construct one cache for a store's domain-computation context:

```python
domains = DomainCache(
    store,
    threshold=DEFAULT_THRESHOLD,
    boolean_threshold=DEFAULT_BOOLEAN_THRESHOLD,
    python_context=None,
       diagnostics=None,
)

get_domain(expr: Expr, bindings: Mapping[VariableRef, Domain] | None = None) -> Domain
set_domain(expr: Expr, known_domain: Domain, bindings: Mapping[VariableRef, Domain] | None = None) -> None
get_table(expr: Expr, bindings: Mapping[VariableRef, Domain] | None = None) -> DomainTable | None
```

The signatures describe instance methods. Expressions need not have their own
store ID. Ordinary callers omit bindings; private computation supplies them
when evaluating callable bodies.

The optional constructor diagnostic sink connects newly discovered evaluation
failures to preprocessing. It does not expose cache state or replay diagnostics.

Thresholds and a snapshot of Python context bindings belong to the cache's
context and remain fixed throughout its lifetime. Different preprocessing
options or context bindings require a new cache.

### Domain Meaning

Represent integers through a private range class, floats as explicit individual
values, and
set-valued alternatives only through their base domain of potential members.
Retain Boolean, string, and `None` alternatives, and tuple structure where
supported. Set-valued tuple positions use the same base-domain representation.
Do not expand large implicit domains merely to answer a domain query.

- An empty domain means no result values are possible under the analysis.
- `UNKNOWN_DOMAIN` means no useful domain bound can be determined.
- A domain containing `None` includes that literal value; it is not empty or
  unknown and does not represent an absent result.
- A nonempty domain does not prove that the expression is defined in any model.
- A finite domain may overapproximate actual results. It is not an exact table
  of reachable input/output combinations.

Equality and hashing use immutable normalized representations. There is no
separate explicit-integer representation: a singleton integer and its singleton
range have the same representation. Keep Booleans distinct from numeric values.
Python's ordinary value equality is not a sufficient cache key for callback
inputs, including values inside tuples and sets. Explicit float values retain
their floating-point representation, including integral floats such as `1.0`.

### Set Base Domains

Do not store explicit set values or alternatives in a `Domain`. Store only a
base domain describing potential scalar members. For example:

```text
possible results {1, 2} or {2, 3} -> set base {1, 2, 3}
possible result  {1, 2, 3}       -> set base {1, 2, 3}
```

These have the same abstract representation. The base records neither required
members nor correlations between members. It conservatively admits every subset
of its members, not just the sets that contributed to its construction. Do not
add a second exact-set representation to recover that lost precision.

Distinguish no set-valued alternative from a set alternative with an empty base:
the latter admits the empty set and is not an empty result domain. Also
distinguish an unknown member base from an empty member base. Sets still contain
scalars only; nested sets and tuple members are not introduced by this change.

Set literals, set-variable sources, and set-valued callback results all contribute
potential members to the base. Union may union bases; intersection may intersect
them. Difference must conservatively retain the left base: subtracting the right
base would incorrectly remove members that need not occur in the right set.
No base alone proves nonemptiness or an exact set cardinality.

For a finite base of size `n`, `2**n` is an upper bound on the number of possible
set values, not the number of members. Domain queries must not enumerate that
powerset. A generic table request over such an input must budget the admitted
set values, not merely the members, and may be unavailable even for a modest
base. Concrete sets in completed table rows are values, not an additional
set-domain representation.

### Private Integer Range Representation

Use a private `Range` class, conventionally named `_Range` in implementation,
to store an immutable ordered sequence of inclusive integer intervals. It is
not exported and adds no methods to the public `DomainCache` interface.

```text
integers {1, 2, 3, 7, 10, 11} -> [(1, 3), (7, 7), (10, 11)]
integer  7                   -> [(7, 7)]
no integers                  -> []
```

Each pair is `lower..upper`, with `lower <= upper`. Sort intervals by their
lower endpoint and merge overlapping or adjacent intervals. Single values are
always `x..x`; do not maintain a separate integer-value set or special singleton
field. Preserve gaps rather than replacing multiple intervals with their hull
unless an explicitly documented sound widening rule requires that loss.

Private range operations provide membership, union, intersection, bounds, and
cardinality without enumerating every integer. Cardinality is the sum of
`upper - lower + 1` over disjoint intervals. Arithmetic domain rules work with
ranges where possible; bounded enumeration remains a fallback, not the storage
format. Cache keys use the normalized interval sequence.

### Explicit Floats and Table Constraints

Store floats as individual values, separately from integer ranges. There are no
float intervals or float range approximations. A float `x` remains an explicit
float even when `x == floor(x)`; do not move it into the integer range class.

Floating-point operations use table constraints most of the. Evaluate the Cartesian product
of their input domains, retain the successful input/output rows in the shared
relation cache, and store the resulting float values individually in the output
domain. Complex constraint encoding reuses those same rows rather than
repeating the product evaluation. Mixed integer/float operations also take this
path; integer axes may need bounded expansion from their ranges.

```text
float inputs {1.0, 2.5} and {0.5}
                |
       Cartesian-product evaluation
                |
       retained rows + explicit output values
                |
       reused by table constraints
```

Check the product budget before enumeration. If the operation cannot be
enumerated within policy, return an unknown domain and an unavailable table;
do not replace its results with a float interval. Literal float values and
joins of already known float alternatives need no operation table.

Operator numeric equality and callback input identity remain different
concerns: a callback can distinguish `1` from `1.0`, and representation-sensitive
callbacks can distinguish `-0.0` from `0.0`. Preserve those distinctions in
callback table keys and rows. Non-finite floats remain outside supported finite
table enumeration.

### get_domain

Return the cached domain if present. Otherwise, compute it privately, store it,
and return it. All recursive requests for operands, variable sources, and
callable bodies pass through this same cache. Recording results only after an
unconditionally recursive traversal is not sufficient memoization.

Empty and unknown domains are completed results, not cache misses. Prefer cheap
symbolic rules where supported; floating-point operations follow the explicit
table-evaluation rule above. Request only dependencies needed by the rule;
short-circuit Boolean and conditional semantics must follow Operator Semantics.
Unlike type inference, a fixed result type does not imply a fixed result domain.

Variable domains conservatively combine choices, definitions, and defaults.
Set-variable sources contribute possible scalar members. Conditions and labels
do not establish model reachability or justify dropping otherwise possible
values. Preserve the existing conservative treatment unless a separate,
sound narrowing rule is specified.

Cache a variable's completed combined domain under its `VariableRef` expression,
using the same expression cache as for other nodes. For an ordinary global query

```text
get_domain(VariableRef("x"))
       -> look up x's sources in the store
       -> combine their domains
       -> cache[(VariableRef("x"), empty bindings)] = completed domain
```

Later expressions referencing `x` reuse this entry without looking up its sources
again. Never cache a partial source union as a completed result. Queries with
lambda bindings use separate `(VariableRef("x"), bindings)` entries; a bound
parameter takes its domain from those bindings, not the global variable sources.

When a finite evaluator must enumerate inputs, consult the private relation
cache first. If enumeration is performed, retain the completed rows and derive
the result domain from their outputs. Do not evaluate once for the domain and
again merely to reconstruct the same rows.

Cache entries distinguish absent, computing, and completed states. Resolve
dependencies on demand, independently of a caller-supplied topological schedule.
Unresolved references and dependency cycles yield conservative unknown results
rather than unbounded recursion or empty domains. Do not publish a result based
on a partially accumulated variable-source union. Dependency analysis remains
responsible for reporting missing references and cycles.

### Lambda Bindings

A body's domain depends on the domains bound to its parameters:

```text
body = add(parameter, 1)

get_domain(body, bindings={parameter: {1, 2}}) -> {2, 3}
get_domain(body, bindings={parameter: {10}})   -> {11}
```

These are separate entries. Snapshot the supplied mapping into an immutable
key. `None` and an empty mapping are equivalent. Bindings override same-named
store variables; unbound free references resolve through the store.

Ordinary lambda calls construct their bindings privately. Nested calls extend
the outer environment and shadow parameter names. Bind every in-scope parameter
explicitly, including parameters whose domains are unknown, so a parameter
cannot accidentally resolve to a global variable.

Retain binding-specific results when evaluating a body for individual input
combinations. Join the branch domains conservatively for the call result.
A bare `Lambda` is a callable descriptor, not a value accepted by `get_domain`.

### set_domain

Record a trusted sound domain without computing the expression:

```python
known_domain = domains.get_domain(expr)
domains.set_domain(auxiliary, known_domain)
domains.set_domain(rewritten_expr, known_domain)
```

The caller must justify the transfer. Rewrites need not produce identical
inferred approximations, even if they preserve runtime meaning. A transferred
bound must cover every possible result of the target expression. Transfers
inside lambda bodies use the corresponding bindings explicitly.

Setting an absent entry stores the domain. Setting the same normalized
representation again is harmless. A different domain for an existing key raises
`ValueError`, even if it is narrower. Integer intervals are normalized before
comparison. This is not a refinement API: cached parents may depend on the
existing bound.

Supplying a domain neither validates an expression nor creates a table. Never
invent input/output rows from the supplied output domain. A later table request
may compute a more precise output projection without replacing the trusted
cached domain; both must be sound and consistent.

### Ownership and Lifetime

The private domain key is `(structural expression, immutable bindings)`, not
`ExprId`: replacing an expression may preserve its ID. Start with the full
binding environment rather than introducing a binding-minimization algorithm.

One preprocessing session owns the cache. Existing variable sources must remain
stable in meaning and in the domain bounds used by the session. 

Splitting may add fresh auxiliaries if their domains are registered before use.
Preserve the original source expressions used for variable-domain analysis, or
transfer their bounds before replacing them. Do not silently recompute a
variable from transformed sources with different inferred approximations.
Changing a variable's possible values or its analysis context requires a new
cache, even when expressions referencing it are structurally unchanged.

`PreparedProblem` retains the completed domain and relation entries needed by
dispatching and fact generation. Multiple solver instances may reuse immutable
Python rows, but must encode their own library-local Clingo symbols.

There is no global semantic cache, public invalidation method, or silent eviction
during the session. Release entries with the prepared problem. A row budget is
checked before enumerating or materializing implicit axes. An aggregate memory
limit may reject further table materialization explicitly; silent eviction and
recomputation would violate the no-repeated-evaluation guarantee. Disk spilling
is possible future work, not required by this interface.

## Private Domain Computation

`_DomainComputation` coordinates literal, variable, collection, operation, and
callable-body rules. Specialized domain handlers remain responsible for integer
range arithmetic, set-base computation, tuple factoring, and other sound shortcuts.
Domain computation does not need to request a static type to enumerate a known
domain, and must not run a type-checking pass as a prerequisite for each query.

Its implementation-facing operations can be expressed schematically as:

```text
_compute_domain(expr, bindings) -> Domain
_resolve_evaluation(expr, bindings) -> evaluation program and ordered inputs
_get_or_compute_relation(program, input_domains) -> completed result or unavailable
```

These are private responsibilities, not additional methods on the public
interface. Recursive domain requests go back through `get_domain`. The relation
helper is shared by domain enumeration and `get_table`; neither
path maintains its own callback loop or independent row cache.

Keep the two kinds of cached result distinct:

```text
domain entries                              relation entries
(expr, bindings)                            (program, ordered input domains)
       |                                                 |
       v                                                 v
sound Domain                                complete rows + output projection
symbolic or enumerated                      or explicit unavailability
       ^                                                 |
       +------------- output projection -----------------+
```

The program identity includes operator semantics or Python source, bound
captures, and the interpretation of input positions. The session fixes Python
context bindings and policy. Bound captures not represented as inputs must be
part of the program identity. Reuse across renamed input variables is allowed
only when their positional interpretation is preserved.

### Type-Compatible Inputs

Compute an operation's domain using only operand values admitted by its type
contract. Filter operand domains locally before applying symbolic rules or
forming a Cartesian product; do not modify their original cached domains.
Also exclude combinations that violate combination-dependent type restrictions.
For example:

```text
x domain: {10}
y domain: {1, 2, 3, "foo"}

get_domain(add(x, y)) -> {11, 12, 13}
```

`"foo"` is ignored for addition. The type checker independently reports the
invalid alternative using the original, unfiltered operand type. Domain
computation does not repeat that static type diagnostic or return unknown just
because some known values are incompatible. If no admissible combinations
remain, the result domain is empty. Unknown inputs are not empty filtered
domains; retain a sound conservative result when their admissible values are
unknown.

Both domain and table requests apply the same filtering policy. Relation keys
include the admissible input domains and the program's type restrictions.
Filtering does not run a type-checking pass or hide invalid alternatives from
independent static validation.

Do not cache a separate materialized Cartesian product: retain axes and completed
input/output rows. Cache negative availability results for a fixed program,
inputs, and policy so unsupported or over-budget requests are not retried.

### Evaluation and Diagnostics

Domain queries are not a substitute for checking every user expression. Run
type and dependency checking independently, including when a result was supplied
by `set_domain`. Cached domains do not suppress those independent checks.

Domain-evaluation diagnostics are emitted only when new computation discovers
them, through preprocessing's private diagnostic integration. Returning a cached
domain, relation, or unavailability result emits no diagnostics and does not
replay earlier ones, even for another root sharing that entry. A later table
request may report failures discovered by genuinely new evaluation, but reusing
already evaluated rows reports nothing again.

Python callbacks must be deterministic and pure for fixed inputs and context.
A shallow context snapshot cannot freeze mutable callback state; mutating that
state violates the cache contract. Compile and evaluate under the same context
for domain and table requests.

Apply the same undefined-row policy in both paths. Expected undefined results,
including the supported recoverable callback exceptions and `FailIntegrityExn`,
produce no successful row. Runtime failures discovered during Cartesian-product
evaluation are reported as runtime errors as well as being excluded from the
successful rows. This includes invalid combinations discovered during evaluation,
even if static checking has already reported a related type error; known
type-incompatible values should normally have been filtered beforehand.
Intentional `FailIntegrityExn` rejection remains an undefined row rather than an
additional runtime-error diagnostic. Continue with other combinations when the
failure is recoverable. A completed evaluation with no successful rows is a
valid empty table. Unsupported values, non-finite results, or failures that
prevent completing the evaluation must not publish a partial relation as exact.
Return an unknown domain or an unavailable relation where a sound fallback is
defined. Do not turn `MemoryError` or `RecursionError` into ordinary cache results.

Include the expression and available evaluation context in newly emitted
diagnostics. Do not retain diagnostic replay obligations in cache entries or add
a public diagnostic-query method. Lazy computation does not promise evaluation
diagnostics for unrequested expressions. Static type and dependency diagnostics
remain the responsibility of their independent validation passes.

## get_table

Complex constraint encoding accesses reusable rows through this public method:

```python
get_table(expr: Expr, bindings: Mapping[VariableRef, Domain] | None = None) -> DomainTable | None
```

Return an immutable completed relation for the expression under an explicit
input interpretation, or `None` if it cannot be produced within the session's
policy. A cached completed relation is returned immediately. Otherwise request
finite evaluation through the same private helper used by domain computation.
This method may enumerate when `get_domain` previously used a symbolic shortcut;
that is new work, not recomputation of a discarded relation.

`DomainTable` is a data record, not another public service. It contains:

- The ordered input expressions and their immutable domains.
- The input interpretation needed to associate row positions with those inputs.
- Immutable rows of `(input_values, output_value)`.
- The output projection as a domain, before optional domain widening.

Rows preserve concrete set values when evaluated, while their output-domain
projection keeps only potential set members. An exact completed relation can
therefore be more precise than its projected domain even without threshold
widening. Reuse those rows rather than reconstructing exact sets from a base.

Completeness means every type-admissible tuple in the declared input product was
evaluated or classified as undefined. Type-incompatible combinations are excluded
by the shared filtering policy, not successful rows. Completeness does not mean
every tuple is reachable in a model.
The table consumer must enforce the declared input identities and bindings.
An empty row sequence is a completed table, distinct from `None`.

Never manufacture a table by taking the Cartesian product of input and output
domains: that loses the relation between values. Likewise, a local table over
operand values is not automatically a table over an expression's free variables.
Repeated references and correlated operands must retain their interpretation.

Splitting and Python lowering must retain enough private provenance to resolve
an unchanged evaluation program and its ordered inputs to the same relation
key. A domain transfer alone is insufficient. New input axes, different input
domains, or a differently composed program may require a new relation; this
interface does not promise to derive every new table by joining old ones.

```text
get_domain(expr) -> finite evaluation -> retained rows -> output Domain
                                              |
get_table(expr) -------------------------------+-> same rows, no evaluation
                                              |
complex encoding -----------------------------+-> solver-local facts
```

`get_table` is a required part of the public interface, even when a particular
request returns `None`. It makes shared evaluation explicit without exposing
cache dictionaries or coupling consumers to private computation objects.