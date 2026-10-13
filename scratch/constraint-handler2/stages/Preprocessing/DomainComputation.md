## Goal

Compute a sound domain for every expression quickly.

Let `D(x) = dom(x)`, `Threshold` be the maximum number of input combinations to
evaluate for general expressions, and `BooleanThreshold` be the maximum for
boolean-valued expressions.

Domains can contain values, are just lower/upper bound approximations, or even
potential values for sets (means domain is power set of the element domain)

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

### MultiDict(entries):

multimaps formed from entry key/value domains

### Lambda(vars,body):

--- actually not sure how this works with the vars

### Python(fn):

```
if product(|D(xi)|) <= Threshold
    apply fn to every (v1,...,vn) in product(D(xi)) and collect results
else
    unknown
```

## Operators

Here, `unknown(D(x))` tests whether the input domain is unknown; this is
distinct from `None` being a value in a known domain. For any boolean-result
operation, if `unknown(D(x))` holds for any input, return the full boolean
domain `{true, false}`, adding `None` only when that operator's semantics can
produce `None`. This fallback takes precedence over the operator-specific
rules below.

For numeric arithmetic, let `I(x)` be the integer part of `D(x)` and `F(x)` its
float part. For operands `x1,...,xn`, let `N_int = product(|I(xi)|)` and
`N_float = product(|I(xi)| + |F(xi)|) - N_int`. Thus `N_float` counts
combinations containing at least one float. For operations where float inputs
produce float results, compute those combinations exactly if `N_float <=
Threshold`; otherwise return `unknown`. Compute all-integer combinations
exactly only if `N_int + N_float <= Threshold`; otherwise use `int_range` only
if the operation is guaranteed to return integers for those inputs. This keeps
the total number of exactly evaluated combinations within `Threshold`.
Operations that can produce floats from all-integer inputs must include those
combinations in the thresholded exact computation or return `unknown`. Because
`unknown` represents the whole domain, an unknown result for any partition
makes the overall result unknown.

### Operation(Eq, [x,y]):

```
if (unknown(D(x)) or unknown(D(y))) or product(|D(x)|,|D(y)|) > BooleanThreshold
    {true, false}
else
    {a == b | a in D(x), b in D(y)}
```

### Operation(Neq, [x,y]):

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

If any input domain is unknown, the domain is unknown.

```
{len(a) | a in D(x)}
```

### Operation(Min, [x1,...,xn]):

If any input domain is unknown, the domain is unknown.

```
{min(v1,...,vn) | vi in D(xi)}
```

### Operation(Max, [x1,...,xn]):

If any input domain is unknown, the domain is unknown.

```
{max(v1,...,vn) | vi in D(xi)}
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
N_float = product(|I(xi)| + |F(xi)|) - N_int
if N_float > Threshold
    unknown
else
    R_float = {sum(v1,...,vn) | vi in I(xi) union F(xi), some vi in F(xi)}
    if N_int + N_float <= Threshold
        R_int = {sum(v1,...,vn) | vi in I(xi)}
    else
        R_int = int_range=(sum(min(I(xi))),sum(max(I(xi))))
    R_int union R_float
```

### Operation(Sub, [x,y]):

If any input domain is unknown, the domain is unknown.

```
N_int = |I(x)| * |I(y)|
N_float = (|I(x)| + |F(x)|) * (|I(y)| + |F(y)|) - N_int
if N_float > Threshold
    unknown
else
    R_float = {a - b | a in I(x) union F(x), b in I(y) union F(y),
               a in F(x) or b in F(y)}
    if N_int + N_float <= Threshold
        R_int = {a - b | a in I(x), b in I(y)}
    else
        R_int = int_range=(min(I(x))-max(I(y)),max(I(x))-min(I(y)))
    R_int union R_float
```

### Operation(Mult, [x1,...,xn]):

If any input domain is unknown, the domain is unknown.

```
N_int = product(|I(xi)|)
N_float = product(|I(xi)| + |F(xi)|) - N_int
if N_float > Threshold
    unknown
else
    R_float = {prod(v1,...,vn) | vi in I(xi) union F(xi), some vi in F(xi)}
    if N_int + N_float <= Threshold
        R_int = {prod(v1,...,vn) | vi in I(xi)}
    else
        R_int = fold interval multiplication over I(xi), starting from 1;
                 [a,b]*[c,d]=[min(ac,ad,bc,bd),max(ac,ad,bc,bd)]
    R_int union R_float
```

### Operation(IntDiv, [x,y]):

If any input domain is unknown, the domain is unknown.

```
N_int = |I(x)| * |I(y)|
N_float = (|I(x)| + |F(x)|) * (|I(y)| + |F(y)|) - N_int
if N_float > Threshold
    unknown
else
    R_float = {a // b | a in I(x) union F(x), b in I(y) union F(y),
               a in F(x) or b in F(y), b != 0}
    if N_int + N_float <= Threshold
        R_int = {a // b | a in I(x), b in I(y), b != 0}
    else
        B = {b in I(y) | b != 0}
        if I(x) = {} or B = {}
            R_int = {}
        else
            M = max(abs(min(I(x))),abs(max(I(x))))
            m = min(abs(b) | b in B)
            R_int = int_range=(-ceil(M/m),ceil(M/m))
    R_int union R_float
# error/warning if 0 in D(y)
```

### Operation(FloatDiv, [x,y]):

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
    {1}
else if D(y) = {1}
    D(x)
else if product(|D(x)|,|D(y)|) <= Threshold
    {a ** b | a in D(x), b in D(y), a ** b is defined and real}
else
    I_y_nonnegative = {b in I(y) | b >= 0}
    N_int = |I(x)| * |I_y_nonnegative|
    N_float = |D(x)| * |D(y)| - N_int
    if N_float > Threshold
        unknown
    else
        R_float = {a ** b | a in I(x) union F(x), b in I(y) union F(y),
                   not (a in I(x) and b in I_y_nonnegative),
                   a ** b is defined and real}
        if N_int + N_float <= Threshold
            R_int = {a ** b | a in I(x), b in I_y_nonnegative}
        else
            A = max(|a| | a in I(x))
            E = max(b | b in I_y_nonnegative)
            R = max(1, A ** E)
            R_int = int_range=(-R,R)
        R_int union R_float
# error/warning for undefined or non-real powers
```

### Operation(FloatFromInt, [x]):

If any input domain is unknown, the domain is unknown.

```
{float(v) | v in D(x)}
```

### Operation(IntFromFloat, [x]):

If any input domain is unknown, the domain is unknown.

```
{int(v) | v in D(x)}
```

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
    {true, false, None}
else if D(x1) = {} or ... or D(xn) = {}
    {}
else
    R = {}
    if false in D(x1) or ... or false in D(xn)
        R = R union {false}
    if true in D(x1) and ... and true in D(xn)
        R = R union {true}
    if None in any D(xi)
        and for every i, (true in D(xi) or None in D(xi))
        R = R union {None}
    R
```

### Operation(Disj, [x1,...,xn]):

```
if unknown(D(x1)) or ... or unknown(D(xn))
    {true, false, None}
else if D(x1) = {} or ... or D(xn) = {}
    {}
else
    R = {}
    if true in D(x1) or ... or true in D(xn)
        R = R union {true}
    if false in D(x1) and ... and false in D(xn)
        R = R union {false}
    if None in any D(xi)
        and for every i, (false in D(xi) or None in D(xi))
        R = R union {None}
    R
```

### Operation(Leqv, [x1,...,xn]):

```
if unknown(D(x1)) or ... or unknown(D(xn))
    {true, false, None}
else
    ???
```

### Operation(Limp, [x,y]):

```
if unknown(D(x)) or unknown(D(y))
    {true, false, None}
else
    {limp(a,b) | a in D(x), b in D(y)}
```

where `limp(a, b)` is defined by this table:

```
a \\ b | false | true  | None
-------|-------|-------|------
false  | true  | true  | true
true   | false | true  | None
None   | None  | true  | None
```

In particular, a false `a` makes the result true regardless of `b`.

### Operation(Lnot, [x]):

```
if unknown(D(x))
    {true, false, None}
else
    R = {}
    if true in D(x)
        R = R union {false}
    if false in D(x)
        R = R union {true}
    if None in D(x)
        R = R union {None}
    R
```

### Operation(Lxor, [x1,...,xn]):

```
if unknown(D(x1)) or ... or unknown(D(xn))
    {true, false, None}
else if product(|D(x1)|,...,|D(xn)|) <= BooleanThreshold
    {xor(v1,...,vn) | vi in D(xi)}
else
    R = {true, false}
    if None in any D(xi)
        R = R union {None}
    R
```

For two operands, `xor(a, b)` is defined by this table. For more operands,
apply binary xor across the operands; if any operand is `None`, the result is
`None`.

```
a \\ b | false | true  | None
-------|-------|-------|------
false  | false | true  | None
true   | true  | false | None
None   | None  | None  | None
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

where U = union(A | A in D(x)) union union(B | B in D(y))
```

### Operation(Diff, [x,y]):

If any input domain is unknown, the domain is unknown.

```
if product(|D(x)|,|D(y)|) <= Threshold
    {A - B | A in D(x), B in D(y)}
else
    P(U)  # represented by possible elements U

where U = union(A | A in D(x)) union union(B | B in D(y))
```

### Operation(Subset, [x,y]):

```
if unknown(D(x)) or unknown(D(y))
    {true, false}
else if product(|D(x)|,|D(y)|) <= Threshold
    {A subseteq B | A in D(x), B in D(y)}
else
    {true,false}
```

### Operation(SetFold, [f,s,z]):

If any input domain is unknown, the domain is unknown.

```
fold f over S in D(s), starting with z in D(z)
# complete domain computation
```

### Operation(Find, [k,m]):

If any input domain is unknown, the domain is unknown.

```
{m[k] if k in m else {} | k in D(k), m in D(m)}
```

### Operation(Find2, [k,v,m]):

```
if unknown(D(k)) or unknown(D(v)) or unknown(D(m))
    {true, false}
else
    {k in m and v in m[k] | k in D(k), v in D(v), m in D(m)}
```

### Operation(MultimapIsIn, [k,m]):

```
if unknown(D(k)) or unknown(D(m))
    {true, false}
else
    {true, false}
```

<!--
### Operation(MultimapMake, [args...]):
```
multimaps formed from argument key/value pairs
```

### Operation(MultimapFold, [f,m,z]):
```
fold f over entries of m in D(m), starting with z in D(z)
```

### Operation(MultimapFoldI, [f,m,z]):
```
as multimap_fold, passing each key to f
```

### Operation(CountKeys, [m]):
```
[min_key_count(D(m)),max_key_count(D(m))]
```

### Operation(CountEntries, [m]):
```
[min_entry_count(D(m)),max_entry_count(D(m))]
```

### Operation(SumIntEntries, [m]):
```
sum of integer entries; bounds from entry-count and value bounds
```

### Operation(MaxEntries, [m]):
```
[min(D(values)),max(D(values))]; include None if empty is possible
```

### Operation(MinEntries, [m]):
```
[min(D(values)),max(D(values))]; include None if empty is possible
``` -->

### Operation(PythonEval, [fn,args...]):

If any input domain is unknown, the domain is unknown.

```
if product(|D(args[0])|,|D(args[1])|, ..., |D(args[n])|) <= Threshold
    {fn(args[0], args[1], ..., args[n]) | args[0] in D(args[0]), args[1] in D(args[1]), ..., args[n] in D(args[n])}
else
    unknown
```

### Operation(Lambda, [vars,body]):

If any input domain is unknown, the domain is unknown.

```
same as PythonEval I guess
```
