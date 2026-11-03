# Operator Semantics

This document defines the meaning of expression operators independently of
whether an expression was supplied through the ASP or Python input interface.
Input formats encode operation names and arguments differently; after
internalization, an operation denotes the same mathematical operation in
either format. Input-specific spellings are listed where they are known.

An operator is applied to the values of its arguments. The contracts below
describe valid argument types and the value produced for valid inputs.
Expressions may also be undefined, and/or produce
diagnostics during evaluation and runtime.

General Rules:
 - An error is raised if an invalid arity is supplied to an operator.
 - Type Errors depend only on argument types and arity
 - Runtime Errors depend on argument values
 - Any float that is equivalent to an integer can be converted to an integer

Definitions:
 - Parameters are denoted as x1, x2, ..., xn for n arguments.
 - out denotes the output of an operator.
 - defined(X) is true if all x in X are defined, false otherwise.
 - number(x) denotes the numeric value of `x` if `x` is an integer or float, x otherwise
 - ANY_TYPE = {bool, None, int, float, string, tuple, set} % no lambda
 - The comparison `==` (and `in`, set construction) in the formulas below is mathematical equality, not Python's: values of different types are unequal (`1 == true` is false), int and float compare by numeric value, and tuples and sets compare element-wise under the same rule.

# Types:

bool: {true, false}
None: {None}
int: the set of all integers
float: the set of all floats
string: the set of all strings
tuple: a tuple of bool, None, int, float, string, set % not nested
set: a set of bool, None, int, float, string
lambda: a callable operation

# Comparison Operators

## eq

### Arity:
n=2

### Types:
x1, ..., xn in ANY_TYPE

out in {bool}

### Semantics:
```
if defined({x1, x2})
  out = (number(x1) == number(x2))
else
  out = undefined
```

### Warnings:
```
if type(x1) != type(x2) and not {type(x1), type(x2)} <= {int, float}
  warn("Comparing values of different types")
```

## neq

### Arity:
n=2

### Types:
x1, ..., xn in ANY_TYPE

out in {bool}

### Semantics:
```
if defined({x1, x2})
  out = (number(x1) != number(x2))
else
  out = undefined
```

### Warnings:
```
if type(x1) != type(x2) and not {type(x1), type(x2)} <= {int, float}
  warn("Comparing values of different types")
```

## lt

### Arity:
n=2

### Types:
x1, ..., xn in {int, float}

out in {bool}

### Semantics:
```
if defined({x1, x2})
  out = (number(x1) < number(x2))
else
  out = undefined
```

### Type Errors:
```
if not {type(x1), type(x2)} <= {int, float}
  error("Unsupported comparison type")
```

## leq

### Arity:
n=2

### Types:
x1, ..., xn in {int, float}

out in {bool}

### Semantics:
```
if defined({x1, x2})
  out = (number(x1) <= number(x2))
else
  out = undefined
```

### Type Errors:
```
if not {type(x1), type(x2)} <= {int, float}
  error("Unsupported comparison type")
```

## gt

### Arity:
n=2

### Types:
x1, ..., xn in {int, float}

out in {bool}

### Semantics:
```
if defined({x1, x2})
  out = (number(x1) > number(x2))
else
  out = undefined
```

### Type Errors:
```
if not {type(x1), type(x2)} <= {int, float}
  error("Unsupported comparison type")
```

## geq

### Arity:
n=2

### Types:
x1, ..., xn in {int, float}

out in {bool}

### Semantics:
```
if defined({x1, x2})
  out = (number(x1) >= number(x2))
else
  out = undefined
```

### Type Errors:
```
if not {type(x1), type(x2)} <= {int, float}
  error("Unsupported comparison type")
```

# None operators

## hasValue

### Arity:
n=1

### Types:
x1 in ANY_TYPE

out in {bool}

### Semantics:
```
if defined({x1})
  out = (x1 != None)
else
  out = undefined
```

## get_or_else

### Arity:
n=2

### Types:
x1, x2 in ANY_TYPE

out in ANY_TYPE

### Semantics:
```
if defined({x1, x2})
  if x1 != None
    out = x1
  else
    out = x2
else
  out = undefined
```

## if_

### Arity:
n=2

### Types:
x1 in {bool}
x2 in ANY_TYPE

out in {type(x2), None}

### Semantics:
```
if defined({x1})
  if x1 == true
    out = x2
  else
    out = None
else
  out = undefined
```

# Arithmetic operators

## abs

### Arity:
n=1

### Types:
x1 in {int, float}

out in {int, float}

### Semantics:
```
if defined({x1})
  out = abs(number(x1))
else
  out = undefined
```

### Type Errors:
```
if not {type(x1)} <= {int, float}
  error("Unsupported arithmetic type")
```

## minus
**should we support this, could be mult(x, -1)**

### Arity:
n=1

### Types:
x1 in {int, float}

out in {int, float}

### Semantics:
```
if defined({x1})
  out = -number(x1)
else
  out = undefined
```

### Type Errors:
```
if not {type(x1)} <= {int, float}
  error("Unsupported arithmetic type")
```

## add
**should we support more than two arguments?**

### Arity:
n=2

### Types:
x1, x2 in {int, float}

out in {int, float}

### Semantics:
```
if defined({x1, x2})
  out = number(x1) + number(x2)
else
  out = undefined
```

### Type Errors:
```
if not {type(x1), type(x2)} <= {int, float}
  error("Unsupported arithmetic type")
```

## sub
**should we support more than two arguments?**

### Arity:
n=2

### Types:
x1, x2 in {int, float}

out in {int, float}

### Semantics:
```
if defined({x1, x2})
  out = number(x1) - number(x2)
else
  out = undefined
```

### Type Errors:
```
if not {type(x1), type(x2)} <= {int, float}
  error("Unsupported arithmetic type")
```

## mult

### Arity:
n=2

### Types:
x1, x2 in {int, float}

out in {int, float}

### Semantics:
```
if x1 == 0 or x2 == 0
  out = 0
elif defined({x1, x2})
  out = number(x1) * number(x2)
else
  out = undefined
```

### Type Errors:
```
if not {type(x1), type(x2)} <= {int, float}
  error("Unsupported arithmetic type")
```

## int_div

### Arity:
n=2

### Types:
x1, x2 in {int, float}

out in {int}

### Semantics:
```
if x2 == 0
  out = undefined
elif defined({x1, x2})
  out = number(x1) // number(x2)    % floor division, rounded towards negative infinity
else
  out = undefined
```

### Warnings:
```
if x2 == 0
  warning("Division by zero")
```

### Type Errors:
```
if not {type(x1), type(x2)} <= {int, float}
  error("Unsupported arithmetic type")
```

## mod

### Arity:
n=2

### Types:
x1, x2 in {int, float}

out in {int, float}

### Semantics:
```
if x2 == 0
  out = undefined
elif defined({x1, x2})
  if type(x1) == int and type(x2) == int
    out = x1 - x2 * (x1 // x2)    % floored remainder; sign follows x2
  else
    out = number(x1) - number(x2) * floor(number(x1) / number(x2))
else
  out = undefined
```

### Warnings:
```
if x2 == 0
  warning("Division by zero")
```

### Type Errors:
```
if not {type(x1), type(x2)} <= {int, float}
  error("Unsupported arithmetic type")
```

## float_div

### Arity:
n=2

### Types:
x1, x2 in {int, float}

out in {float, int}

### Semantics:
```
if x2 == 0
  out = undefined
elif defined({x1, x2})
  out = number(x1) / number(x2)    % true division
else
  out = undefined
```

### Warnings:
```
if x2 == 0
  warning("Division by zero")
```

### Type Errors:
```
if not {type(x1), type(x2)} <= {int, float}
  error("Unsupported arithmetic type")
```

## pow

### Arity:
n=2

### Types:
x1, x2 in {int, float}

out in {int, float}

### Semantics:
```
if (x1 == 0 and x2 < 0)
  out = undefined
elif (x1 < 0 and x2 != floor(x2))
  out = undefined
elif defined({x1, x2})
  out = number(x1) ** number(x2)
else
  out = undefined
```

### Warnings:
```
if (x1 == 0 and x2 < 0)
  warning("Zero to a negative power")
elif (x1 < 0 and x2 != floor(x2))
  warning("Negative number to a non-integer power")
```

### Type Errors:
```
if not {type(x1), type(x2)} <= {int, float}
  error("Unsupported arithmetic type")
```

## max/min

### Arity:
n>=1

### Types:
x1, ..., xn in {int, float}

out in {int, float}

### Semantics:
```
if defined({x1, ..., xn})
  out = max/min(number(x1), ..., number(xn))
else
  out = undefined
```

### Type Errors:
```
if not {type(x1), ..., type(xn)} <= {int, float}
  error("Unsupported arithmetic type")
```

## sqrt

### Arity:
n=1

### Types:
x1 in {int, float}

out in {float, int}

### Semantics:
```
if x1 < 0
  out = undefined
elif defined({x1})
  out = sqrt(number(x1))
else
  out = undefined
```

### Warnings:
```
if x1 < 0
  warning("Square root of a negative number")
```

### Type Errors:
```
if not {type(x1)} <= {int, float}
  error("Unsupported arithmetic type")
```

## sin/cos/tan

### Arity:
n=1

### Types:
x1 in {int, float}

out in {float, int}

### Semantics:
```
if defined({x1})
  out = sin/cos/tan(number(x1))
else
  out = undefined
```

### Type Errors:
```
if not {type(x1)} <= {int, float}
  error("Unsupported arithmetic type")
```

## atan

### Arity:
n=1

### Types:
x1 in {int, float}

out in {float, int}

### Semantics:
```
if defined({x1})
  out = atan(number(x1))
else
  out = undefined
```

### Type Errors:
```
if not {type(x1)} <= {int, float}
  error("Unsupported arithmetic type")
```

## asin/acos

### Arity:
n=1

### Types:
x1 in {int, float}

out in {float, int}

### Semantics:
```
if x1 < -1 or x1 > 1
  out = undefined
elif defined({x1})
  out = asin/acos(number(x1))
else
  out = undefined
```

### Type Errors:
```
if not {type(x1)} <= {int, float}
  error("Unsupported arithmetic type")
```

### Runtime Errors:
```
if x1 < -1 or x1 > 1
  error("asin/acos requires -1 <= x1 <= 1")
```

## floor

### Arity:
n=1

### Types:
x1 in {int, float}

out in {int}

### Semantics:
```
if defined({x1})
  out = floor(number(x1))
else
  out = undefined
```

### Type Errors:
```
if not {type(x1)} <= {int, float}
  error("Unsupported arithmetic type")
```

## ceil

### Arity:
n=1

### Types:
x1 in {int, float}

out in {int}

### Semantics:
```
if defined({x1})
  out = ceil(number(x1))
else
  out = undefined
```

### Type Errors:
```
if not {type(x1)} <= {int, float}
  error("Unsupported arithmetic type")
```

# Boolean logic operators

## lnot

### Arity:
n=1

### Types:
x1 in {bool}

out in {bool}

### Semantics:
```
if defined({x1})
  out = true if x1==false else false
else
  out = undefined
```

### Type Errors:
```
if not {type(x1)} <= {bool}
  error("Unsupported boolean type")
```

## conj

### Arity:
n >= 0

### Types:
x1, ..., xn in {bool}

out in {bool}

### Semantics:
```
if n == 0
  out = true
elif false in {x1, ..., xn}
  out = false
elif defined({x1, ..., xn})
  out = x1 and x2 and ... and xn
else
  out = undefined
```

### Type Errors:
```
if not {type(x1), ..., type(xn)} <= {bool}
  error("Unsupported boolean type")
```

## disj

### Arity:
n >= 0

### Types:
x1, ..., xn in {bool}

out in {bool}

### Semantics:
```
if n == 0
  out = false
elif true in {x1, ..., xn}
  out = true
elif defined({x1, ..., xn})
  out = x1 or x2 or ... or xn
else
  out = undefined
```

### Type Errors:
```
if not {type(x1), ..., type(xn)} <= {bool}
  error("Unsupported boolean type")
```

## limp

### Arity:
n = 2

### Types:
x1, x2 in {bool}

out in {bool}

### Semantics:
```
if x1 == false or x2 == true
  out = true
elif defined({x1, x2})
  out = (not x1) or x2
else
  out = undefined
```

### Type Errors:
```
if not {type(x1), type(x2)} <= {bool}
  error("Unsupported boolean type")
```

## lxor

### Arity:
n >= 0

### Types:
x1, ..., xn in {bool}

out in {bool}

### Semantics:
```
if n == 0
  out = false
elif n == 1
  out = x1
elif defined({x1, ..., xn})
  out = x1 xor x2 xor ... xor xn
else
  out = undefined
```

### Type Errors:
```
if not {type(x1), ..., type(xn)} <= {bool}
  error("Unsupported boolean type")
```

## leqv

### Arity:
n >= 0

### Types:
x1, ..., xn in {bool}

out in {bool}

### Semantics:
```
% true iff the number of false operands is even (covers n == 0 and n == 1)
if defined({x1, ..., xn})
  out = (count of i where xi == false) % 2 == 0
else
  out = undefined
```

### Type Errors:
```
if not {type(x1), ..., type(xn)} <= {bool}
  error("Unsupported boolean type")
```

## snot

### Arity:
n = 1

### Types:
x1 in {bool, None}

out in {bool}

### Semantics:
```
if defined({x1})
  if x1 == true or x1 == None
    out = false
  elif x1 == false
    out = true
else
  out = undefined
```

### Type Errors:
```
if not {type(x1)} <= {bool, None}
  error("Unsupported boolean or None type")
```

## wnot

### Arity:
n = 1

### Types:
x1 in {bool, None}

out in {bool}

### Semantics:
```
if defined({x1})
  if x1 == false
    out = false
  elif x1 == true or x1 == None
    out = true
else
  out = undefined
```

### Type Errors:
```
if not {type(x1)} <= {bool, None}
  error("Unsupported boolean or None type")
```

## ite

### Arity:
n=3

### Types:
x1 in {bool}
x2, x3 in ANY_TYPE

out in {type(x2), type(x3)}

### Semantics:
```
if defined({x1})
  if x1 == true
    out = x2
  else
    out = x3
else
  out = undefined
```

### Type Errors:
```
if not {type(x1)} <= {bool}
  error("Unsupported boolean type")
```

# String Operators

## concat

### Arity:
n == 2

### Types:
x1, x2 in {string}

out in {string}

### Semantics:
```
if defined({x1, x2})
  out = x1 + x2
else
  out = undefined
```

### Type Errors:
```
if not {type(x1), type(x2)} <= {string}
  error("Unsupported string type")
```

# Mixed Operators

## length

### Arity:
n = 1

### Types:
x1 in {string, set, tuple}

out in {int}

### Semantics:
```
if defined({x1})
  if type(x1) == string
    out = len(x1)
  elif type(x1) == set
    out = |x1|
  elif type(x1) == tuple
    out = |x1|
  else
    out = undefined
else
  out = undefined
```

### Type Errors:
```
if not type(x1) in {string, set, tuple}
  error("Unsupported type for length operator")
```

# Tuple Operators

## make_tuple

### Arity:
n >= 0

### Types:
x1, ..., xn in {int, float, bool, string, None, set}

out in {tuple}

### Semantics:
```
if defined({x1, ..., xn})
  out = (x1, ..., xn)
else
  out = undefined
```

## tuple_index

### Arity:
n = 2

### Types:
x1 in {tuple}
x2 in {int}

out in ANY_TYPE

### Semantics:
```
if defined({x1, x2})
  if 0 <= x2 < |x1|
    out = x1[x2]
  else
    out = undefined
else
  out = undefined
```

### Type Errors:
```
if not type(x1) == tuple
  error("Unsupported type for tuple_index operator")
if not type(x2) == int
  error("Index must be an integer")
```

### Runtime Errors:
```
if x2 < 0 or x2 >= |x1|
  error("Index out of bounds")
```

# Set Operators

## set_make

### Arity:
n >= 0

### Types:
x1, ..., xn in {int, float, bool, string, None}

out in {set}

### Semantics:
```
if defined({x1, ..., xn})
  out = {x1, ..., xn}
else
  out = undefined
```

### Type Errors:
```
if not {type(x1), ..., type(xn)} <= {int, float, bool, string, None}
  error("Unsupported type for set_make operator")
```

## set_isin

### Arity:
n = 2

### Types:
x1 in {int, float, bool, string, None}
x2 in {set}

out in {bool}

### Semantics:
```
if defined({x1, x2})
  out = x1 in x2
else
  out = undefined
```

### Type Errors:
```
if not type(x1) in {int, float, bool, string, None}
  error("Unsupported type for set_isin operator")
if not type(x2) == set
  error("Second argument must be a set")
```

## set_notin
**do we really need this, could be expressed as `not set_isin(x1, x2)`**

### Arity:
n = 2

### Types:
x1 in {int, float, bool, string, None}
x2 in {set}

out in {bool}

### Semantics:
```
if defined({x1, x2})
  out = x1 not in x2
else
  out = undefined
```

### Type Errors:
```
if not type(x1) in {int, float, bool, string, None}
  error("Unsupported type for set_notin operator")
if not type(x2) == set
  error("Second argument must be a set")
```

## union

### Arity:
n >= 0

### Types:
x1, ..., xn in {set}

out in {set}

### Semantics:
```
if n == 0
  out = {}
elif defined({x1, ..., xn})
  out = union({x1, ..., xn})
else
  out = undefined
```

### Type Errors:
```
if not {type(x1), ..., type(xn)} <= {set}
  error("Unsupported type for union operator")
```

## inter

### Arity:
n >= 1

### Types:
x1, ..., xn in {set}

out in {set}

### Semantics:
```
if defined({x1, ..., xn})
  out = inter({x1, ..., xn})
else
  out = undefined
```

### Type Errors:
```
if not {type(x1), ..., type(xn)} <= {set}
  error("Unsupported type for inter operator")
```

## diff

### Arity:
n = 2

### Types:
x1, x2 in {set}

out in {set}

### Semantics:
```
if defined({x1, x2})
  out = x1 - x2
else
  out = undefined
```

### Type Errors:
```
if not {type(x1), type(x2)} <= {set}
  error("Unsupported type for diff operator")
```

## subset

### Arity:
n = 2

### Types:
x1, x2 in {set}

out in {bool}

### Semantics:
```
if defined({x1, x2})
  out = x1 <= x2
else
  out = undefined
```

### Type Errors:
```
if not {type(x1), type(x2)} <= {set}
  error("Unsupported type for subset operator")
```

# Callables

## set_fold
The lambda's first parameter is bound to the set element and its second
parameter to the accumulator. The iteration order over the set is not specified,
so the lambda must give the same result for every order.

### Arity:
n = 3

### Types:
x1 in {lambda}
x2 in {set}
x3 in ANY_TYPE

out in ANY_TYPE

### Semantics:
```
% m = number of parameters of x1; requires m == 2
if defined({x1, x2, x3})
  acc = x3
  for each e in x2
    acc = body(x1) evaluated with p1 bound to e and p2 bound to acc
    if acc is undefined
      out = undefined
      stop
  out = acc
else
  out = undefined
```
Any undefined step makes `out` undefined.

### Type Errors:
```
if type(x1) != lambda
  error("set_fold requires a Lambda as first argument")
if type(x2) != set
  error("set_fold requires a set as second argument")
```

### Runtime Errors:
```
if m != 2
  error("set_fold requires a Lambda with 2 parameters")
```

### Example:
```
% set_fold(lambda x, acc: x + acc, {1, 2, 3}, 0)
%   f(1, 0) = 1, f(2, 1) = 3, f(3, 3) = 6
out = 6
```

## lambda_call
Lambda parameters are local to the call and shadow variables of the same name
in outer scopes.

### Arity:
n >= 1 (x1 is the lambda, followed by one argument per lambda parameter)

### Types:
x1 in {lambda}
x2, ..., xn in ANY_TYPE

out in ANY_TYPE

### Semantics:
```
% m = number of parameters of x1; requires n - 1 == m
if defined({x1, ..., xn})
  out = body(x1) evaluated with parameter p_i bound to x_(i+1)
else
  out = undefined
```
The body's own result may be undefined, which makes `out` undefined.

### Type Errors:
```
if type(x1) != lambda
  error("lambda_call requires a Lambda as first argument")
```

### Runtime Errors:
```
if n - 1 != m
  error("Lambda expects m arguments, got n - 1")
```

### Example:
```
% lambda_call(lambda x: x + 1, 5)
%   body(x1) = x + 1, with x bound to 5
out = 5 + 1 = 6
```

## python_call
Python callbacks must be deterministic and side-effect-free
for domain computation to remain sound. Python source is trusted executable
input, not sandboxed code.

### Arity:
n >= 1 (x1 is the Python source, followed by the arguments passed to the callable)

### Types:
fn = x1 in {string}
x2, ..., xn in ANY_TYPE

out in ANY_TYPE

### Semantics:
```
% fn = eval(x1)
% fn is called positionally; parameter names inside the source are not used
if defined({x2, ..., xn})
  out = fn(x2, ..., xn)
else
  out = undefined
```
A set result is converted to a frozenset.

### Warnings:
```
if fn raises ArithmeticError, LookupError, TypeError or ValueError for defined arguments
  warning("Python callable failed")
  out = undefined for this input
if fn raises FailIntegrityExn for defined arguments
  out = undefined for this input
```

### Runtime Errors:
```
if fn is not callable
  error("Python source must evaluate to a callable")
if fn does not accept n - 1 positional arguments
  error("Python callable arity mismatch")
if type(out) not in ANY_TYPE
  error("Unsupported Python result type")
```

### Example:
```
% python_call("lambda value: external_abs(value)", -3)
%   fn = eval("lambda value: external_abs(value)")
%   out = fn(-3) = abs(-3) = 3
```

# Internal operators
**should we make them available for general use?**

## linear_integer
This operator denotes a linear combination of integer-valued terms with integer coefficients and an integer offset.

### Arity and Types:
n = number of terms (including the offset)
each term xi is a tuple of the form (coefficient, variable) where the coefficient is an integer (constant) and the variable of type int.

out in {int}

### Semantics:
```
if n == 0
    offset = 0
else
    offset = xn

for i in {1, ..., n-1}
    if xi_1 == 0
        pi = 0
    elif defined({xi_1, xi_2})
        pi = xi_1 * xi_2
    else
        pi = undefined

if defined({p1, ..., p(n-1), offset})
    out = p1 + p2 + ... + p(n-1) + offset
else
    out = undefined
```

### Type Errors:
```
if not all({type(xi_1)} is integer constant for i in {1, ..., n-1})
    error("Coefficient must be an integer constant")
if not all({type(xi_2)} <= {int} for i in {1, ..., n-1})
    error("Variable must be of type int")
if not offset is integer constant
    error("Offset must be an integer constant")
```

## linear_comparison
This operator denotes a linear combination of integer-valued terms with integer coefficients and an integer offset and a comparison relation against 0.

### Arity and Types:
n >= 2
n = number of terms (including the offset and the relation symbol)
the first term x1 is the relation symbol, which must be one of {"lt", "leq", "eq", "neq", "geq", "gt"} as a constant string.
each term xi for i in {2, ..., n-1} is a tuple of the form (coefficient, variable) where the coefficient is an integer (constant) and the variable of type int.
the last term xn is the integer constant offset.

out in {bool}

### Semantics:
```
relation = x1
offset = xn

for i in {2, ..., n-1}
    if xi_1 == 0
        pi = 0
    elif defined({xi_1, xi_2})
        pi = xi_1 * xi_2
    else
        pi = undefined

if defined({p2, ..., p(n-1), offset})
  lhs = p2 + ... + p(n-1) + offset
  if relation == "lt"
        out = lhs < 0
  elif relation == "leq"
        out = lhs <= 0
  elif relation == "eq"
        out = lhs == 0
  elif relation == "neq"
        out = lhs != 0
  elif relation == "geq"
        out = lhs >= 0
  elif relation == "gt"
        out = lhs > 0
    else
        out = undefined
else
    out = undefined
```

### Type Errors:
```
if not all({type(xi_1)} is integer constant for i in {2, ..., n-1})
    error("Coefficient must be an integer constant")
if not all({type(xi_2)} <= {int} for i in {2, ..., n-1})
    error("Variable must be of type int")
if not offset is integer constant
    error("Offset must be an integer constant")
if not relation in {"lt", "leq", "eq", "neq", "geq", "gt"}
  error("Relation must be one of {lt, leq, eq, neq, geq, gt}")
```

## TODO: Input spelling

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