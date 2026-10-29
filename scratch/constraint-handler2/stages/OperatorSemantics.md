# Operator Semantics

This document defines the meaning of expression operators independently of
whether an expression was supplied through the ASP or Python input interface.
Input formats encode operation names and arguments differently; after
internalization, an operation denotes the same mathematical operation in
either format. Input-specific spellings are listed where they are known.

An operator is applied to the values of its arguments. The contracts below
describe valid argument types and the value produced for valid inputs.
Expressions may also be undefined, have an unknown domain, or produce
diagnostics during evaluation; these cases are described by the consuming
stage, not by changing the operator's mathematical meaning. See
[StaticTypeChecking](Preprocessing/StaticTypeChecking.md) for static type
contracts and [DomainComputation](Preprocessing/DomainComputation.md) for
domain approximations, diagnostics, and threshold behavior.

## Equality and generic comparisons

| Operator | Arguments | Meaning |
| --- | --- | --- |
| `eq(x, y)` | Any values | True iff `x` and `y` are equal. Integers and reals compare by numeric value; booleans are distinct from numbers. Values of different other types are unequal. |
| `neq(x, y)` | Any values | Logical negation of `eq(x, y)`. |
| `max(x1, ..., xn)` | One or more booleans or numbers | Greatest argument under the ordering below. |
| `min(x1, ..., xn)` | One or more booleans or numbers | Least argument under the ordering below. |

Booleans are ordered `false < true`; integers and reals use numeric ordering.
Mixed integer/real comparisons use numeric values. `max` and `min` preserve the
type of the selected value.

## Strings and generic values

| Operator | Arguments | Meaning |
| --- | --- | --- |
| `concat(x, y)` | Two strings | String formed by appending `y` to `x`. |
| `length(x)` | String, tuple, or set | Number of characters, tuple elements, or set elements, respectively. |

The ASP draft also lists `trunc(string, integer)` and
`substring(string, integer, integer)`. Their precise behavior (including
indexing, negative indices, and out-of-range arguments) is not yet specified
and must be settled before they can be given portable semantics.

`mod(x, y)` appears in the static type table but not in either input operator
list, and its remainder convention is not specified. `tuple_get(t, index)`
also appears in the static type table without a corresponding input-list entry
or a defined indexing convention. These operators need their input exposure
and edge-case behavior settled before they can be specified here.

## Conditional and optional-value operations

`None` is an ordinary value in the expression model. These operators inspect
whether an argument is `None`; they do not treat every false-like value as
missing.

| Operator | Arguments | Meaning |
| --- | --- | --- |
| `get_or_else(x, fallback)` | Any values | Return `fallback` if `x` is `None`; otherwise return `x`. |
| `if_(condition, x)` | Boolean, any value | Return `x` when `condition` is true; return `None` when it is false. |
| `has_value(x)` | Any value | Return true iff `x` is not `None`. |
| `ite(condition, if_true, if_false)` | Boolean, any values | Return `if_true` when the condition is true, otherwise `if_false`. |

## Arithmetic and numeric comparisons

| Operator | Arguments | Meaning |
| --- | --- | --- |
| `abs(x)` | Integer or real | Absolute value of `x`. |
| `minus(x)` | Integer or real | Additive inverse of `x`. |
| `add(x1, ..., xn)` | One or more numbers | Sum of the arguments. |
| `sub(x, y)` | Two numbers | `x - y`. |
| `mult(x1, ..., xn)` | One or more numbers | Product of the arguments. |
| `linear_integer((c1, x1), ..., (cn, xn), c)` | Integer coefficients, integer-valued terms, optional integer offset | Sum `c1*x1 + ... + cn*xn + c`; omitted offset is zero. |
| `int_div(x, y)` | Two numbers, `y != 0` | Floor division, rounded toward negative infinity; result is an integer. |
| `real_div(x, y)` | Two numbers, `y != 0` | Real quotient `x / y`. |
| `pow(base, exponent)` | Two numbers | Exponentiation when the result is defined and real. |
| `sqrt(x)` | Number, `x >= 0` | Nonnegative square root, returned as a real. |
| `sin(x)`, `cos(x)`, `tan(x)` | Number | Corresponding trigonometric function; input is in radians. |
| `asin(x)`, `acos(x)` | Number in `[-1, 1]` | Inverse trigonometric function, returned in radians. |
| `atan(x)` | Number | Inverse tangent, returned in radians. |
| `floor(x)`, `ceil(x)` | Number | Greatest integer no greater than `x`, or least integer no less than `x`, respectively. |
| `real_from_int(x)` | Integer | Convert `x` to a real. |
| `int_from_real(x)` | Real | Convert to an integer by truncating toward zero. |
| `lt(x, y)`, `leq(x, y)`, `gt(x, y)`, `geq(x, y)` | Booleans or numbers | Strict/non-strict ordering comparisons; return a boolean. |

Integer-only `add`, `sub`, and `mult` return integers; if any operand is real,
their result is real. `pow` may return either integer or real for integer
inputs (for example, a negative exponent can produce a real); otherwise its
result is real. Division by zero and mathematically undefined or non-real
results are excluded from the value semantics and reported by the evaluating
stage.

## Boolean logic

The ordinary boolean operators require boolean operands:

| Operator | Arguments | Meaning |
| --- | --- | --- |
| `lnot(x)` | Boolean | Logical negation. |
| `conj(x1, ..., xn)` | Zero or more booleans | Conjunction; the empty conjunction is true. |
| `disj(x1, ..., xn)` | Zero or more booleans | Disjunction; the empty disjunction is false. |
| `limp(x, y)` | Two booleans | Material implication: false only when `x` is true and `y` is false. |
| `lxor(x1, ..., xn)` | Zero or more booleans | True iff an odd number of arguments are true; the empty parity is false. |
| `leqv(x1, ..., xn)` | Zero or more booleans | True iff an even number of arguments are false; the empty parity is true. |

`snot` and `wnot` implement distinct three-valued negations over `true`,
`false`, and `None`:

| Input | `snot(input)` | `wnot(input)` |
| --- | --- | --- |
| `true` | `false` | `false` |
| `false` | `true` | `true` |
| `None` | `false` | `true` |

## Sets, tuples, and folds

Sets are finite, unordered collections of distinct values. Tuples are finite,
ordered sequences and may contain nested tuples.

| Operator | Arguments | Meaning |
| --- | --- | --- |
| `set_make(x1, ..., xn)` | Zero or more scalar values | Construct the set of the arguments; duplicate elements occur once. |
| `cardinality(s)` | Set | Number of distinct elements in `s`. |
| `set_isin(x, s)` | Scalar value and set | True iff `x` is an element of `s`. |
| `set_notin(x, s)` | Scalar value and set | Logical negation of `set_isin(x, s)`. |
| `union(a, b)` | Two sets | Set containing elements that occur in `a` or `b`. |
| `inter(a, b)` | Two sets | Set containing elements that occur in both `a` and `b`. |
| `diff(a, b)` | Two sets | Set containing elements of `a` that do not occur in `b`. |
| `subset(a, b)` | Two sets | True iff every element of `a` is also in `b`. |
| `set_fold(f, s, initial)` | Binary callback, set, initial accumulator | Visit the elements of `s` in deterministic `repr` order, repeatedly replacing the accumulator with `f(accumulator, element)`, then return the final accumulator. The empty set returns `initial`. |

The set-valued `union`, `inter`, and `diff` operate on whole sets. `set_make`
and the membership operators require scalar elements; nested sets are not
elements in the current type model.

## Calls and callbacks

| Operator | Arguments | Meaning |
| --- | --- | --- |
| `lambda_(lambda, a1, ..., an)` | Lambda and one argument per parameter | Evaluate the lambda body with its parameters bound to the corresponding argument values. |
| `python_eval(fn, a1, ..., an)` | Python callable and its arguments | Invoke `fn(a1, ..., an)` and return its result. |

Lambda parameters are local to the call and shadow variables of the same name
in outer scopes. Python callbacks must be deterministic and side-effect-free
for domain computation to remain sound. Python source is trusted executable
input, not sandboxed code.

The ASP draft also lists `python_execute(source, result_name)`. This form does
not match the expression-valued `python_eval` operation, and its execution
scope, side effects, and result-binding behavior are not specified here.

## Input spelling

These are surface spellings for the same operation where both input drafts
provide names:

| Shared operation | ASP spelling | Python spelling |
| --- | --- | --- |
| Boolean negation | `neg` | `lnot` |
| Conjunction | `and` | `conj` |
| Disjunction | `or` | `disj` |
| Set intersection | `intersection` | `inter` |
| Set membership | `in` | `set_isin` |
| Greater than or equal | `ge` | `geq` |
| Less than or equal | `le` | `leq` |

The ASP draft uses `val(type, value)` wrappers and `variable(name)` terms;
Python input uses Python scalar values and `VariableRef` objects. These are
encoding differences only. A mapping above is a proposed correspondence for
the input drafts, not a claim that every spelling is currently implemented by
every input adapter.
