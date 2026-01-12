# Base Types

This section documents the fundamental data types supported by the **constraint_handler**. Each type comes with its own set of operators and functions.

---

## None
To represent undefined values, the constraint handler uses `none`. Unlike a variable simply missing from a list, `none` is an explicit value that propagates through certain operations.

### Definition
```prolog
val(none, none)

```
### Output
```prolog
value(name, val(none, none))
```

### Supported Operators
| Operator | Name | Signature | Description |
| :--- | :--- | :--- | :--- |
| **Logical** | | | |
| `limp` | Implication | ([none](#none) \| [bool](#bool), [none](#none) \| [bool](#bool)) $\to$ [none](#none) | If either of the values is `none`, the result will be `none`. Otherwise, this follows the standard implication rules from [bool](#bool). |
| **Negation** | | | |
| `lnot` | Classical Negation | ([none](#none)) $\to$ [none](#none) | The negation of `none` is still `none`. |

---

## Bool
Booleans represent the logical values `true` and `false`. They are the result of comparisons and the building blocks for logical conditions.

### Definition
```prolog
val(bool, true)
val(bool, false)
```
### Output
```prolog
value(name, val(bool, true))
value(name, val(bool, false))
```

### Supported Operators
!!! info
    Some of the operators like `conj` and `disj` accept any number of arguments, these use the [list](expressions.md#list) notation as shown in the expression section. Others are strictly unary or binary.


| Operator | Name | Signature | Description |
| :--- | :--- | :--- | :--- |
| **Comparison** | | | | |
| `eq` | Equality | ([bool](#bool), [bool](#bool)) $\to$ [bool](#bool) | `true` if all arguments are equal. |
| `neq` | Inequality | ([bool](#bool), [bool](#bool)) $\to$ [bool](#bool) | `true` if not all arguments are equal. |
| **Logical** | | | | |
| `conj` | Conjunction | ([list](expressions.md#list)[[bool](#bool)]) $\to$ [bool](#bool) | `true` only if *all* arguments in the list are true. Short-circuits if `false` is found. |
| `disj` | Disjunction | ([list](expressions.md#list)[[bool](#bool)]) $\to$ [bool](#bool) | `true` if *at least one* argument in the list is true. |
| `limp` | Implication | ([bool](#bool), [bool](#bool)) $\to$ [bool](#bool) | `false` only if the first argument is `true` and the second is `false`. Otherwise `true`. | [bool](#bool) \| [none](#none) |
| `lxor` | Exclusive OR | ([list](expressions.md#list)[[bool](#bool)]) $\to$ [bool](#bool)  | `true` if an **odd** number of arguments are `true`. |
| `leqv` | Equivalence | ([list](expressions.md#list)[[bool](#bool)]) $\to$ [bool](#bool)  | `true` if an **even** number of arguments are `true`. |
| **Negation** | | | | |
| `lnot` | Logical | ([bool](#bool)) $\to$ [bool](#bool) | Standard inversion (`true` $\to$ `false`, `false` $\to$ `true`). |
| `snot` | Strong | ([bool](#bool)) $\to$ [bool](#bool) | Treats undefined/missing values as `false`. |
| `wnot` | Weak | ([bool](#bool)) $\to$ [bool](#bool) | Treats undefined/missing values as `true`. |

!!! Example
    Checking for inequality of two variables

    ```prolog
    variable_define(example, a, val(bool, true)).
    variable_define(example, b, val(bool, false)).
    variable_define(example, c, operation(neq, (variable(a), (variable(b), ())))).
    ```

    This would assign the value `true` to the variable `c`.

---

## Int
Integers represent positive and negative whole numbers. They support standard arithmetic operations as well as comparisons.

### Definition
```prolog
val(int, 42)
val(int, -7)
```
### Output
```prolog
value(name, val(int, 42))
value(name, val(int, -7))
```

### Supported Operators
| Operator | Name | Signature | Description |
| :--- | :--- | :--- | :--- |
| **Arithmetic** | | | |
| `add` | Addition | ([int](#int), [int](#int)) $\to$ [int](#int) | Adds two integers. |
| `sub` | Subtraction | ([int](#int), [int](#int)) $\to$ [int](#int) | Subtracts the second integer from the first. |
| `mult` | Multiplication | ([int](#int), [int](#int)) $\to$ [int](#int) | Multiplies two integers. |
| `div` | Integer Division | ([int](#int), [int](#int)) $\to$ [int](#int) | Divides the first integer by the second. |
| `pow` | Exponentiation | ([int](#int), [int](#int)) $\to$ [int](#int) | Raises the first integer to the power of the second. |
| `abs` | Absolute Value | ([int](#int)) $\to$ [int](#int) | Returns the absolute value of the integer. |
| `minus` | Unary Minus | ([int](#int)) $\to$ [int](#int) | Negates the integer. |
| **Trigonometry** | | | |
| `sqrt` | Square Root | ([int](#int)) $\to$ [float](#float) | Calculates the square root of the integer. |
| `sin` | Sine | ([int](#int)) $\to$ [float](#float) | Calculates the sine of the integer. |
| `cos` | Cosine | ([int](#int)) $\to$ [float](#float) | Calculates the cosine of the integer. |
| `tan` | Tangent | ([int](#int)) $\to$ [float](#float) | Calculates the tangent of the integer. |
| `asin` | Arc Sine | ([int](#int)) $\to$ [float](#float) | Calculates the inverse sine. |
| `acos` | Arc Cosine | ([int](#int)) $\to$ [float](#float) | Calculates the inverse cosine. |
| `atan` | Arc Tangent | ([int](#int)) $\to$ [float](#float) | Calculates the inverse tangent. |
| **Comparison** | | | |
| `eq` | Equality | ([int](#int), [int](#int)) $\to$ [bool](#bool) | Returns `true` if inputs are identical, otherwise `false`. |
| `neq` | Inequality | ([int](#int), [int](#int)) $\to$ [bool](#bool) | Returns `true` if inputs differ, otherwise `false`. |
| `lt` | Less Than | ([int](#int), [int](#int)) $\to$ [bool](#bool) | `true` if first is strictly less than second. |
| `leq` | Less Than or Equal | ([int](#int), [int](#int)) $\to$ [bool](#bool) | `true` if first is less than or equal to second. |
| `gt` | Greater Than | ([int](#int), [int](#int)) $\to$ [bool](#bool) | `true` if first is strictly greater than second. |
| `geq` | Greater Than or Equal | ([int](#int), [int](#int)) $\to$ [bool](#bool) | `true` if first is greater than or equal to second. |

!!! Example
    Adding two integers

    ```prolog
    variable_define(example, a, val(int, 5)).
    variable_define(example, b, val(int, 10)).
    variable_define(example, c, operation(add, (variable(a), (variable(b), ())))).
    ```
    This would assign the value `15` to the variable `c`.

---

## Float
Floats represent real numbers with fractional parts. They support a wide range of mathematical operations, including trigonometry.

!!! info
    Since neither `,` nor `.` can be used in ASP to represent floating point numbers, floats are represented by strings inside of the
    function symbol `float/1`. This means `"3.14"` is used for strings, while `float("3.14")` is used for floats.

### Definition
```prolog
val(float, float("3.14159"))
val(float, float("-0.001"))
```

### Output
```prolog
value(name, val(float, float("3.14159")))
value(name, val(float, float("-0.001")))
```

### Supported Operators
!!! info "Type Promotion" 
    If a binary operation involves one [int](#int) and one [float](#float) (e.g. the addition of an int and a float), the integer is automatically promoted to a float. The result is then calcualted as if both operands were floats.

| Operator | Name | Signature | Description |
| :--- | :--- | :--- | :--- |
| **Arithmetic** | | | |
| `add` | Addition | ([float](#float), [float](#float)) $\to$ [float](#float) | Adds two floats. |
| `sub` | Subtraction | ([float](#float), [float](#float)) $\to$ [float](#float) | Subtracts the second float from the first. |
| `mult` | Multiplication | ([float](#float), [float](#float)) $\to$ [float](#float) | Multiplies two floats. |
| `div` | Division | ([float](#float), [float](#float)) $\to$ [float](#float) | Performs integer division on two floats. |
| `fdiv` | Float Division | ([float](#float), [float](#float)) $\to$ [float](#float) | Performs explicit floating point division. |
| `floor` | Floor | ([float](#float)) $\to$ [float](#float) | Rounds the float down to the nearest integer value. |
| `pow` | Exponentiation | ([float](#float), [float](#float)) $\to$ [float](#float) | Raises the first value to the power of the second. |
| `abs` | Absolute Value | ([float](#float)) $\to$ [float](#float) | Returns the absolute value. |
| `minus` | Unary Minus | ([float](#float)) $\to$ [float](#float) | Negates the value. |
| `max` | Maximum | ([float](#float), [float](#float)) $\to$ [float](#float) | Returns the larger of the two values. |
| **Trigonometry** | | | |
| `sqrt` | Square Root | ([float](#float)) $\to$ [float](#float) | Calculates the square root. |
| `sin` | Sine | ([float](#float)) $\to$ [float](#float) | Calculates the sine. |
| `cos` | Cosine | ([float](#float)) $\to$ [float](#float) | Calculates the cosine. |
| `tan` | Tangent | ([float](#float)) $\to$ [float](#float) | Calculates the tangent. |
| `asin` | Arc Sine | ([float](#float)) $\to$ [float](#float) | Calculates the inverse sine. |
| `acos` | Arc Cosine | ([float](#float)) $\to$ [float](#float) | Calculates the inverse cosine. |
| `atan` | Arc Tangent | ([float](#float)) $\to$ [float](#float) | Calculates the inverse tangent. |
| **Comparison** | | | |
| `eq` | Equality | ([float](#float), [float](#float)) $\to$ [bool](#bool) | Returns `true` if inputs are identical, otherwise `false`. |
| `neq` | Inequality | ([float](#float), [float](#float)) $\to$ [bool](#bool) | Returns `true` if inputs differ, otherwise `false`. |
| `lt` | Less Than | ([float](#float), [float](#float)) $\to$ [bool](#bool) | `true` if first is strictly less than second. |
| `leq` | Less Than or Equal | ([float](#float), [float](#float)) $\to$ [bool](#bool) | `true` if first is less than or equal to second. |
| `gt` | Greater Than | ([float](#float), [float](#float)) $\to$ [bool](#bool) | `true` if first is strictly greater than second. |
| `geq` | Greater Than or Equal | ([float](#float), [float](#float)) $\to$ [bool](#bool) | `true` if first is greater than or equal to second. |

!!! Example
    Multiplying two floats

    ```prolog
    variable_define(example, a, val(float, float("2.5"))).
    variable_define(example, b, val(float, float("4.0"))).
    variable_define(example, c, operation(mult, (variable(a), (variable(b), ())))).
    ```
    This would assign the value `float("10.0")` to the variable `c`.

---

## String
Strings are used to represent text-based data. They support concatenation and comparison operations.

### Definition
```prolog
val(string, "Hello, World!")
val(string, "Constraint Handling")
```

### Output
```prolog
value(name, val(string, "Hello, World!"))
value(name, val(string, "Constraint Handling"))
```

| Operator | Name | Signature | Description |
| :--- | :--- | :--- | :--- |
| **Manipulation** | | | |
| `concat` | Concatenation | ([string](#string), [string](#string)) $\to$ [string](#string) | Joins two strings together. |
| `length` | Length | ([string](#string)) $\to$ [int](#int) | Returns the number of characters in the string. |
| **Comparison** | | | |
| `eq` | Equality | ([string](#string), [string](#string)) $\to$ [bool](#bool) | Returns `true` if inputs are identical, otherwise `false`. |
| `neq` | Inequality | ([string](#string), [string](#string)) $\to$ [bool](#bool) | Returns `true` if inputs differ, otherwise `false`. |

!!! Example
    Concatenating a prefix to a name.
    ```prolog
    variable_define(example, prefix, val(str, "var_")).
    variable_define(example, suffix, val(str, "x")).
    variable_define(example, full_name, operation(concat, (variable(prefix), (variable(suffix), ())))).
    ```

    This would assign the value `"var_x"` to the variable `full_name`.

---

## Symbol
Symbols represent raw ASP constants or function symbols (atoms). Unlike strings, they are not enclosed in quotes and follow standard ASP naming conventions (starting with a lowercase letter).

### Definition
```prolog
val(symbol, active)
val(symbol, state(idle))
```

### Output
```prolog
value(name, val(symbol, active))
value(name, val(symbol, state(idle)))
```
### Supported Operators
!!! info "Ordering" 
    Symbol comparison follows the standard Clingo/ASP ordering rules.

| Operator | Name | Signature | Description |
| :--- | :--- | :--- | :--- |
| **Comparison** | | | |
| `eq` | Equality | ([symbol](#symbol), [symbol](#symbol)) $\to$ [bool](#bool) | `true` if inputs are identical, otherwise `false`. |
| `neq` | Inequality | ([symbol](#symbol), [symbol](#symbol)) $\to$ [bool](#bool) | `true` if inputs differ, otherwise `false`. |
| `lt` | Less Than | ([symbol](#symbol), [symbol](#symbol)) $\to$ [bool](#bool) | `true` if first argument is smaller than the second. |
| `leq` | Less Than or Equal | ([symbol](#symbol), [symbol](#symbol)) $\to$ [bool](#bool) | `true` if first argument is smaller than or equal to the second. |
| `gt` | Greater Than | ([symbol](#symbol), [symbol](#symbol)) $\to$ [bool](#bool) | `true` if first argument is larger than the second. |
| `geq` | Greater Than or Equal | ([symbol](#symbol), [symbol](#symbol)) $\to$ [bool](#bool) | `true` if first argument is larger than or equal to the second. |

!!! Example 
    Checking if a status variable is set to error.

    ```prolog
    variable_define(system, current_status, val(symbol, error)).
    variable_define(system, is_critical, operation(eq, (variable(current_status), (val(symbol, error), ())))).
    ```

    This would assign `true` to `is_critical`.