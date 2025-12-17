# Basic Concepts

This section introduces the fundamental concepts of the **constraint_handler** library. Understanding these concepts is essential for effectively using the library in your ASP programs. For a complete overview of all available features, refer to the **TODO**.

## Input & Output

The constraint handler uses a number of predicates and function symbols to represent inputs and outputs. Here, an input is the 
content of the ASP program that uses the constraint handler, while the output are the additional atoms added to the stable models
by the constraint handler.

## Types
Types define the kind of data being handled. The constraint handler supports primitive as well as some abstract datatypes. One of the main advantages of the constraint handler is its ability to seamlessly manage different data types within ASP programs that are not natively supported by Clingo. For instance, while Clingo primarily handles integers, the constraint handler extends this capability to include floats and even sets and maps.

For a full list of supported types, refer to the **TODO** section in the ASP Reference.

## Values
Values represent concrete data used in rules and constraints. 

To work with a value directly, the constraint handler uses the `val/2` function symbol.

```prolog
val(Type, Value)
```

| Name | Description |
| :--- | :--- |
| `Type` | The data type of the value. Supported types include `int`, `float`, and `string`. |
| `Value` | The actual value, which should correspond to the specified type. |


!!! Example 
    This represents the integer value 42. It can be used in expressions such as operations or assignments.
    ```prolog
    val(int, 42)
    ```

Values assigned to certain variables are added to the output. For this the constraint handler uses the `value/3` predicate.

| Name | Description |
| :--- | :--- |
| `Var` | The variable associated with the value. |
| `Type` | The data type of the value. |
| `Value` | The actual value assigned to the variable. |

!!! Example 
    This represents the value of the variable `my_variable` being the integer 42
    ```prolog
    value(my_variable, int, 42)
    ```

## Variables & Assignment

Variables represent unknown values that can be assigned during the solving process. 

They are defined using the `assign/3` predicate.

```prolog
assign(Name, Var, val(Type, Value)).
```

| Name | Description |
| :--- | :--- |
| `Name` | **TODO** |
| `Var` | A unique identifier for the variable. |
| `val(Type, Value)` | The value assigned to the variable, where `Type` indicates the data type (e.g., `int`, `float`, `string`). |

!!! Example
    Assigning the integer value `42` to the variable `x` with the name `some_name`:

    ```prolog
    assign(some_name, x, val(int, 42)).
    ```

    This is exactly what our small test example from the [Getting Started](getting_started.md#test-example) guide does. It assigns the value `42` of type `int` to the variable `x` with the name `some_name`. This creates the output atom `value(x, int, 42)` in the stable model.

While it is technically possible to use the `value/3` predicate to use the value of a variable, it is not recommended. Instead, users are
advised to use the `variable/1` function symbol.

```prolog
variable(Var)
```

| Name | Description |
| :--- | :--- |
| `Var` | A unique identifier for the variable. |

!!! Example
    Getting the value assigned to variable `x` and assign it to variable `y`:

    ```prolog
    assign(some_name, x, val(int,42)).
    assign(some_name, y, variable(x)).
    ```

## Operators & Operations
One key aspect of the constraint handler is its ability to express arbitrary operations. To achieve this, it uses the `operation/2` predicate together with a collection of operators.

```prolog
operation(Op, Args).
```

| Name | Description |
| :--- | :--- |
| `Op` | The operator to be applied. Supported operators include arithmetic operations (e.g, `add`, `sub`, `mul`, `div`), comparison operations (e.g., `eq`, `lt`, `gt`), and logical operations (e.g., `and`, `or`, `not`). For a full list of supported operators by specific types, please refer to the respective pages in the reference. |
| `Args` | A list of arguments on which the operator will be applied. Arguments can be values (using `val/2`), variables (using `variable/1`), or even other operations (using nested `operation/2`). |

!!! Example
    Adding two variables `x` and `y` and assigning the result to variable `z`
    ```prolog
    assign(some_name, x, val(int,5)).
    assign(some_name, y, val(int,7)).
    assign(some_name, z, operation(add, (variable(x), (variable(y),())))).
    ```

## Lists & Nesting
As can be seen in the previous section, the constraint handler uses lists and nesting to create complex expressions.

### Lists
Lists are represented as recursive tuples. More precisely, a list is either the empty tuple `()` or a tuple of the form `(Head, Tail)`, where `Head` is the first element of the list and `Tail` is another list representing the rest of the elements. A list has to be terminated by the empty tuple.

!!! Example
    The list containing the integers `1`, `2`, and `3` is represented as follows:
    ```prolog
    (val(int, 1), (val(int, 2), (val(int, 3), ())))
    ```

### Nesting
Nesting allows for the construction of more complex structures by embedding expressions within each other. This is particularly useful when defining
expressions that can be seen as a sequence of operations. In that case one or more elements of the argument list will be entire operations.

!!! Example
    Consider the expressions `a+x` and `b+c`. These can be represented like this:
    ```prolog
    operation(add, (variable(a), (variable(x),())))
    operation(add, (variable(b), (variable(c),())))
    ```

    If we now wanted to represent `a + b + c` directly, we can imagine one possible structure like this:

    ```mermaid
    graph TD
      Op1[add] --> A[variable a]
      Op1 --> Op2[add]
      Op2 --> B[variable b]
      Op2 --> C[variable c]
    ```

    As the diagram suggests, this can be achieved by replacing the `variable(x)` in the first operation by the entirety of the second operation:
    ```prolog
    operation(add, (variable(a), (operation(add, (variable(b), (variable(c),()))),())))
    ```

## Constraints
In the constraint handler, constraints are represented by the `ensure/2` predicate. The conditions within the constraints are expressed using the same operators and operations as described above. These conditions must evaluate to true for the stable model to be considered valid.

```prolog
ensure(Name, Condition).
```

| Name | Description |
| :--- | :--- |
| `Name` | **TODO** |
| `Condition` | The condition that must hold true. This is typically expressed using the `operation/2` predicate to combine variables, values, and operations. |

!!! Example
    Ensuring that the variable `z` is greater than `10`
    ```prolog
    ensure(some_name, operation(gt, (variable(z), (val(int,10),())))).
    ```