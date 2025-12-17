# Base Types

This section documents the fundamental data types supported by the **constraint_handler**. Each type comes with its own set of operators and functions.

---

## None
To represent undefined values, the constraint handler uses `none`. Unlike a variable simply missing from a list, `none` is an explicit value that propagates through certain operations.

### Definition
```asp
val(none, none)

```
### Output
```asp
value(name, none, none)
```

### Supported Operators
| Operator | Name | Arity | Description | Return Type |
| :--- | :--- | :--- | :--- | :--- |
| **Logical** | | | | |
| `limp` | Implication | 2 | If either of the values is `none`, the result will be `none`. Otherwise, this follows the standard implication rules from [bool](#bool). | [none](#none) |
| **Negation** | | | | |
| `lnot` | Classical Negation | 1 | The negation of `none` is still `none`. | [none](#none) |

---

## Bool
Booleans represent the logical values `true` and `false`. They are the result of comparisons and the building blocks for logical conditions.

### Definition
```asp
val(bool, true)
val(bool, false)
```
### Output
```asp
value(name, bool, true)
value(name, bool, false)
```

### Supported Operators
!!! info
    Some of the operators like `conj` and `disj` accept any number of arguments, these are declared *N-ary*.
    Others are strictly unary or binary.


| Operator | Name | Arity | Description | Return Type |
| :--- | :--- | :--- | :--- | :--- |
| **Comparison** | | | | |
| `eq` | Equality | 2 | `true` if `A` is equal to `B`. | [bool](#bool) |
| `neq` | Inequality | 2 | `true` if `A` is not equal to `B`. | [bool](#bool) |
| **Logical** | | | | |
| `conj` | Conjunction | N-ary | `true` only if *all* arguments in the list are true. Short-circuits if `false` is found. | [bool](#bool) |
| `disj` | Disjunction | N-ary | `true` if *at least one* argument in the list is true. | [bool](#bool) |
| `limp` | Implication | 2 | `false` only if the first argument is `true` and the second is `false`. Otherwise `true`. If either of the values is empty, the result will be empty as well. | [bool](#bool) \| [none](#none) |
| `lxor` | Exclusive OR | N-ary  | `true` if an **odd** number of arguments are `true`. | [bool](#bool) |
| `leqv` | Equivalence | N-ary  | `true` if an **even** number of arguments are `true`. | [bool](#bool) |
| **Negation** | | | | |
| `lnot` | Logical Negation | 1 | Standard inversion (`true` $\to$ `false`, `false` $\to$ `true`). Requires a defined value. | [bool](#bool) |
| `snot` | Strong Negation | 1 | Treats undefined/missing values as `false`. | [bool](#bool) |
| `wnot` | Weak Negation | 1 | Treats undefined/missing values as `true`. | [bool](#bool) |

!!! Example
    Checking for inequality of two variables

    ```asp
    assign(example, a, val(bool, true)).
    assign(example, b, val(bool, false)).
    assign(example, c, operation(neq, (variable(a), (variable(b), ())))).
    ```

    This would assign the value `true` to the variable `c`.

---

## Int
Integers represent positive and negative whole numbers. They support standard arithmetic operations as well as comparisons.

### Definition
```asp
val(int, 42)
val(int, -7)
```
### Output
```asp
value(name, int, 42)
value(name, int, -7)
```

### Supported Operators
| Operator | Name | Arity | Description | Return Type |
| :--- | :--- | :--- | :--- | :--- |
| **Arithmetic** | | | | |
| `add` | Addition | 2 | Adds two integers (`A + B`). | [int](#int) |
| `sub` | Subtraction | 2 | Subtracts the second integer from the first (`A - B`). | [int](#int) |
| `mult` | Multiplication | 2 | Multiplies two integers (`A * B`). | [int](#int) |
| `div` | Integer Division | 2 | Divides the first integer by the second (`A / B`). | [int](#int) |
| `pow` | Exponentiation | 2 | Raises the first integer to the power of the second (`A ^ B`). | [int](#int) |
| `abs` | Absolute Value | 1 | Returns the absolute value of the integer (`|A|`). | [int](#int) |
| `minus` | Unary Minus | 1 | Negates the integer (`-A`). | [int](#int) |
| **Trigonometry** | | | | |
| `sqrt` | Square Root | 1 | Calculates the square root of the integer. | [float](#float) |
| `sin` | Sine | 1 | Calculates the sine of the integer. | [float](#float) |
| `cos` | Cosine | 1 | Calculates the cosine of the integer. | [float](#float) |
| `tan` | Tangent | 1 | Calculates the tangent of the integer. | [float](#float) |
| `asin` | Arc Sine | 1 | Calculates the inverse sine. | [float](#float) |
| `acos` | Arc Cosine | 1 | Calculates the inverse cosine. | [float](#float) |
| `atan` | Arc Tangent | 1 | Calculates the inverse tangent. | [float](#float) |
| **Comparison** | | | | |
| `eq` | Equality | 2 | `true` if `A` is equal to `B`. | [bool](#bool) |
| `neq` | Inequality | 2 | `true` if `A` is not equal to `B`. | [bool](#bool) |
| `lt` | Less Than | 2 | `true` if `A` is strictly less than `B`. | [bool](#bool) |
| `leq` | Less Than or Equal | 2 | `true` if `A` is less than or equal to `B`. | [bool](#bool) |
| `gt` | Greater Than | 2 | `true` if `A` is strictly greater than `B`. | [bool](#bool) |
| `geq` | Greater Than or Equal | 2 | `true` if `A` is greater than or equal to `B`. | [bool](#bool) |

!!! Example
    Adding two integers

    ```asp
    assign(example, a, val(int, 5)).
    assign(example, b, val(int, 10)).
    assign(example, c, operation(add, (variable(a), (variable(b), ())))).
    ```
    This would assign the value `15` to the variable `c`.

---

## Float
Floats represent real numbers with fractional parts. They support a wide range of mathematical operations, including trigonometry.

!!! info
    Since neither `,` nor `.` can be used in ASP to represent floating point numbers, floats are represented by strings inside of the
    function symbol `float/1`. This means `"3.14"` is used for strings, while `float("3.14")` is used for floats.

### Definition
```asp
val(float, float("3.14159"))
val(float, float("-0.001"))
```

### Output
```asp
value(name, float, float("3.14159"))
value(name, float, float("-0.001"))
```

### Supported Operators
!!! info "Type Promotion" 
    If a binary operation involves one [int](#int) and one [float](#float) (e.g. the addition of an int and a float), the integer is automatically promoted to a float. The result is then calcualted as if both operands were floats.

| Operator | Name | Arity | Description | Return Type |
| :--- | :--- | :--- | :--- | :--- |
| **Arithmetic** | | | | |
| `add` | Addition | 2 | Adds two floats (`A + B`). | [float](#float) |
| `sub` | Subtraction | 2 | Subtracts the second float from the first (`A - B`). | [float](#float) |
| `mult` | Multiplication | 2 | Multiplies two floats (`A * B`). | [float](#float) |
| `div` | Division | 2 | Performs integer division on two floats (`A / B`). | [float](#float) |
| `fdiv` | Float Division | 2 | Performs explicit floating point division. | [float](#float) |
| `floor` | Floor | 1 | Rounds the float down to the nearest integer value (returned as float). | [float](#float) |
| `pow` | Exponentiation | 2 | Raises the first value to the power of the second. | [float](#float) |
| `abs` | Absolute Value | 1 | Returns the absolute value (`|A|`). | [float](#float) |
| `minus` | Unary Minus | 1 | Negates the value (`-A`). | [float](#float) |
| `max` | Maximum | 2 | Returns the larger of the two values. | [float](#float) |
| **Trigonometry** | | | | |
| `sqrt` | Square Root | 1 | Calculates the square root. | [float](#float) |
| `sin` | Sine | 1 | Calculates the sine. | [float](#float) |
| `cos` | Cosine | 1 | Calculates the cosine. | [float](#float) |
| `tan` | Tangent | 1 | Calculates the tangent. | [float](#float) |
| `asin` | Arc Sine | 1 | Calculates the inverse sine. | [float](#float) |
| `acos` | Arc Cosine | 1 | Calculates the inverse cosine. | [float](#float) |
| `atan` | Arc Tangent | 1 | Calculates the inverse tangent. | [float](#float) |
| **Comparison** | | | | |
| `eq` | Equality | 2 | `true` if `A` is equal to `B`. | [bool](#bool) |
| `neq` | Inequality | 2 | `true` if `A` is not equal to `B`. | [bool](#bool) |
| `lt` | Less Than | 2 | `true` if `A` is strictly less than `B`. | [bool](#bool) |
| `leq` | Less Than or Equal | 2 | `true` if `A` is less than or equal to `B`. | [bool](#bool) |
| `gt` | Greater Than | 2 | `true` if `A` is strictly greater than `B`. | [bool](#bool) |
| `geq` | Greater Than or Equal | 2 | `true` if `A` is greater than or equal to `B`. | [bool](#bool) |

!!! Example
    Multiplying two floats

    ```asp
    assign(example, a, val(float, float("2.5"))).
    assign(example, b, val(float, float("4.0"))).
    assign(example, c, operation(mult, (variable(a), (variable(b), ())))).
    ```
    This would assign the value `float("10.0")` to the variable `c`.

---

## String
Strings are used to represent text-based data. They support concatenation and comparison operations.

### Definition
```asp
val(string, "Hello, World!")
val(string, "Constraint Handling")
```

### Output
```asp
value(name, string, "Hello, World!")
value(name, string, "Constraint Handling")
```

| Operator | Name | Arity | Description | Return Type |
| :--- | :--- | :--- | :--- | :--- |
| **Manipulation** | | | | |
| `concat` | Concatenation | 2 | Joins two strings together. | [string](#string) |
| `length` | Length | 1 | Returns the number of characters in the string. | [int](#int) |
| **Comparison** | | | | |
| `eq` | Equality | 2 | `true` if string `A` is identical to string `B`. | [bool](#bool) |
| `neq` | Inequality | 2 | `true` if string `A` is not identical to string `B`. | [bool](#bool) |

!!! Example
    Concatenating a prefix to a name.
    ```asp
    assign(example, prefix, val(str, "var_")).
    assign(example, suffix, val(str, "x")).
    assign(example, full_name, operation(concat, (variable(prefix), (variable(suffix), ())))).
    ```

    This would assign the value `"var_x"` to the variable `full_name`.

---

## Symbol
Symbols represent raw ASP constants or function symbols (atoms). Unlike strings, they are not enclosed in quotes and follow standard ASP naming conventions (starting with a lowercase letter).

### Definition
```asp
val(symbol, active)
val(symbol, state(idle))
```

### Output
```asp
value(name, symbol, active)
value(name, symbol, state(idle))
```
### Supported Operators
!!! info "Ordering" 
    Symbol comparison follows the standard Clingo/ASP ordering rules.

| Operator | Name | Arity | Description | Return Type |
| :--- | :--- | :--- | :--- | :--- |
| **Comparison** | | | | |
| `eq` | Equality | 2 | `true` if `A` is equal to `B`. | [bool](#bool) |
| `neq` | Inequality | 2 | `true` if `A` is not equal to `B`. | [bool](#bool) |
| `lt` | Less Than | 2 | `true` if `A` comes before `B` in standard ASP order. | [bool](#bool) |
| `leq` | Less Than or Equal | 2 | `true` if `A` comes before or is equal to `B`. | [bool](#bool) |
| `gt` | Greater Than | 2 | `true` if `A` comes after `B` in standard ASP order. | [bool](#bool) |
| `geq` | Greater Than or Equal | 2 | `true` if `A` comes after or is equal to `B`. | [bool](#bool) |

!!! Example 
    Checking if a status variable is set to error.

    ```asp
    assign(system, current_status, val(symbol, error)).
    assign(system, is_critical, operation(eq, (variable(current_status), (val(symbol, error), ())))).
    ```

    This would assign `true` to `is_critical`.