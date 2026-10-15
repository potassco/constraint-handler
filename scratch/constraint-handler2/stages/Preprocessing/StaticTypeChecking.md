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

| Operator(s)                                                                             | Input type contract                                                                      | Result type                                                                                                  |
| --------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `eq(x,y)`, `neq(x,y)`                                                                   | `type(x)=any, type(y)=any`                                                               | `boolean`                                                                                                    |
| `concat(x,y)`                                                                           | `type(x) == type(y) == string`                                                           | `string`                                                                                                     |
| `length(x)`                                                                             | `type(x) == string`                                                                      | `integer`                                                                                                    |
| `max(A1, ..., An)`, `min(A1, ..., An)`                                                  | `n >= 1` `type(A_i) in {boolean, integer, floating_point}`                               | `union(type(A_i))`                                                                                           |
| `get_or_else(A,B)`                                                                      | `type(A)=any, type(B)=any`                                                               | `(type(A) without none) union type(B)`                                                                       |
| `if_(condition,A)`                                                                      | `type(condition) == boolean, type(A)=any`                                                | `type(A) union none`                                                                                         |
| `has_value(x)`                                                                          | `type(x)=any`                                                                            | `boolean`                                                                                                    |
| `abs(A)`, `minus(A)`                                                                    | `type(A) in {integer, floating_point}`                                                   | `type(A)`                                                                                                    |
| `sqrt(x)`, `cos(x)`, `sin(x)`, `tan(x)`, `acos(x)`, `asin(x)`, `atan(x)`                | `type(x) in {integer, floating_point}`                                                   | `floating_point`                                                                                             |
| `floor(x)`, `ceil(x)`                                                                   | `type(x) in {integer, floating_point}`                                                   | `integer`                                                                                                    |
| `add(A1, ..., An)`, `sub(A1,A2)`, `mult(A1, ..., An)`                                   | `n >= 1` (`sub`: `n == 2`), `type(A_i) in {integer, floating_point}`                     | `integer` if all `integer`, else `floating_point`                                                            |
| `int_div(A,B)`                                                                          | `type(A_i) in {integer, floating_point}`                                                 | `integer`                                                                                                    |
| `float_div(A,B)`                                                                        | `type(A_i) in {integer, floating_point}`                                                 | `floating_point`                                                                                             |
| `pow(base,exponent)`                                                                    | `type(base) in {integer, floating_point}`, `type(exponent) in {integer, floating_point}` | `integer union floating_point` if both are `integer` (negative exponents give floats), else `floating_point` |
| `leq(A,B)`, `lt(A,B)`, `geq(A,B)`, `gt(A,B)`                                            | `type(A_i) in {boolean, integer, floating_point}`                                        | `boolean`                                                                                                    |
| `float_from_int(x)`                                                                     | `type(x) == integer`                                                                     | `floating_point`                                                                                             |
| `int_from_float(x)`                                                                     | `type(x) == floating_point`                                                              | `integer`                                                                                                    |
| `conj(A1, ..., An)`, `disj(A1, ..., An)`, `limp(A,B)`, `lxor(A1, ..., An)`             | `type(A_i) == boolean` (`limp`: `n == 2`)                                                | `boolean`                                                                                                    |
| `leqv(A,B)`                                                                             | `type(A_i) in {boolean, none}`, `n == 2`                                                  | `boolean` union `none` if any `type(A_i)` contains `none`; else `boolean`                                    |
| `ite(condition,A,B)`                                                                    | `type(condition) == boolean, type(A)=any, type(B)=any`                                   | `type(A) union type(B)`                                                                                      |
| `lnot(A)`                                                                               | `type(A) == boolean`                                                                    | `boolean`                                                                                                    |
| `snot(A)`, `wnot(A)`                                                                    | `type(A) in {boolean, none}`                                                             | `boolean`                                                                                                    |
| `cardinality(S)`                                                                        | `type(S) == set`                                                                         | `integer`                                                                                                    |
| `set_make(A1, ..., An)`                                                                 | `type(A_i) in Scalar`                                                                    | `SetOf(union(type(Ai)), false)`; `SetOf(frozenset(), true)` if `n == 0`                                      |
| `set_isin(x,S)`, `set_notin(x,S)`                                                       | `type(x) in Scalar, type(S) == set`                                                      | `boolean`                                                                                                    |
| `union(A,B)`                                                                            | `type(A) == type(B) == set`                                                              | set of members from both; `can_be_empty` only if both can be empty                                           |
| `inter(A,B)`                                                                            | `type(A) == type(B) == set`                                                              | set of members from both; `can_be_empty` true                                                                |
| `diff(A,B)`                                                                             | `type(A) == type(B) == set`                                                              | set of members from `A`; `can_be_empty` true                                                                 |
| `subset(A,B)`                                                                           | `type(A) == type(B) == set`                                                              | `boolean`                                                                                                    |
| `set_fold(callback,S,initial)`                                                          | `type(callback)=callable, type(S) == set, type(initial)=any`                             | `UnknownType()`                                                                                              |
| `python_eval(fn,args)`                                                                  | `type(fn)=callable, args=any`                                                            | `UnknownType()`                                                                                              |
| `lambda_(L,args)`                                                                       | `type(L)=lambda, args match parameters of `L\`                                           | body type under argument bindings                                                                            |

# TODO:

- how to raise errors if contracts are violated
