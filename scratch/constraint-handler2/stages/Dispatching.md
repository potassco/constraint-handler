## Description

Dispatching assigns every top-level expression in the `ConstraintStore` to
exactly one engine. It only reads the store and the domains from
[Domains](Preprocessing/Domains.md) computed by
[DomainComputation](Preprocessing/DomainComputation.md). It does not rewrite
expressions, compute domains, or evaluate anything.

Engines:

- `native`: a native operation or bare leaf whose actual inputs have known
  domains.
- `complex`: a `python_eval` call whose actual inputs have known domains.
- `propagator`: at least one actual input has an unknown domain, including
  inputs of a `python_eval` call.

Dispatching runs after the complete splitting pass, including Python conversion.
Remaining nested expressions and lambda applications have already been compiled
to Python calls. Engine selection depends on call kind, not expression nesting.

Top-level expressions are exactly the IDs in `ConstraintStore.expressions`.
Nested expressions are converted inline and never stored under their own ID, so
every stored ID is referenced by a constraint, or as the value or condition of a
variable choice, definition, default, or set-variable entry.

## Definitions

- `params(e)`: the actual inputs of root `e`, using the same view as
  `GroundingCost.parameters` in [Splitting](Preprocessing/Splitting.md). A
  `linear_integer` contributes its term expressions and offset, not its
  coefficient pairs. A `Set` or `Tuple` contributes its elements. `VariableRef`
  and `ValueDef` have no parameters. For `python_eval`, exclude the first
  argument: its `Python` descriptor is executable code, not an input value.
- `leaf(p)`: `p` is a `VariableRef` or `ValueDef`, or a `Set` or `Tuple` that
  contains no `Operation` at any depth. This matches the trivial-leaf rule of
  Splitting.
- `known(p, domains)`: the input's recorded domain is not `unknown`. A
  `ValueDef` is always known. Callable descriptors have no domain and are
  excluded from this check, not treated as unknown inputs.

Precondition: all actual inputs are leaves. Unconverted `lambda_` calls,
lambda descriptors, and nested operations raise `TypeError`. The dispatcher
does not silently classify or repair preprocessing errors.

## Algorithm

```python
def dispatch(store: ConstraintStore, domains: DomainStore) -> DispatchStore:
  engines = DispatchStore()
  for expr_id, expr in sorted(store.expressions.items()):
        params = parameters(expr)
    require_flat_inputs(expr, params)
    known_inputs = [known(p, domains) for p in params]
    if not all(known_inputs):
            engines[expr_id] = Engine.propagator
    elif is_python_call(expr):
            engines[expr_id] = Engine.complex
    else:
      engines[expr_id] = Engine.native
    return engines
```

Rules:

1. The propagator test comes first. A Python call with an unknown actual input
  goes to `propagator`, not `complex`.
2. Every non-literal actual input must have a domain entry. A missing entry
  raises `KeyError`, even if another input is already known to be unknown.
  It is not treated as unknown.
3. The root's own domain is not consulted. Only its parameters decide the
   engine.
4. Roots are visited in ID order, and each root is classified exactly once.
5. The pass is pure. It does not mutate the store or the domains.

`DispatchStore` is a simple mapping from expression ID to `Engine`. Iterating
its items visits every classification in ID order; the expression remains
available through `store.expressions[expr_id]`. Max exports `dispatch`,
`DispatchStore`, and `Engine` as public API.

Postconditions: the result keys equal `store.expressions.keys()`, every value is
one of the three engines, and the three buckets are disjoint. Engine inputs are
selected by engine; each constraint and variable entry keeps referring to its
expressions by ID. If the value and the condition of one entry belong to
different engines, the entry is not split. Each ID is handled by its own engine.

## Examples

Assume `x` and `y` have known domains, `z` has an unknown domain, and `fn` is a
Python callable.

| Root                     | Parameters        | Engine       | Reason                              |
| ------------------------ | ----------------- | ------------ | ----------------------------------- |
| `1`                      | none              | `native`     | value, no parameters                |
| `x`                      | none              | `native`     | variable, no parameters             |
| `eq(x, 1)`               | `x`, `1`          | `native`     | leaves with known domains           |
| `set_make(x, 1)`         | `x`, `1`          | `native`     | leaves with known domains           |
| `set_isin(x, {1, 2})`    | `x`, `{1, 2}`     | `native`     | operation-free collection          |
| `python_eval(fn, x, y)`  | `x`, `y`          | `complex`    | Python call, known inputs           |
| `eq(x, z)`               | `x`, `z`          | `propagator` | `z` has an unknown domain           |
| `python_eval(fn, z)`     | `z`               | `propagator` | unknown actual input                |
| `python_eval(fn, x)`     | `x`               | `complex`    | descriptor needs no domain          |
| `python_eval(fn)`        | none              | `complex`    | zero-argument Python call           |

## TODO

- Engine implementations must respect `Constraint.is_check` and its
  undefined-value semantics; dispatch itself ignores this flag.
  Maybe python evaluation has to rause Undefined or something to make it distinguishable from other errors.
