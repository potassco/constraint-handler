## Description

Compute a static type for every variable and expression in
[InternalInput](../Inputs/InternalInput.md), starting from the explicit tags on
`ValueDef` literals. Store the result in [StaticTypes](StaticTypes.md).

The variable/expression dependency graph is acyclic as a prerequisite. This
stage assumes that property; it does not check it. Process variables and
expressions in dependency-first topological order.

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

`UnknownType()` absorbs every union it appears in. The information is not
recovered by later unions.

### Variables: Definitions, Choices, and Defaults

For each variable `v`, collect types from all three sources:

v is a Variable:

given:

```python
choices_type = (
	union(type(choice.value) for choice in v.choices)
	if v.choices is not None
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

## Operator Type Table

| Operator(s)                                                                | Input type contract                                                  | Result type                                                                                                                                                                          |
| -------------------------------------------------------------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `eq(x,y)`, `neq(x,y)`                                                      | `type(x)=any, type(y)=any`                                           | `boolean`                                                                                                                                                                            |
| `concat(x,y)`                                                              | `type(x) == type(y) == string`                                       | `string`                                                                                                                                                                             |
| `length(x)`                                                                | `type(x) == string`                                                  | `integer`                                                                                                                                                                            |
| `max(A1, ..., An)`, `min(A1, ..., An)`                                     | `n >= 1` `type(A_i) in {boolean, integer, real}`                     | `union(type(A_i))`                                                                                                                                                                   |
| `get_or_else(A,B)`                                                         | `type(A)=any, type(B)=any`                                           | `(type(A) without none) union type(B)`                                                                                                                                               |
| `if_(condition,A)`                                                         | `type(condition) == boolean, type(A)=any`                            | `type(A) union none`                                                                                                                                                                 |
| `has_value(x)`                                                             | `type(x)=any`                                                        | `boolean`                                                                                                                                                                            |
| `abs(A)`, `minus(A)`                                                       | `type(A) in {integer, real}`                                         | `type(A)`                                                                                                                                                                            |
| `sqrt(x)`, `cos(x)`, `sin(x)`, `tan(x)`, `acos(x)`, `asin(x)`, `atan(x)`   | `type(x) in {integer, real}`                                         | `real`                                                                                                                                                                               |
| `floor(x)`, `ceil(x)`                                                      | `type(x) in {integer, real}`                                         | `integer`                                                                                                                                                                            |
| `add(A1, ..., An)`, `sub(A1,A2)`, `mult(A1, ..., An)`                      | `n >= 1` (`sub`: `n == 2`), `type(A_i) in {integer, real}`           | `integer` if all `integer`, else `real`                                                                                                                                              |
| `linear_integer((c1, A1), ..., (cn, An), c)`                               | `c_i` and `c` are integer literals; `type(A_i) == integer`           | `integer`                                                                                                                                                                            |
| `mod(A,B)`, `int_div(A,B)`                                                 | `type(A_i) in {integer, real}`                                       | `integer` if both `integer` (`int_div`: always `integer`), else `real`                                                                                                               |
| `real_div(A,B)`                                                            | `type(A_i) in {integer, real}`                                       | `real`                                                                                                                                                                               |
| `pow(base,exponent)`                                                       | `type(base) in {integer, real}`, `type(exponent) in {integer, real}` | `integer union real` if both are `integer` (negative exponents give reals), else `real`                                                                                              |
| `leq(A,B)`, `lt(A,B)`, `geq(A,B)`, `gt(A,B)`                               | `type(A_i) in {boolean, integer, real}`                              | `boolean`                                                                                                                                                                            |
| `real_from_int(x)`                                                         | `type(x) == integer`                                                 | `real`                                                                                                                                                                               |
| `int_from_real(x)`                                                         | `type(x) == real`                                                    | `integer`                                                                                                                                                                            |
| `conj(A1, ..., An)`, `disj(A1, ..., An)`, `limp(A,B)`, `lxor(A1, ..., An)` | `type(A_i) == boolean` (`limp`: `n == 2`)                            | `boolean`                                                                                                                                                                            |
| `leqv(A1, ..., An)`                                                        | `type(A_i) == boolean`                                               | `boolean`                                                                                                                                                                            |
| `ite(condition,A,B)`                                                       | `type(condition) == boolean, type(A)=any, type(B)=any`               | `type(A) union type(B)`                                                                                                                                                              |
| `lnot(A)`                                                                  | `type(A) == boolean`                                                 | `boolean`                                                                                                                                                                            |
| `snot(A)`, `wnot(A)`                                                       | `type(A) in {boolean, none}`                                         | `boolean`                                                                                                                                                                            |
| `cardinality(S)`                                                           | `type(S) == set`                                                     | `integer`                                                                                                                                                                            |
| `set_make(A1, ..., An)`                                                    | `type(A_i) in Scalar`                                                | `SetOf(union(type(Ai)), false)`; `SetOf(frozenset(), true)` if `n == 0`                                                                                                              |
| `set_isin(x,S)`, `set_notin(x,S)`                                          | `type(x) in Scalar, type(S) == set`                                  | `boolean`                                                                                                                                                                            |
| `union(A,B)`                                                               | `type(A) == type(B) == set`                                          | set of members from both; `can_be_empty` only if both can be empty                                                                                                                   |
| `inter(A,B)`                                                               | `type(A) == type(B) == set`                                          | set of members from both; `can_be_empty` true                                                                                                                                        |
| `diff(A,B)`                                                                | `type(A) == type(B) == set`                                          | set of members from `A`; `can_be_empty` true                                                                                                                                         |
| `subset(A,B)`                                                              | `type(A) == type(B) == set`                                          | `boolean`                                                                                                                                                                            |
| `set_fold(callback,S,initial)`                                             | `type(callback)=callable, type(S) == set, type(initial)=any`         | `UnknownType()`                                                                                                                                                                      |
| `python_eval(fn,args)`                                                     | `type(fn)=callable, args=any`                                        | `UnknownType()`                                                                                                                                                                      |
| `lambda_(L,args)`                                                          | `type(L)=lambda`, `len(args)` equals the arity of `L`                | `UnknownType()` if any `type(a_i)` is unknown; else union over `(t_1,...,t_n)` in `type(a_1) x ... x type(a_n)` of `type_in_env(body, {x_i -> {t_i}})`; see Call Operation `lambda_` |

Equality and inequality accept different input types. Different scalar types
compare unequal, except integers and reals compare by numeric value. Thus
`eq("a", 42)` and `eq(true, 1)` are false, while `eq(1, 1.0)` is true. These
comparisons are valid expressions, not type errors.

### Call Operation `lambda_`

```
type(lambda_(Lambda((x_1,...,x_n), body), a_1,...,a_n))
    = union of type(body | x_i : {t_i}) for (t_1,...,t_n) in type(a_1) x ... x type(a_n)
```

`type(body | x_i : {t_i})` is the type of `body` under the rules in this
document, with each `VariableRef(x_i)` typed `{t_i}`. Parameters shadow outer
variables of the same name, so they are looked up in the lambda's environment,
not in `StaticTypes.variables`.

Binding one member type at a time keeps the result exact. With
`x : {integer, real}`, `add(x, 1)` gives `{integer, real}`, while binding the
whole union would give only `real`. The number of combinations is
`product(|type(a_i)|)`. An `UnknownType()` argument gives `UnknownType()`. An
empty argument type gives an empty result, matching the empty-domain rule. The
type does not depend on the domain, so it is available even when the domain is
unknown.

# TODO:

- how to raise errors if contracts are violated
