## Description

Compute a static type for every variable and expression in
[InternalInput](../Inputs/InternalInput.md), starting from the explicit tags on
`ValueDef` literals. Store the result in [StaticTypes](StaticTypes.md).

Dependency analysis uses `compute_evaluation_order` to report undefined
variables and cycles through `Diagnostics`. Process the acyclic portion in
dependency-first topological order. Expressions in or depending on a cycle, and
variables whose types cannot be computed, receive `UNKNOWN`. Independent
expressions are still analyzed. Cycle detection is part of preprocessing, not
an unchecked prerequisite of static typing.

## Algorithms

### Literals and References

```
type(ValueDef(value_type, value)) = {value_type}
```

```
type(VariableRef(name)) = type(name)
```

### Unknown Types

```
union(T_1, ..., T_n) = UnknownType()  if any T_i == UnknownType()
```

`UnknownType()` returns the immutable singleton `UNKNOWN`. It absorbs every
union it appears in; later unions do not recover the lost information. The
empty known type `frozenset()` instead denotes no possible values.

Known unions retain all scalar and tuple alternatives. All `SetOf` members in
one union are merged: union their scalar element types and OR their
`can_be_empty` flags. Tuple alternatives are retained separately, not merged
position by position. An empty union is `frozenset()`.

### Set and Tuple Literals

A set literal must contain only scalar-valued elements. An empty literal has
`SetOf(frozenset(), True)`. Non-scalar elements produce an error and `UNKNOWN`,
never a partial set type. Unknown elements make the whole literal unknown, even
if another element has an empty type. Otherwise, if any element has the empty
type `frozenset()`, the whole literal has the empty type: that element has no
possible value, so the set cannot be constructed.

A tuple literal has `TupleType((type(item_1), ..., type(item_n)))`, including
the empty tuple `TupleType(())`. Positions may contain scalars or recursively
nested tuples, but not sets. Any known set alternative produces an error and
`UNKNOWN`, even alongside an unknown or empty position. Every position is
visited before this check. Otherwise, an unknown position makes the whole tuple
unknown, and any empty position type makes the whole tuple type empty.

### Variables: Definitions, Choices, and Defaults

For each variable `v`, collect types from all three sources:

v is a Variable:

given:

```python
choices_type = (
	union(type(choice.value) for choice in v.choices)
	if v.choices
	else frozenset()
)
definition_type = union(type(definition.value) for definition in v.definitions)
defaults_type = union(type(default.value) for default in v.defaults)
```

An empty union is `frozenset()`. Entries are retained independently; labels
identify their source and do not affect the type union. How these sources
combine when solving remains a separate variable-semantics decision.

```
type(v) = choices_type union definition_type union defaults_type
```

### Set Variables

Union the element types of every base candidate, assigned member, and default
member. These sources contribute scalar elements, not complete set values. An
unknown source makes the whole set type unknown. Any non-scalar member produces
a variable diagnostic and `UNKNOWN`; valid members must not be published as a
misleading partial type after an error. Validate known members from every
source before unioning them: an unknown source must not suppress errors in
other known sources.

The result is one `SetOf` with those scalar element types. It may be empty
unless at least one assigned member has the literal Boolean condition `True`.
Conditional assignments, choices, and defaults alone do not guarantee
nonemptiness. Conditions that might always be true are not proved here; the
flag remains conservative. A set variable without member sources has
`SetOf(frozenset(), True)`.

### Union Input Semantics

The table's scalar contracts apply to every known member of every operand, not
merely to one admissible alternative. For example, `{integer, string}` violates
a numeric contract; it is not silently narrowed to `{integer}`. Contracts do
not implicitly coerce booleans to integers.

Result rules are lifted over the Cartesian product of operand alternatives,
then unioned. Thus `add({integer, real}, {integer})` yields `{integer, real}`,
not just `{real}`. Integer-only combinations of `add`, `sub`, `mult`, and `mod`
yield `integer`; combinations containing a real yield `real`. `pow` includes
both integer and real for an integer/integer combination, and real for every
other numeric combination. Mixed input unions retain all applicable results.
Set metadata follows the conservative rules in the table.

For ordinary operations, unknown inputs propagate to `UNKNOWN`; empty known
inputs produce an empty result when no input is unknown. Operator contracts
still check known operands and arity before unknown or empty propagation, so an
unknown operand cannot hide a known invalid operand. An empty tuple or set
value is not an empty type and does not trigger this propagation rule. Nullary
operators have their explicit table rules.

### Optimization Statements

For every `Optimization`, validate the objective root against the integer-only
contract and the condition root against the Boolean-only contract. Reals,
Booleans as objectives, and mixed known unions violate the integer contract.
Empty known types remain valid (the expression has no possible value). Unknown
types follow the ordinary unknown policy; later domain/dispatch validation must
reject objectives that cannot use known finite native integer order encoding.
Diagnostics identify the offending expression or condition root.

## Operator Type Table

| Operator(s)                                                                | Input type contract                                                      | Result type                                                                                                                                                                          |
| -------------------------------------------------------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `eq(x,y)`, `neq(x,y)`                                                      | `type(x)=any, type(y)=any`                                               | `boolean`                                                                                                                                                                            |
| `concat(x,y)`                                                              | `type(x) == type(y) == string`                                           | `string`                                                                                                                                                                             |
| `length(x)`                                                                | every member is `string`, `SetOf`, or `TupleType`                        | `integer`, including empty strings, sets, and tuples                                                                                                                                 |
| `max(A1, ..., An)`, `min(A1, ..., An)`                                     | `n >= 1` `type(A_i) in {boolean, integer, real}`                         | `union(type(A_i))`                                                                                                                                                                   |
| `get_or_else(A,B)`                                                         | `type(A)=any, type(B)=any`                                               | `(type(A) without none) union type(B)`                                                                                                                                               |
| `if_(condition,A)`                                                         | `type(condition) == boolean, type(A)=any`                                | `type(A) union none`                                                                                                                                                                 |
| `has_value(x)`                                                             | `type(x)=any`                                                            | `boolean`                                                                                                                                                                            |
| `abs(A)`, `minus(A)`                                                       | `type(A) in {integer, real}`                                             | `type(A)`                                                                                                                                                                            |
| `sqrt(x)`, `cos(x)`, `sin(x)`, `tan(x)`, `acos(x)`, `asin(x)`, `atan(x)`   | `type(x) in {integer, real}`                                             | `real`                                                                                                                                                                               |
| `floor(x)`, `ceil(x)`                                                      | `type(x) in {integer, real}`                                             | `integer`                                                                                                                                                                            |
| `add(A1, ..., An)`, `sub(A1,A2)`, `mult(A1, ..., An)`                      | `n >= 1` (`sub`: `n == 2`), `type(A_i) in {integer, real}`               | `integer` if all `integer`, else `real`                                                                                                                                              |
| `linear_integer((c1, A1), ..., (cn, An), c)`                               | `c_i` and `c` are integer literals; `type(A_i) == integer`               | `integer`                                                                                                                                                                            |
| `mod(A,B)`, `int_div(A,B)`                                                 | `type(A_i) in {integer, real}`                                           | `integer` if both `integer` (`int_div`: always `integer`), else `real`                                                                                                               |
| `real_div(A,B)`                                                            | `type(A_i) in {integer, real}`                                           | `real`                                                                                                                                                                               |
| `pow(base,exponent)`                                                       | `type(base) in {integer, real}`, `type(exponent) in {integer, real}`     | `integer union real` if both are `integer` (negative exponents give reals), else `real`                                                                                              |
| `leq(A,B)`, `lt(A,B)`, `geq(A,B)`, `gt(A,B)`                               | `type(A_i) in {boolean, integer, real}`                                  | `boolean`                                                                                                                                                                            |
| `real_from_int(x)`                                                         | `type(x) == integer`                                                     | `real`                                                                                                                                                                               |
| `int_from_real(x)`                                                         | `type(x) == real`                                                        | `integer`                                                                                                                                                                            |
| `conj(A1, ..., An)`, `disj(A1, ..., An)`, `limp(A,B)`, `lxor(A1, ..., An)` | `type(A_i) == boolean` (`limp`: `n == 2`)                                | `boolean`                                                                                                                                                                            |
| `leqv(A1, ..., An)`                                                        | `type(A_i) == boolean`                                                   | `boolean`                                                                                                                                                                            |
| `ite(condition,A,B)`                                                       | `type(condition) == boolean, type(A)=any, type(B)=any`                   | `type(A) union type(B)`                                                                                                                                                              |
| `lnot(A)`                                                                  | `type(A) == boolean`                                                     | `boolean`                                                                                                                                                                            |
| `snot(A)`, `wnot(A)`                                                       | `type(A) in {boolean, none}`                                             | `boolean`                                                                                                                                                                            |
| `cardinality(S)`                                                           | `type(S) == set`                                                         | `integer`                                                                                                                                                                            |
| `set_make(A1, ..., An)`                                                    | `type(A_i) in Scalar`                                                    | `SetOf(union(type(Ai)), false)`; `SetOf(frozenset(), true)` if `n == 0`                                                                                                              |
| `set_isin(x,S)`, `set_notin(x,S)`                                          | `type(x) in Scalar, type(S) == set`                                      | `boolean`                                                                                                                                                                            |
| `union(A,B)`                                                               | `type(A) == type(B) == set`                                              | set of members from both; `can_be_empty` only if both can be empty                                                                                                                   |
| `inter(A,B)`                                                               | `type(A) == type(B) == set`                                              | set of members from both; `can_be_empty` true                                                                                                                                        |
| `diff(A,B)`                                                                | `type(A) == type(B) == set`                                              | set of members from `A`; `can_be_empty` true                                                                                                                                         |
| `subset(A,B)`                                                              | `type(A) == type(B) == set`                                              | `boolean`                                                                                                                                                                            |
| `tuple_get(T,index)`                                                       | every member of `T` is `TupleType`; integer index                        | literal index: union of the selected position across tuple alternatives; otherwise union of all positions; an out-of-range literal is an error                                       |
| `set_fold(callback,S,initial)`                                             | binary `Lambda` or `Python` callback; `type(S) == set`; any initial type | `UNKNOWN`; lambda bodies and accumulator feedback are checked as described below                                                                                                     |
| `python_eval(fn,args)`                                                     | `type(fn)=callable, args=any`                                            | `UnknownType()`                                                                                                                                                                      |
| `lambda_(L,args)`                                                          | `type(L)=lambda`, `len(args)` equals the arity of `L`                    | `UnknownType()` if any `type(a_i)` is unknown; else union over `(t_1,...,t_n)` in `type(a_1) x ... x type(a_n)` of `type_in_env(body, {x_i -> {t_i}})`; see Call Operation `lambda_` |

Nullary `conj()`, `disj()`, `lxor()`, and `leqv()` are valid Boolean
expressions. Their respective values are `true`, `false`, `false`, and `true`.
The Boolean input contract holds vacuously when there are no operands.

Equality and inequality accept different input types. Different scalar types
compare unequal, except integers and reals compare by numeric value. Thus
`eq("a", 42)` and `eq(true, 1)` are false, while `eq(1, 1.0)` is true. These
comparisons are valid expressions, not type errors.

### Call Operation `lambda_`

Parameter names within a lambda must be distinct. Repeated names produce an
error and `UNKNOWN`, even if an empty argument type prevents body evaluation.
Nested lambdas may still shadow outer parameter names.

```
type(lambda_(Lambda((x_1,...,x_n), body), a_1,...,a_n))
    = union of type(body | x_i : {t_i}) for (t_1,...,t_n) in type(a_1) x ... x type(a_n)
```

`type(body | x_i : {t_i})` is the type of `body` under the rules in this
document, with each `VariableRef(x_i)` typed `{t_i}`. Parameters shadow outer
variables of the same name, so they are looked up in the lambda's environment,
not in the global `StaticTypeStore.expressions` mapping.

Binding one member type at a time retains binding-specific results and scoped
metadata. With `x : {integer, real}`, `add(x, 1)` gives `{integer, real}`. The
number of known combinations is `product(|type(a_i)|)`. Unknown arguments are
bound as `UNKNOWN`, and the body is still visited to diagnose independent
errors; the call result remains `UNKNOWN`. An empty argument type means no
invocation, so the body is not visited. With only known inputs this gives an
empty result; an unknown input still makes the call result unknown. The type
does not depend on the domain, so it is available even when the domain is
unknown. Nested lambda bindings shadow and extend their outer environment.

### Call Operation `set_fold`

Require three arguments: callback, set, and initial accumulator. A lambda must
have exactly two distinctly named parameters, bound to accumulator and scalar
element types in that order. Repeated names are an error even for an empty set
or initial type. A `Python` callback is opaque and cannot be inspected or
executed by this pass. A known non-set operand is an error.

For lambda callbacks, start with the initial accumulator type and the set's
element types. Analyze every binding combination using the lambda rules above.
Union the callback result back into the accumulator and repeat until stable or
unknown. Scalar types form a finite fixed point. If a new structured member
would grow the accumulator, widen it to `UNKNOWN`, check the body once with
that unknown binding, and stop; this avoids unbounded tuple nesting. Empty
element or initial types do not invoke the body. Unknown sets give an unknown
element binding, but independent body errors can still be reported.

The fold's result is always `UNKNOWN`, even when its lambda checks succeed or
its set is empty. This pass does not infer a precise fold result, iteration
count, or iteration order. Feedback checking is a conservative approximation,
not proof that every runtime invocation succeeds.

### `linear_comparison`

The first argument is a literal string naming `eq`, `neq`, `lt`, `leq`, `gt`,
or `geq`. The remaining arguments satisfy the `linear_integer` contract below:
zero or more integer coefficient/term pairs and a required integer offset.
The result is Boolean, representing `sum(ci * xi) + offset relation 0`.
Real, Boolean, mixed, and other noninteger terms are rejected. Unknown terms
give `UNKNOWN`; empty known terms give an empty result if none is unknown.
Relation tags, pairs, and all their components retain scoped metadata.

### `linear_integer`

At least one argument is required. Each term is a pair `(coefficient, value)`
whose coefficient is a literal integer. The required trailing offset must also
be a literal integer, including an explicit zero when needed.
Every value term must have only integer alternatives. Coefficients,
terms, pair expressions, and offsets retain their visited types, including
lambda-scoped entries. Unknown components propagate to `UNKNOWN`; an empty
known component gives an empty result if no component is unknown.

## Diagnostics

Pass the shared `Diagnostics` collector to dependency analysis and
`compute_static_types`. Contract violations append error diagnostics rather
than raising immediately; invalid results become `UNKNOWN`. Analysis of
unrelated expressions continues. This pass does not emit warnings. The caller
decides whether collected errors prevent later preprocessing or solving.

No known partial type is published after rejecting non-scalar set elements or
an invalid member of an operator input union. Such types are unknown even when
some of their alternatives were valid.
