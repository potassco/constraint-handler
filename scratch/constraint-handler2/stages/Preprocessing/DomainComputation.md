## Goal

Compute a sound domain for every expression quickly.

Let `D(x) = dom(x)`, `Threshold` be the maximum number of input combinations to
evaluate for general expressions, and `BooleanThreshold` be the maximum for
boolean-valued expressions.

Domains can contain values, are just lower/upper bound approximations, or even potential values for sets (means domain is power set of the element domain)

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

### Operation(Eq, [x,y]):
```
if product(D(x),D(y)) <= BooleanThreshold
    {a == b | a in D(x), b in D(y)}
else
    {true, false}
```

### Operation(Neq, [x,y]):
```
if product(D(x),D(y)) <= BooleanThreshold
    {a != b | a in D(x), b in D(y)}
else
    {true, false}
```

### Operation(Concat, [x,y]):
```
{a + b | a in D(x), b in D(y)}
```

### Operation(Length, [x]):
```
{len(a) | a in D(x)}
```

### Operation(Min, [x1,...,xn]):
```
{min(v1,...,vn) | vi in D(xi)}
```

### Operation(Max, [x1,...,xn]):
```
{max(v1,...,vn) | vi in D(xi)}
```

### Operation(GetOrElse, [x,y]):
```
(D(x) - {None}) union D(y), if None in D(x); else D(x)
```

### Operation(If, [c,x]):
```
D(x) union {None}, if false or None in D(c); else D(x)
```

### Operation(Ite, [c,x,y]):
```
D(x) if D(c)={true}; D(y) if D(c)={false}; else D(x) union D(y)
```

### Operation(HasValue, [x]):
```
{v is not None | v in D(x)}
```

### Operation(Abs, [x]):
```
{abs(v) | v in D(x)}
```

### Operation(Sqrt, [x]):
```
{sqrt(v) | v in D(x) where v >= 0}
# error/warning for negative values in D(x)
```

### Operation(Cos, [x]):
```
{cos(v) | v in D(x)}
```

### Operation(Sin, [x]):
```
{sin(v) | v in D(x)}
```

### Operation(Tan, [x]):
```
{tan(v) | v in D(x) where v is not an odd multiple of pi/2}
# error/warning for odd multiples of pi/2 in D(x)
```

### Operation(Acos, [x]):
```
{acos(v) | v in D(x) where v in [-1,1]}
# error/warning for values outside [-1,1] in D(x)
```

### Operation(Asin, [x]):
```
{asin(v) | v in D(x) where v in [-1,1]}
# error/warning for values outside [-1,1] in D(x)
```

### Operation(Atan, [x]):
```
{atan(v) | v in D(x)}
```

### Operation(Minus, [x]):
```
{-v | v in D(x)}
```

### Operation(Floor, [x]):
```
{floor(v) | v in D(x)}
```

### Operation(Ceil, [x]):
```
{ceil(v) | v in D(x)}
```

### Operation(Add, [x1,...,xn]):
```
if product(D(x1),...,D(xn)) <= Threshold
    {sum(v1,...,vn) | vi in D(xi)}
else
    [sum(min(D(xi))),sum(max(D(xi)))]
```

### Operation(Sub, [x,y]):
```
if product(D(x),D(y)) <= Threshold
    {a - b | a in D(x), b in D(y)}
else
    [min(D(x))-max(D(y)),max(D(x))-min(D(y))]
```

### Operation(Mult, [x1,...,xn]):
```
if product(D(x1),...,D(xn)) <= Threshold
    {prod(v1,...,vn) | vi in D(xi)}
else
    fold interval multiplication from 1; [a,b]*[c,d]=[min(ac,ad,bc,bd),max(ac,ad,bc,bd)]
```

### Operation(IntDiv, [x,y]):
```
if product(|D(x)|,|D(y)|) <= Threshold
    {a // b | a in D(x), b in D(y), b != 0}
else
    B = {b in D(y) | b != 0}
    if D(x) = {} or B = {}
        {}
    else
        M = max(abs(min(D(x))),abs(max(D(x))))
        m = min(abs(b) | b in B)
        [-ceil(M/m),ceil(M/m)]
# error/warning if 0 in D(y)
```

### Operation(FloatDiv, [x,y]):
```
if product(|D(x)|,|D(y)|) <= Threshold
    {a / b | a in D(x), b in D(y), b != 0}
else
    B = {b in D(y) | b != 0}
    if D(x) = {} or B = {}
        {}
    else
        M = max(abs(min(D(x))),abs(max(D(x))))
        m = min(abs(b) | b in B)
        [-M/m,M/m]
# error/warning if 0 in D(y)
```

### Operation(Pow, [x,y]):
```
if D(y) = {0}
    {1}
else if D(y) = {1}
    D(x)
else if product(|D(x)|,|D(y)|) <= Threshold
    {a ** b | a in D(x), b in D(y), a ** b is defined and real}
else if D(x) = {} or D(y) = {}
    {}
else
    A = max(|a| | a in D(x))
    E = max(|b| | b in D(y))
    if A = 0
        R = 1
    else
        m = min(|a| | a in D(x), a != 0)
        R = max(1, A ** E, m ** (-E))
    [-R,R]
# error/warning for undefined or non-real powers
```

### Operation(FloatFromInt, [x]):
```
{float(v) | v in D(x)}
```

### Operation(IntFromFloat, [x]):
```
{int(v) | v in D(x)}
```

### Operation(Leq, [x,y]):
```
{true} if max(D(x)) <= min(D(y))
{false} if min(D(x)) > max(D(y))

if product(|D(x)|,|D(y)|) <= BooleanThreshold
    {x <= y | x in D(x), y in D(y)}
else
    {true,false}
```

### Operation(Lt, [x,y]):
```
{true} if max(D(x)) < min(D(y))
{false} if min(D(x)) >= max(D(y))

if product(|D(x)|,|D(y)|) <= BooleanThreshold
    {a < b | a in D(x), b in D(y)}
else
    {true,false}
```

### Operation(Geq, [x,y]):
```
{true} if min(D(x)) >= max(D(y))
{false} if max(D(x)) < min(D(y))

if product(|D(x)|,|D(y)|) <= BooleanThreshold
    {a >= b | a in D(x), b in D(y)}
else
    {true,false}
```

### Operation(Gt, [x,y]):
```
{true} if min(D(x)) > max(D(y))
{false} if max(D(x)) <= min(D(y))

if product(|D(x)|,|D(y)|) <= BooleanThreshold
    {a > b | a in D(x), b in D(y)}
else
    {true,false}
```

### Operation(Conj, [x1,...,xn]):
```
if product(|D(x1)|,...,|D(xn)|) <= BooleanThreshold
    {and(v1,...,vn) | vi in D(xi)}
else
    {true,false}
```

### Operation(Disj, [x1,...,xn]):
```
if product(|D(x1)|,...,|D(xn)|) <= BooleanThreshold
    {or(v1,...,vn) | vi in D(xi)}
else
    {true,false}
```

### Operation(Leqv, [x1,...,xn]):
```
???
```

### Operation(Limp, [x,y]):
```
if product(|D(x)|,|D(y)|) <= BooleanThreshold
    {not a or b | a in D(x), b in D(y)}
else
    {true,false}
```

### Operation(Lnot, [x]):
```
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
if product(|D(x1)|,...,|D(xn)|) <= BooleanThreshold
    {xor(v1,...,vn) | vi in D(xi)}
else
    {true,false}
```

### Operation(Snot, [x]):
```
R = {}
if true in D(x) or None in D(x)
    R = R union {false}
if false in D(x)
    R = R union {true}
R
```

### Operation(Wnot, [x]):
```
R = {}
if true in D(x)
    R = R union {false}
if false in D(x) or None in D(x)
    R = R union {true}
R
```

### Operation(Cardinality, [x]):
```
{ size(v) | v in D(x)}
```

### Operation(SetMake, [x1,...,xn]):
```
{{v1,...,vn} | vi in D(xi)}
```

### Operation(SetIsIn, [x,s]):
```
if product(|D(x)|,|D(s)|) <= BooleanThreshold
    {a in S | a in D(x), S in D(s)}
else
    {true,false}
```

### Operation(SetNotIn, [x,s]):
```
if product(|D(x)|,|D(s)|) <= BooleanThreshold
    {a not in S | a in D(x), S in D(s)}
else
    {true,false}
```

### Operation(Union, [x,y]):
```
if product(|D(x)|,|D(y)|) <= Threshold
    {A union B | A in D(x), B in D(y)}
else
    P(U)  # represented by possible elements U

where U = union(A | A in D(x)) union union(B | B in D(y))
```

### Operation(Inter, [x,y]):
```
if product(|D(x)|,|D(y)|) <= Threshold
    {A inter B | A in D(x), B in D(y)}
else
    P(U)  # represented by possible elements U

where U = union(A | A in D(x)) union union(B | B in D(y))
```

### Operation(Diff, [x,y]):
```
if product(|D(x)|,|D(y)|) <= Threshold
    {A - B | A in D(x), B in D(y)}
else
    P(U)  # represented by possible elements U

where U = union(A | A in D(x)) union union(B | B in D(y))
```

### Operation(Subset, [x,y]):
```
if product(|D(x)|,|D(y)|) <= Threshold
    {A subseteq B | A in D(x), B in D(y)}
else
    {true,false}
```

### Operation(SetFold, [f,s,z]):
```
fold f over S in D(s), starting with z in D(z)
# complete domain computation
```

### Operation(Find, [k,m]):
```
{m[k] if k in m else {} | k in D(k), m in D(m)}
```

### Operation(Find2, [k,v,m]):
```
{k in m and v in m[k] | k in D(k), v in D(v), m in D(m)}
```

### Operation(MultimapIsIn, [k,m]):
```
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
```
if product(|D(args[0])|,|D(args[1])|, ..., |D(args[n])|) <= Threshold
    {fn(args[0], args[1], ..., args[n]) | args[0] in D(args[0]), args[1] in D(args[1]), ..., args[n] in D(args[n])}
else
    unknown
```

### Operation(Lambda, [vars,body]):
```
same as PythonEval I guess
```
