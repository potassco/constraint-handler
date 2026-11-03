# Static Type Checking

## Scope

[Operator Semantics](../../OperatorSemantics.md) is authoritative for operator
arity, accepted types, results, and the distinction between type and runtime
errors.

`get_type` describes the type of a result if a value is produced. It does not
decide whether the expression is valid or will produce a value. `TypeChecker`
validates expressions independently of their cached result types.

## Three Implementation Files

The implementation files live in `src/constraint_handler/type_checking/`:

| File | Object | Responsibility |
| --- | --- | --- |
| `type_cache.py` | `TypeCache` | Public type representation and memoized access. |
| `type_checker.py` | `TypeChecker` | Visit the store and return diagnostics. |
| `_type_inference.py` | `_TypeInference` | Private computation, bindings, and shared operator rules. |

These are three implementation files, not three specification documents. The
package initializer only re-exports the public interface.
Existing type representations can live in `type_cache.py`, avoiding a fourth
file just for their declarations. `_TypeInference` is not exported by the package
or instantiated by normalization, splitting, or other callers.

```text
normalization / splitting               ConstraintStore
          |                                   |
          v                                   v
      TypeCache <------------------------- TypeChecker
   get_type / set_type                   visits and checks
          |                                   |
          +----------------+------------------+
                           v
                    _TypeInference
                   private shared rules
```

## TypeCache

### Public Interface

Construct one cache for a store's typing context. Its only public methods are:

```python
types = TypeCache(store)

get_type(expr: Expr, bindings: Mapping[VariableRef, Type] | None = None) -> Type
set_type(expr: Expr, known_type: Type, bindings: Mapping[VariableRef, Type] | None = None) -> None
```

The signatures describe instance methods. Callers need not supply bindings for
ordinary store expressions. Expressions need not have their own store ID.
Expose no mutable cache dictionary, inference object, or diagnostic sink.

Retain immutable scalar, `SetOf`, and `TupleType` alternatives and `UNKNOWN`.
The empty known type means no type alternatives are known to be possible;
`UNKNOWN` means the result type cannot be determined. Neither means the literal
value `None`. A type is not proof of validity, definedness, or existence of a
result. Tuple and set shapes follow Operator Semantics: flat tuples may contain
scalars or flat sets; sets contain scalars only.
Retain known tuple shapes even when a slot is `UNKNOWN`, using that marker for
the slot rather than discarding the entire tuple type.

### get_type

Return the cached type if present. Otherwise, compute it using private inference,
store it, and return it. Recursive requests for subexpressions and variable
sources use this same cache. `UNKNOWN` and the empty known type are cached
results, not cache misses.

Compute types only: do not emit diagnostics, execute Python source or callbacks,
enumerate values, or compute domains. Use the operator name directly whenever it
determines the result type. Only request operand types when they are needed to
determine the result.

| Result rule | Examples |
| --- | --- |
| Always Boolean | Comparisons, Boolean operators, membership, subset, `has_value`. |
| Always integer | `length`, `cardinality`, `floor`, `ceil`, `int_div`, `linear_integer`. |
| Always integer or real | Trigonometric functions and `sqrt`. |
| Depends on operand types | Arithmetic such as `add`, `mult`, and `abs`; branches of `ite` and `get_or_else`. |
| Depends on structure or bindings | Tuple/set element types, tuple access, variable sources, and lambda call results. |

For example, `get_type(length(42))` returns integer without inspecting the
operand; the checker independently reports that `42` is not a valid operand.
Likewise, a comparison has Boolean result type even when an operand's type is
unknown. A fixed-result rule applies even to malformed arity; arity is checked
separately. Return `UNKNOWN` only when the result type cannot be determined, not
as a general marker for invalid expressions. Do not turn processing failures
such as running out of memory into ordinary type results.

Private entries distinguish missing, currently computing, and completed states.
If inference needs an unresolved reference or cyclic dependency, use `UNKNOWN`
rather than an empty type or unbounded recursion. A fixed-result operator need
not traverse those dependencies. Dependency analysis remains responsible for
reporting undefined references and cycles.

### Lambda Bindings

A lambda body's type depends on the types bound to its parameters. For example,
using schematic expression notation:

```text
body = add(parameter, 1)

get_type(body, bindings={parameter: {integer}}) -> {integer}
get_type(body, bindings={parameter: {real}})    -> {real}
```

These are separate cache entries. Bindings override same-named store
variables. References not present in bindings resolve through the store.
Snapshot the supplied mapping into an immutable key; later caller mutations
must not change an entry's meaning. `None` and an empty mapping are equivalent.

Stored variable sources are global declarations: infer their expressions without
the querying lambda's bindings. A local parameter shadows a direct reference in
the body, but does not change the meaning of another variable's stored definition.

For `get_type(lambda_call(...))`, inference obtains argument types, binds the
lambda parameters, and requests the body's type automatically. The caller does
not have to construct bindings for an ordinary lambda call. Analyze known type
alternatives under their corresponding bindings, then union the results.

Nested calls extend outer bindings and shadow matching parameter names. Every
in-scope lambda parameter must be explicitly bound, including parameters whose
type is `UNKNOWN`, so an unknown parameter never falls back to a global variable.
A caller querying a body separately must provide those bindings itself.

A bare `Lambda` is a callable descriptor, not a value expression accepted by
`get_type`. This API returns the type of a body or call result, not a function
signature. No separate public `get_lambda_type` method is needed.

### set_type

Record a trusted result without computing the expression. A later request for
the same expression and bindings returns it immediately:

```python
known_type = types.get_type(expr)
rewritten = normalize(expr)
types.set_type(rewritten, known_type)
```

Transfers inside lambdas must use the same bindings on both calls:

```python
known_type = types.get_type(body, bindings=bindings)
rewritten_body = normalize(body)
types.set_type(rewritten_body, known_type, bindings=bindings)
```

Both examples assume the rewrite preserves the inferred type. Equivalent runtime
meaning alone does not ensure identical inferred approximations; a rewrite may
make inference more precise. The caller must justify a type transfer.

Setting an absent entry stores the type. Setting the same type again is harmless.
A different type for an existing key raises `ValueError`, avoiding silent changes
that could invalidate cached parent types. This is not a type-refinement API.

The supplied type is trusted, not recomputed to verify it. Supplying a type does
not certify that the expression is valid or suppress checker diagnostics.

### Ownership and Lifetime

The private cache key is `(structural expression, immutable bindings)`, not
`ExprId`: a store can replace an expression while preserving its ID. Start with
the full binding environment; reducing keys to relevant bindings is optional
future work, not necessary for this interface.

One preprocessing session owns the cache and shares it with checking and
transformations. Its existing variable sources must remain stable in meaning
and type. Fresh split auxiliaries may be added when their types are registered
before use. Proven type-preserving expression replacements may share the cache.
Changing a variable's sources so its type can change requires a new cache, even
when the expressions referencing that variable are structurally unchanged.

There is no global cache, public invalidation method, or eviction during the
session. Releasing the session releases its entries.

## Private Type Inference

`_TypeInference` computes types for literals, variable sources, collections,
operations, and callable bodies. Variable types conservatively combine choices,
definitions, and defaults; set-variable sources contribute scalar element types.
Labels do not change types.

Keep operator result rules and validation contracts together in
`_type_inference.py`, but apply them separately: inference computes result types;
the checker uses private contract helpers to validate operands. There is no
second operator table and no validation prerequisite for a type-cache entry.

For operand-dependent results, combine possible result types according to
Operator Semantics. Use `UNKNOWN` when necessary information is unavailable or
the result rule cannot be applied safely. Do not filter an invalid input union
to make it appear valid; the checker must see the original operand types.
Do not propagate unknown or empty operand types through fixed-result operators,
or attempt to determine runtime definedness. Nullary operators still have their
declared result types, whether or not that arity is valid for the operator.

Python call result types are unknown without executing source. Folds may return
`UNKNOWN` conservatively, but their lambda bodies still require checking under
element and accumulator bindings. Any accumulator analysis must terminate,
widening to `UNKNOWN` if structured types would otherwise grow indefinitely.

## TypeChecker

### Public Interface

```python
checker = TypeChecker(types)
diagnostics = checker.check(store)  # frozenset[Diagnostic]
```

The store must belong to the cache's typing context. Each call returns a fresh
diagnostic set, without accumulating reporting side effects in the cache. Do not
mutate the store or run normalization, domain computation, or Python callbacks.

### Checking Rules

Visit every stored root and its nested expressions, including choices,
definitions, defaults, set assignments, constraints, optimization expressions,
and conditions. Visit callable bodies under the applicable lexical bindings,
not as independent global expressions. Unknown arguments must not prevent
checking independent known errors in those bodies.

Request operand types through `get_type`, supplying bindings when needed.
Validate operation arity and argument types using the shared private rules.
A known union violates a contract if any alternative is inadmissible. Unknown
type information alone does not prove a type error, but cannot excuse known
invalid siblings or malformed structure.

Report type errors and statically decidable type warnings from Operator
Semantics. Equality between incompatible scalar types is a warning, not a type
error; integer/real comparisons are compatible. With known unions, warn if a
pair of alternatives triggers the specified warning. Also enforce statement
contracts: constraint roots and all statement conditions must be Boolean, and
optimization objectives must be integer.

Do not silently reclassify runtime-only failures as static errors. This includes
tuple index bounds and lambda parameter-count failures as currently classified
by Operator Semantics. Operand-dependent inference may return `UNKNOWN` when it
cannot safely interpret such a shape, without reporting an error. Dependency
analysis reports missing references and cycles separately.

Include severity, message, and the relevant root/expression or variable location.
Deduplicate identical diagnostics at the same location, including those reached
through multiple bindings. Preserve diagnostics for separate roots sharing an
expression. Presentation order is separate from the returned set.

Most importantly, check an expression even if its type was cached or supplied by
`set_type`. A type-cache hit is not a validation-cache hit. Checking a store
before transformations prevents invalid user expressions from disappearing
without diagnostics.
