# Base Types

This section documents the fundamental data types supported by the **constraint_handler**. Each type comes with its own set of operators and functions.

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


| Operator | Name | Arity | Description |
| :--- | :--- | :--- | :--- |
| **Comparison** | | | |
| `eq` | Equality | 2 | `true` if `A` is equal to `B`. |
| `neq` | Inequality | 2 | `true` if `A` is not equal to `B`. |
| **Logical** | | | |
| `conj` | Conjunction | N-ary | `true` only if *all* arguments in the list are true. Short-circuits if `false` is found. |
| `disj` | Disjunction | N-ary | `true` if *at least one* argument in the list is true. |
| `limp` | Implication | 2 | `false` only if the first argument is `true` and the second is `false`. Otherwise `true`. If either of the values is empty, the result will be empty as well. |
| `lxor` | Exclusive OR | N-ary  | `true` if an **odd** number of arguments are `true`. |
| `leqv` | Equivalence | N-ary  | `true` if an **even** number of arguments are `true`. |
| **Negation** | | | |
| `lnot` | Logical Negation | 1 | Standard inversion (`true` $\to$ `false`, `false` $\to$ `true`). Requires a defined value. |
| `snot` | Strong Negation | 1 | Treats undefined/missing values as `false`. |
| `wnot` | Weak Negation | 1 | Treats undefined/missing values as `true`. |

!!! Example
    Checking for inequality of two variables

    ```asp
    assign(example, a, val(bool, true)).
    assign(example, b, val(bool, false)).
    assign(example, c, operation(neq, (variable(a), (variable(b), ())))).
    ```

    This would assign the value `true` to the variable `c`.


## Int


## Float



## String



## Symbol
