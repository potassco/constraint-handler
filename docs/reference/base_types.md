# Base Types

This section documents the fundamental data types supported by the **constraint_handler**. Each type comes with its own set of operators.

---
## Notation
In the following sections, we will use the here declared notation to describe types and their available operators.

### Operator Signatures
Operators are described using a function signature notation:

```prolog
(input_type1, input_type2, ...) -> output_type
```

Where `input_type` and `output_type` refer to the data types involved in the [Operation].

#### Simple
Simple operators often only require a single input type and produce a single output type. For example, an addition operator for integers would be represented as:

```prolog
(int, int) -> int
```

#### Union
Sometimes the output type may be a union of multiple types, indicating that the operator can return different types based on the inputs. This is denoted using the pipe symbol `|`. For example:

```prolog
(int, int) -> int | float
```
Could represent some division [Operation] that returns an integer when the division is exact, and a float otherwise.

#### Generic Variables
Capitalized letters act as placeholders for any type.

 - **Consistency:** If the same letter appears multiple times (e.g., `A`), all arguments using that letter must be of the same type.
 - **Distinctness:** Different letters (e.g., `A` and `B`) can represent different types.


When defining more complex operators, the output type may depend directly on the input types. This is indicated using placeholders like `A`, `B`, etc. For example:

```prolog
(A, B) -> A | B
```
Indicates that the output type can be either of the input types.
!!! Example "Example: Same Type"
    Given some operator signature:

    ```prolog
    (T, T) -> bool
    ```
    This means that the operator takes two inputs of the same type (denoted by `T`), and returns a boolean value.

!!! Example "Example: Different Types"
    Given some operator signature:

    ```prolog
    (A,B) -> A
    ```

    This means that the operator takes two inputs of potentially different types (denoted by `A` and `B`), and returns a value of the same type as the first input (`A`).
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
| **Comparison** | | | |
| `eq` | Equality | ([none] \| T, [none] \| T) $\to$ [bool] | `true` if both arguments have the same value, otherwise `false`. |
| `neq` | Inequality | ([none] \| T, [none] \| T) $\to$ [bool] | `true` if both arguments have different values, otherwise `false`. |
| **Logical** | | | |
| `limp` | Implication | ([none] \| [bool], [none] \| [bool]) $\to$ [none] | If either of the values is `none`, the result will be `none`. Otherwise, this follows the standard implication rules from [bool]. |
| **Negation** | | | |
| `lnot` | Classical Negation | ([none]) $\to$ [none] | The negation of `none` is still `none`. |

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
    Some of the operators like `conj` and `disj` accept any number of arguments, these use the [list] notation as shown in the expression section. Others are strictly unary or binary.


| Operator | Name | Signature | Description |
| :--- | :--- | :--- | :--- |
| **Comparison** | | | | |
| `eq` | Equality | ([bool] \| [none], [bool] \| [none]) $\to$ [bool] | `true` if both arguments have the same value, otherwise `false`. |
| `neq` | Inequality | ([bool] \| [none], [bool] \| [none]) $\to$ [bool] | `true` if both arguments have different values, otherwise `false`. |
| **Logical** | | | | |
| `conj` | Conjunction | ([list]\[[bool]\]) $\to$ [bool] | `true` only if *all* arguments in the list are true. Short-circuits if `false` is found. |
| `disj` | Disjunction | ([list]\[[bool]\]) $\to$ [bool] | `true` if *at least one* argument in the list is true. |
| `limp` | Implication | ([bool], [bool]) $\to$ [bool] | `false` only if the first argument is `true` and the second is `false`. Otherwise `true`. | [bool] \| [none] |
| `lxor` | Exclusive OR | ([list]\[[bool]\]) $\to$ [bool]  | `true` if an **odd** number of arguments are `true`. |
| `leqv` | Equivalence | ([list]\[[bool]\]) $\to$ [bool]  | `true` if an **even** number of arguments are `true`. |
| **Negation** | | | | |
| `lnot` | Logical | ([bool]) $\to$ [bool] | Standard inversion (`true` $\to$ `false`, `false` $\to$ `true`). |
| `snot` | Strong | ([bool]) $\to$ [bool] | Treats undefined/missing values as `false`. |
| `wnot` | Weak | ([bool]) $\to$ [bool] | Treats undefined/missing values as `true`. |

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
| `add` | Addition | ([int], [int]) $\to$ [int] | Adds two integers. |
| `sub` | Subtraction | ([int], [int]) $\to$ [int] | Subtracts the second integer from the first. |
| `mult` | Multiplication | ([int], [int]) $\to$ [int] | Multiplies two integers. |
| `div` | Integer Division | ([int], [int]) $\to$ [int] | Divides the first integer by the second. |
| `pow` | Exponentiation | ([int], [int]) $\to$ [int] | Raises the first integer to the power of the second. |
| `abs` | Absolute Value | ([int]) $\to$ [int] | Returns the absolute value of the integer. |
| `minus` | Unary Minus | ([int]) $\to$ [int] | Negates the integer. |
| **Trigonometry** | | | |
| `sqrt` | Square Root | ([int]) $\to$ [float] | Calculates the square root of the integer. |
| `sin` | Sine | ([int]) $\to$ [float] | Calculates the sine of the integer. |
| `cos` | Cosine | ([int]) $\to$ [float] | Calculates the cosine of the integer. |
| `tan` | Tangent | ([int]) $\to$ [float] | Calculates the tangent of the integer. |
| `asin` | Arc Sine | ([int]) $\to$ [float] | Calculates the inverse sine. |
| `acos` | Arc Cosine | ([int]) $\to$ [float] | Calculates the inverse cosine. |
| `atan` | Arc Tangent | ([int]) $\to$ [float] | Calculates the inverse tangent. |
| **Comparison** | | | |
| `eq` | Equality | ([int] \| [none], [int] \| [none]) $\to$ [bool] | `true` if both arguments have the same value, otherwise `false`. |
| `neq` | Inequality | ([int] \| [none], [int] \| [none]) $\to$ [bool] | `true` if both arguments have different values, otherwise `false`. |
| `lt` | Less Than | ([int], [int]) $\to$ [bool] | `true` if first is strictly less than second. |
| `leq` | Less Than or Equal | ([int], [int]) $\to$ [bool] | `true` if first is less than or equal to second. |
| `gt` | Greater Than | ([int], [int]) $\to$ [bool] | `true` if first is strictly greater than second. |
| `geq` | Greater Than or Equal | ([int], [int]) $\to$ [bool] | `true` if first is greater than or equal to second. |

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
    If a binary operation involves one [int] and one [float] (e.g. the addition of an int and a float), the integer is automatically promoted to a float. The result is then calcualted as if both operands were floats.

| Operator | Name | Signature | Description |
| :--- | :--- | :--- | :--- |
| **Arithmetic** | | | |
| `add` | Addition | ([float], [float]) $\to$ [float] | Adds two floats. |
| `sub` | Subtraction | ([float], [float]) $\to$ [float] | Subtracts the second float from the first. |
| `mult` | Multiplication | ([float], [float]) $\to$ [float] | Multiplies two floats. |
| `div` | Division | ([float], [float]) $\to$ [float] | Performs integer division on two floats. |
| `fdiv` | Float Division | ([float], [float]) $\to$ [float] | Performs explicit floating point division. |
| `floor` | Floor | ([float]) $\to$ [float] | Rounds the float down to the nearest integer value. |
| `pow` | Exponentiation | ([float], [float]) $\to$ [float] | Raises the first value to the power of the second. |
| `abs` | Absolute Value | ([float]) $\to$ [float] | Returns the absolute value. |
| `minus` | Unary Minus | ([float]) $\to$ [float] | Negates the value. |
| `max` | Maximum | ([float], [float]) $\to$ [float] | Returns the larger of the two values. |
| **Trigonometry** | | | |
| `sqrt` | Square Root | ([float]) $\to$ [float] | Calculates the square root. |
| `sin` | Sine | ([float]) $\to$ [float] | Calculates the sine. |
| `cos` | Cosine | ([float]) $\to$ [float] | Calculates the cosine. |
| `tan` | Tangent | ([float]) $\to$ [float] | Calculates the tangent. |
| `asin` | Arc Sine | ([float]) $\to$ [float] | Calculates the inverse sine. |
| `acos` | Arc Cosine | ([float]) $\to$ [float] | Calculates the inverse cosine. |
| `atan` | Arc Tangent | ([float]) $\to$ [float] | Calculates the inverse tangent. |
| **Comparison** | | | |
| `eq` | Equality | ([float] \| [none], [float] \| [none]) $\to$ [bool] | `true` if both arguments have the same value, otherwise `false`. |
| `neq` | Inequality | ([float] \| [none], [float] \| [none]) $\to$ [bool] | `true` if both arguments have different values, otherwise `false`. |
| `lt` | Less Than | ([float], [float]) $\to$ [bool] | `true` if first is strictly less than second. |
| `leq` | Less Than or Equal | ([float], [float]) $\to$ [bool] | `true` if first is less than or equal to second. |
| `gt` | Greater Than | ([float], [float]) $\to$ [bool] | `true` if first is strictly greater than second. |
| `geq` | Greater Than or Equal | ([float], [float]) $\to$ [bool] | `true` if first is greater than or equal to second. |

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

!!! Warning
    Currently strings are called `str` and not `string`. In the future, this section will completely move into either direction.

### Definition
```prolog
val(str, "Hello, World!")
val(str, "Constraint Handling")
```

### Output
```prolog
value(name, val(str, "Hello, World!"))
value(name, val(str, "Constraint Handling"))
```

| Operator | Name | Signature | Description |
| :--- | :--- | :--- | :--- |
| **Manipulation** | | | |
| `concat` | Concatenation | ([string], [string]) $\to$ [string] | Joins two strings together. |
| `length` | Length | ([string]) $\to$ [int] | Returns the number of characters in the string. |
| **Comparison** | | | |
| `eq` | Equality | ([string] \| [none], [string] \| [none]) $\to$ [bool] | `true` if both arguments have the same value, otherwise `false`. |
| `neq` | Inequality | ([string] \| [none], [string] \| [none]) $\to$ [bool] | `true` if both arguments have different values, otherwise `false`. |

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
Normal ASP symbols can also be used as values. They are frequently used for representing states or identifiers.

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
| `eq` | Equality | ([symbol] \| [none], [symbol] \| [none]) $\to$ [bool] | `true` if both arguments have the same value, otherwise `false`. |
| `neq` | Inequality | ([symbol] \| [none], [symbol] \| [none]) $\to$ [bool] | `true` if both arguments have different values, otherwise `false`. |
| `lt` | Less Than | ([symbol], [symbol]) $\to$ [bool] | `true` if first argument is smaller than the second. |
| `leq` | Less Than or Equal | ([symbol], [symbol]) $\to$ [bool] | `true` if first argument is smaller than or equal to the second. |
| `gt` | Greater Than | ([symbol], [symbol]) $\to$ [bool] | `true` if first argument is larger than the second. |
| `geq` | Greater Than or Equal | ([symbol], [symbol]) $\to$ [bool] | `true` if first argument is larger than or equal to the second. |

!!! Example
    Checking if a status variable is set to error.

    ```prolog
    variable_define(system, current_status, val(symbol, error)).
    variable_define(system, is_critical, operation(eq, (variable(current_status), (val(symbol, error), ())))).
    ```

    This would assign `true` to `is_critical`.
