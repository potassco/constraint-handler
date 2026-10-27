## Goal

Compute a sound domain for every expression quickly.

Let `D(x) = dom(x)`, `Threshold` be the maximum number of input combinations to
evaluate for general expressions, and `BooleanThreshold` be the maximum for
boolean-valued expressions.

Domains can contain values, are just lower/upper bound approximations, or even
potential values for sets (means domain is power set of the element domain)

The input is a mapping from each variable to the set of expressions that could
define it, `Def(x) = {e1,...,en}`. An expression depends on every defining
expression of each variable it reads: add an edge `d -> e` for each input
variable `x` of `e` and each `d in Def(x)`. Once all expressions in `Def(x)`
have been processed, combine their results according to the variable-definition
semantics to obtain `D(x)`.

Order expressions with a non-recursive topological pass (Kahn's algorithm):
build the dependency edges and each expression's indegree, enqueue all
zero-indegree expressions, then repeatedly dequeue and process one expression
and decrement the indegrees of its dependents, enqueuing any that reach zero.
Deduplicate edges when computing indegrees. If the queue empties before every
expression is processed, the dependency graph contains a cycle; the remaining
expressions include any expressions blocked downstream of that cycle. Check
that every input variable has at least one defining expression separately, so
an undefined variable is not reported as a cycle.

## Expressions

### Value(v):

```
{v}
```

### VariableRef(x):

```
D(x)
```

### Set(e_1,...,en):

```
{{v1,...,vn} | vi in D(ei)}
```

### Tuple(e1,...,en):

```
{(v1,...,vn) | vi in D(ei)}
```

### Lambda(vars,body) and Python(fn):

Undefined. Neither is a value, so neither has a domain. `Lambda` is consumed by
`Operation(LambdaCall, ...)` and `Python` by `Operation(PythonEval, ...)`.

## Operators

Here, `unknown(D(x))` tests whether the input domain is unknown; this is
distinct from `None` being a value in a known domain.

For numeric arithmetic, let `I(x)` be the integer part of `D(x)` and `R(x)` its
real part. For operands `x1,...,xn`, let `N_int = product(|I(xi)|)` and
`N_real = product(|I(xi)| + |R(xi)|) - N_int`. Thus `N_real` counts
combinations containing at least one real. For operations where real inputs
produce real results, compute those combinations exactly if
`N_real <= Threshold`; otherwise return `unknown`. Compute all-integer
combinations exactly only if `N_int + N_real <= Threshold`; otherwise use
`int_range` only if the operation is guaranteed to return integers for those
inputs. This keeps the total number of exactly evaluated combinations within
`Threshold`. Operations that can produce reals from all-integer inputs must
include those combinations in the thresholded exact computation or return
`unknown`. Because `unknown` represents the whole domain, an unknown result for
any partition makes the overall result unknown.

Numerical failures, including overflow and non-finite real inputs or results,
must emit a warning and return `unknown` for the entire operation, discarding
any partial results. Mathematically undefined or complex-valued combinations
are instead excluded with a warning.

### Operation(Eq, [x,y]):

Equality accepts operands of any types; different types are not a static type
error. Integers and reals compare by numeric value (`1 == 1.0` is `true`).
Booleans are not numbers for equality (`true == 1` is `false`). Other different
scalar types compare unequal (`"a" == 42` is `false`).

```
if (unknown(D(x)) or unknown(D(y))) or product(|D(x)|,|D(y)|) > BooleanThreshold
    {true, false}
else
    {a == b | a in D(x), b in D(y)}
```

### Operation(Neq, [x,y]):

`neq(a,b)` is the negation of `eq(a,b)`, with the same cross-type rules.

```
if (unknown(D(x)) or unknown(D(y))) or product(|D(x)|,|D(y)|) > BooleanThreshold
    {true, false}
else
    {a != b | a in D(x), b in D(y)}
```

### Operation(Concat, [x,y]):

If any input domain is unknown, the domain is unknown.

```
{a + b | a in D(x), b in D(y)}
```

### Operation(Length, [x]):

If any input domain is unknown, the domain is unknown. Supported inputs are
strings, tuples, and sets; all return integer lengths.

```
{len(a) | a in D(x)}
```

### Operation(Min, [x1,...,xn]):

If any input domain is unknown, the domain is unknown. Only for numeric and
Boolean values

```
{min(v1,...,vn) | vi in D(xi), vi is numeric or Boolean}
```

### Operation(Max, [x1,...,xn]):

If any input domain is unknown, the domain is unknown. The same input
restrictions and diagnostics as for `Min` apply.

```
{max(v1,...,vn) | vi in D(xi), vi is numeric or Boolean}
```

### Operation(GetOrElse, [x,y]):

If any input domain is unknown, the domain is unknown.

```
(D(x) - {None}) union D(y), if None in D(x); else D(x)
```

### Operation(If, [c,x]):

If any input domain is unknown, the domain is unknown.

```
D(x) union {None}, if false or None in D(c); else D(x)
```

### Operation(Ite, [c,x,y]):

If any input domain is unknown, the domain is unknown.

```
D(x) if D(c)={true}; D(y) if D(c)={false}; else D(x) union D(y)
```

### Operation(HasValue, [x]):

```
if unknown(D(x))
    {true, false}
else
    {v is not None | v in D(x)}
```

### Operation(Abs, [x]):

If any input domain is unknown, the domain is unknown.

```
{abs(v) | v in D(x)}
```

### Operation(Sqrt, [x]):

If any input domain is unknown, the domain is unknown.

```
{sqrt(v) | v in D(x) where v >= 0}
# error/warning for negative values in D(x)
```

### Operation(Cos, [x]):

If any input domain is unknown, the domain is unknown.

```
{cos(v) | v in D(x)}
```

### Operation(Sin, [x]):

If any input domain is unknown, the domain is unknown.

```
{sin(v) | v in D(x)}
```

### Operation(Tan, [x]):

If any input domain is unknown, the domain is unknown.

```
{tan(v) | v in D(x) where v is not an odd multiple of pi/2}
# error/warning for odd multiples of pi/2 in D(x)
```

### Operation(Acos, [x]):

If any input domain is unknown, the domain is unknown.

```
{acos(v) | v in D(x) where v in [-1,1]}
# error/warning for values outside [-1,1] in D(x)
```

### Operation(Asin, [x]):

If any input domain is unknown, the domain is unknown.

```
{asin(v) | v in D(x) where v in [-1,1]}
# error/warning for values outside [-1,1] in D(x)
```

### Operation(Atan, [x]):

If any input domain is unknown, the domain is unknown.

```
{atan(v) | v in D(x)}
```

### Operation(Minus, [x]):

If any input domain is unknown, the domain is unknown.

```
{-v | v in D(x)}
```

### Operation(Floor, [x]):

If any input domain is unknown, the domain is unknown.

```
{floor(v) | v in D(x)}
```

### Operation(Ceil, [x]):

If any input domain is unknown, the domain is unknown.

```
{ceil(v) | v in D(x)}
```

### Operation(Add, [x1,...,xn]):

If any input domain is unknown, the domain is unknown.

```
N_int = product(|I(xi)|)
N_real = product(|I(xi)| + |R(xi)|) - N_int
if N_real > Threshold
    unknown
else
    R_real = {sum(v1,...,vn) | vi in I(xi) union R(xi), some vi in R(xi)}
    if N_int + N_real <= Threshold
        R_int = {sum(v1,...,vn) | vi in I(xi)}
    else
        R_int = int_range=(sum(min(I(xi))),sum(max(I(xi))))
    R_int union R_real
```

### Operation(Sub, [x,y]):

If any input domain is unknown, the domain is unknown.

```
N_int = |I(x)| * |I(y)|
N_real = (|I(x)| + |R(x)|) * (|I(y)| + |R(y)|) - N_int
if N_real > Threshold
    unknown
else
    R_real = {a - b | a in I(x) union R(x), b in I(y) union R(y),
               a in R(x) or b in R(y)}
    if N_int + N_real <= Threshold
        R_int = {a - b | a in I(x), b in I(y)}
    else
        R_int = int_range=(min(I(x))-max(I(y)),max(I(x))-min(I(y)))
    R_int union R_real
```

### Operation(Mult, [x1,...,xn]):

If any input domain is unknown, the domain is unknown.

```
N_int = product(|I(xi)|)
N_real = product(|I(xi)| + |R(xi)|) - N_int
if N_real > Threshold
    unknown
else
    R_real = {prod(v1,...,vn) | vi in I(xi) union R(xi), some vi in R(xi)}
    if N_int + N_real <= Threshold
        R_int = {prod(v1,...,vn) | vi in I(xi)}
    else
        R_int = fold interval multiplication over I(xi), starting from 1;
                 [a,b]*[c,d]=[min(ac,ad,bc,bd),max(ac,ad,bc,bd)]
    R_int union R_real
```

### Operation(LinearInteger, [(c1, x1), ..., (cn, xn), c]):

Each `(ci, xi)` pairs a constant integer coefficient `ci` with an
integer-valued expression `xi`, followed by a required constant integer offset
`c` (explicitly `0` when needed). If any `D(xi)` is unknown, the domain is unknown.
Coefficients and offsets must be integer literals; real or other noninteger
term values are invalid and produce a diagnostic and an unknown domain.

```
N_int = product(|I(xi)|)
if N_int <= Threshold
    {sum(ci * vi) + c | vi in I(xi)}
else
    # Each term interval is [min(ci*min(I(xi)), ci*max(I(xi))), max(ci*min(I(xi)), ci*max(I(xi)))]
    int_range=(sum(l_i) + c, sum(u_i) + c)
```

### Operation(LinearComparison, [relation, (c1, x1), ..., (cn, xn), c]):

Validate a literal string relation from `eq`, `neq`, `lt`, `leq`, `gt`, `geq`,
then apply the integer-only `LinearInteger` domain computation to the remaining
arguments. Compare that domain with the singleton integer domain `{0}` using
the corresponding comparison rules and Boolean enumeration threshold. Preserve
an unknown linear domain as unknown, including after invalid noninteger terms.
Empty inputs give an empty result; a constant-only form has one Boolean result.
The inferred sum domain is analysis metadata only, not a stored numeric
expression or a native result-domain enumeration.

### Operation(IntDiv, [x,y]):

If any input domain is unknown, the domain is unknown. The result is always an
integer, including for real operands: evaluate `int(a // b)`, rounding the
quotient toward negative infinity, not toward zero.

```
N_int = |I(x)| * |I(y)|
N_real = (|I(x)| + |R(x)|) * (|I(y)| + |R(y)|) - N_int
if N_real > Threshold
    unknown
else
    R_mixed = {int(a // b) | a in I(x) union R(x), b in I(y) union R(y),
                a in R(x) or b in R(y), b != 0}
    if N_int + N_real <= Threshold
        R_int = {a // b | a in I(x), b in I(y), b != 0}
    else
        B = {b in I(y) | b != 0}
        if I(x) = {} or B = {}
            R_int = {}
        else
            M = max(abs(min(I(x))),abs(max(I(x))))
            m = min(abs(b) | b in B)
            R_int = int_range=(-ceil(M/m),ceil(M/m))
    R_int union R_mixed  # Both parts contain only integers.
# error/warning if 0 in D(y)
```

### Operation(RealDiv, [x,y]):

If any input domain is unknown, the domain is unknown.

```
if product(|D(x)|,|D(y)|) <= Threshold
    {a / b | a in D(x), b in D(y), b != 0}
else
    unknown
# error/warning if 0 in D(y)
```

### Operation(Pow, [x,y]):

If any input domain is unknown, the domain is unknown.

```
if D(x) = {} or D(y) = {}
    {}
else if D(y) = {0}
    {a ** 0 | a in D(x)}  # Integer bases give 1; real bases give 1.0.
else if D(y) = {1}
    D(x)
else if product(|D(x)|,|D(y)|) <= Threshold
    {a ** b | a in D(x), b in D(y), a ** b is defined and real}
else
    I_y_nonnegative = {b in I(y) | b >= 0}
    N_int = |I(x)| * |I_y_nonnegative|
    N_real = |D(x)| * |D(y)| - N_int
    if N_real > Threshold
        unknown
    else
        R_real = {a ** b | a in I(x) union R(x), b in I(y) union R(y),
                   not (a in I(x) and b in I_y_nonnegative),
                   a ** b is defined and real}
        if N_int + N_real <= Threshold
            R_int = {a ** b | a in I(x), b in I_y_nonnegative}
        else
            A = max(|a| | a in I(x))
            E = max(b | b in I_y_nonnegative)
            R = max(1, A ** E)
            R_int = int_range=(-R,R)
        R_int union R_real
# error/warning for undefined or non-real powers
```

### Operation(RealFromInt, [x]):

If any input domain is unknown, the domain is unknown.

```
if |I(x)| + |R(x)| <= Threshold
    {real(v) | v in I(x)} union R(x)
else
    unknown
```

### Operation(IntFromReal, [x]):

If any input domain is unknown, the domain is unknown.

```
R = I(x) union {int(v) | v in R(x)}
if I(x) has an interval representation or |R| > Threshold
    int_range=(min(R), max(R))
else
    R
```

An empty `R` gives `{}`.

### Operation(Leq, [x,y]):

```
if unknown(D(x)) or unknown(D(y))
    {true, false}
else if D(x) = {} or D(y) = {}
    {}
else if max(D(x)) <= min(D(y))
    {true}
else if min(D(x)) > max(D(y))
    {false}

else if product(|D(x)|,|D(y)|) <= BooleanThreshold
    {a <= b | a in D(x), b in D(y)}
else
    {true,false}
```

### Operation(Lt, [x,y]):

```
if unknown(D(x)) or unknown(D(y))
    {true, false}
else if D(x) = {} or D(y) = {}
    {}
else if max(D(x)) < min(D(y))
    {true}
else if min(D(x)) >= max(D(y))
    {false}

else if product(|D(x)|,|D(y)|) <= BooleanThreshold
    {a < b | a in D(x), b in D(y)}
else
    {true,false}
```

### Operation(Geq, [x,y]):

```
if unknown(D(x)) or unknown(D(y))
    {true, false}
else if D(x) = {} or D(y) = {}
    {}
else if min(D(x)) >= max(D(y))
    {true}
else if max(D(x)) < min(D(y))
    {false}

else if product(|D(x)|,|D(y)|) <= BooleanThreshold
    {a >= b | a in D(x), b in D(y)}
else
    {true,false}
```

### Operation(Gt, [x,y]):

```
if unknown(D(x)) or unknown(D(y))
    {true, false}
else if D(x) = {} or D(y) = {}
    {}
else if min(D(x)) > max(D(y))
    {true}
else if max(D(x)) <= min(D(y))
    {false}

else if product(|D(x)|,|D(y)|) <= BooleanThreshold
    {a > b | a in D(x), b in D(y)}
else
    {true,false}
```

### Operation(Conj, [x1,...,xn]):

```
if unknown(D(x1)) or ... or unknown(D(xn))
    {true, false}
else if D(x1) = {} or ... or D(xn) = {}
    {}
else
    R = {}
    if false in D(x1) or ... or false in D(xn)
        R = R union {false}
    if true in D(x1) and ... and true in D(xn)
        R = R union {true}
    R
```

### Operation(Disj, [x1,...,xn]):

```
if unknown(D(x1)) or ... or unknown(D(xn))
    {true, false}
else if D(x1) = {} or ... or D(xn) = {}
    {}
else
    R = {}
    if true in D(x1) or ... or true in D(xn)
        R = R union {true}
    if false in D(x1) and ... and false in D(xn)
        R = R union {false}
    R
```

### Operation(Leqv, [x1,...,xn]):

```
if unknown(D(x1)) or ... or unknown(D(xn))
    {true, false}
else if D(x1) = {} or ... or D(xn) = {}
    {}
else if some D(xi) contains both true and false
    {true, false}
else
    {count(i where D(xi) = {false}) % 2 == 0}
```

`leqv` is true exactly when the number of false operands is even. Fixed inputs
give a singleton domain: all-true inputs give `{true}`, a single false input
gives `{false}`, and two false inputs give `{true}`. A nullary call gives
`{true}`. A domain containing both booleans allows either parity.

### Operation(Limp, [x,y]):

```
if unknown(D(x)) or unknown(D(y))
    {true, false}
else
    {limp(a,b) | a in D(x), b in D(y)}
```

where `limp(a, b)` is defined by this table:

```
a \\ b | false | true
-------|-------|-----
false  | true  | true
true   | false | true
```

### Operation(Lnot, [x]):

```
if unknown(D(x))
    {true, false}
else
    R = {}
    if true in D(x)
        R = R union {false}
    if false in D(x)
        R = R union {true}
    R
```

### Operation(Lxor, [x1,...,xn]):

```
if unknown(D(x1)) or ... or unknown(D(xn))
    {true, false}
else if D(x1) = {} or ... or D(xn) = {}
    {}
else if some D(xi) contains both true and false
    {true, false}
else
    {count(i where D(xi) = {true}) % 2 == 1}
```

For two operands, `xor(a, b)` is defined by this table. For more operands,
apply binary xor across the boolean operands, starting from false. A nullary
call gives `{false}`.

```
a \\ b | false | true
-------|-------|------
false  | false | true
true   | true  | false
```

### Operation(Snot, [x]):

```
if unknown(D(x))
    {true, false}
else
    R = {}
    if true in D(x) or None in D(x)
        R = R union {false}
    if false in D(x)
        R = R union {true}
    R
```

### Operation(Wnot, [x]):

```
if unknown(D(x))
    {true, false}
else
    R = {}
    if true in D(x)
        R = R union {false}
    if false in D(x) or None in D(x)
        R = R union {true}
    R
```

### Operation(Cardinality, [x]):

If any input domain is unknown, the domain is unknown.

```
{ size(v) | v in D(x)}
```

### Operation(SetMake, [x1,...,xn]):

If any input domain is unknown, the domain is unknown.

```
{{v1,...,vn} | vi in D(xi)}
```

### Operation(SetIsIn, [x,s]):

```
if unknown(D(x)) or unknown(D(s))
    {true, false}
else if product(|D(x)|,|D(s)|) <= BooleanThreshold
    {a in S | a in D(x), S in D(s)}
else
    {true,false}
```

### Operation(SetNotIn, [x,s]):

```
if unknown(D(x)) or unknown(D(s))
    {true, false}
else if product(|D(x)|,|D(s)|) <= BooleanThreshold
    {a not in S | a in D(x), S in D(s)}
else
    {true,false}
```

### Operation(Union, [x,y]):

If any input domain is unknown, the domain is unknown.

```
if product(|D(x)|,|D(y)|) <= Threshold
    {A union B | A in D(x), B in D(y)}
else
    P(U)  # represented by possible elements U

where U = union(A | A in D(x)) union union(B | B in D(y))
```

### Operation(Inter, [x,y]):

If any input domain is unknown, the domain is unknown.

```
if product(|D(x)|,|D(y)|) <= Threshold
    {A inter B | A in D(x), B in D(y)}
else
    P(U)  # represented by possible elements U

where U = union(A | A in D(x)) inter union(B | B in D(y))
```

### Operation(Diff, [x,y]):

If any input domain is unknown, the domain is unknown.

```
if product(|D(x)|,|D(y)|) <= Threshold
    {A - B | A in D(x), B in D(y)}
else
    P(U)  # represented by possible elements U

where U = union(A | A in D(x))
```

For all three set operators, an empty input domain gives `{}`.

### Operation(Subset, [x,y]):

```
if unknown(D(x)) or unknown(D(y))
    {true, false}
else if product(|D(x)|,|D(y)|) <= BooleanThreshold
    {A subseteq B | A in D(x), B in D(y)}
else
    {true,false}
```

### Operation(SetFold, [f,s,z]):

The callback is a two-parameter `Lambda((acc,elem), body)`. A `Python` callback
currently gives `unknown`, without executing Python. Malformed callbacks or
arities also give `unknown`. Invalid callback kinds and wrong operation arities
produce diagnostics.

```
if f is not a two-parameter Lambda
    unknown
else if unknown(D(s)) or unknown(D(z))
    unknown
else if D(s) = {} or D(z) = {}
    {}
else if |D(s)| * |D(z)| > Threshold
    unknown
else
    R = {}
    for (S, initial) in D(s) x D(z)
        A = {initial}
        for element in sorted(S, key=repr)
            A = domain(body, environment extended with acc -> A, elem -> {element})
            if unknown(A)
                unknown
        R = R union A
    union_domains(R, Threshold)
```

The iteration order is deterministic `repr` order. Folding the empty set
returns the initial value. Each body evaluation uses the usual operator
thresholds, and its domains are recorded in the corresponding binding scope.
The final union uses the normal domain representation: large integer outputs
may become intervals, while too many distinct real outputs give `unknown`.

### Operation(PythonEval, [fn,args...]):

`fn` is `Python(source)`, where `source` evaluates to a callable, for example
`Python("lambda x: math.sqrt(x)")`. The evaluation namespace provides Python
builtins and `math`. This executes trusted Python code, not a sandbox.
Callables must be deterministic and side-effect-free for domain inference to be
sound.

```
if any input domain is unknown
    unknown
else if any input domain is empty
    {}
else if product(|D(args[0])|,|D(args[1])|, ..., |D(args[n])|) <= Threshold
    callback = eval(source)
    R = {callback(v0,...,vn) | vi in D(args[i])}
    union_domains(R, Threshold)
else
    unknown
```

Check the product before evaluating the source or invoking the callback. A
zero-argument call has one combination and is evaluated once if
`Threshold >= 1`. Supported results are bool, int, real, string, `None`,
recursively scalar tuples, and frozensets of those scalar/tuple values.
Source-evaluation errors, non-callable source, callback exceptions, and
unsupported results produce a warning and `unknown`; partial successful results
must not be returned. `MemoryError` and `RecursionError` propagate rather than
being treated as ordinary evaluation failures.

### Operation(LambdaCall, [L,a1,...,an]):

`L` is `Lambda((x1,...,xn), body)` and the operator is `lambda_`. The arity
must match: `n` arguments for `n` parameters. The body is not a graph node; it
is evaluated once per binding, so the only dependencies are the argument
expressions. The body must be closed over its parameters, which the final step
of [Splitting](Splitting.md) guarantees. A zero-argument call evaluates the
body once. The enumeration cost matches the call cost `C(args)` in Splitting.

```
if unknown(D(a1)) or ... or unknown(D(an)) or product(|D(a1)|,...,|D(an)|) > Threshold
    unknown
else
    R = {}
    for (v1,...,vn) in D(a1) x ... x D(an)
        b = body(v1,...,vn)
        if unknown(b)
            unknown
        R = R union b
    R
```

`body(v1,...,vn)` is the domain of the body with each parameter bound to its
value. If any body evaluation is unknown, the result is unknown.

An empty argument domain makes the product zero, so the result is `{}`.
