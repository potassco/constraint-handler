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

For value input, the constraint handler uses the `val/2` function symbol.

```asp
val(Type, Value)
```

| Name | Description |
| :--- | :--- |
| `Type` | The data type of the value. Supported types include `int`, `float`, and `string`. |
| `Value` | The actual value, which should correspond to the specified type. |


!!! Example 
    This represents the integer value 42 when it is used in an assignment
    ```asp
    val(int, 42)
    ```

For value output, the constraint handler uses the `value/3` predicate.

| Name | Description |
| :--- | :--- |
| `Var` | The variable associated with the value. |
| `Type` | The data type of the value. |
| `Value` | The actual value assigned to the variable. |

!!! Example 
    This represents the value of the variable `my_variable` being the same integer 42
    ```asp
    value(my_variable, int, 42)
    ```

## Variables & Assignment

Variables represent unknown values that can be assigned during the solving process. 

They are defined using the `assign/3` predicate.

```asp
assign(Name, Var, val(Type, Value)).
```

| Name | Description |
| :--- | :--- |
| `Name` | **TODO** |
| `Var` | A unique identifier for the variable. |
| `val(Type, Value)` | The value assigned to the variable, where `Type` indicates the data type (e.g., `int`, `float`, `string`). |

!!! Example
    Assigning the integer value `42` to the variable `x` with the name `some_name`:

    ```asp
    assign(some_name, x, val(int, 42)).
    ```

    This is exactly what our small test example from the [Getting Started](getting_started.md#test-example) guide does. It assigns the value `42` of type `int` to the variable `x` with the name `some_name`. This creates the output atom `value(x, int, 42)` in the stable model.

While it is technically possible to use the `value/3` predicate to use the value of a variable, it is not recommended. Instead, users are
advised to use the `variable/1` function symbol.

```asp
variable(Var)
```

| Name | Description |
| :--- | :--- |
| `Var` | A unique identifier for the variable. |

!!! Example
    Getting the value assigned to variable `x` and assign it to variable `y`:

    ```asp
    assign(some_name, x, val(int,42)).
    assign(some_name, y, variable(x)).
    ```

## Operators & Operations
One key aspect of the constraint handler is its ability to express arbitrary operations. To achieve this, it uses the `operation/2` predicate.

```asp
operation(Op, Args).
```

| Name | Description |
| :------ | :--- |
| `Op` | **TODO** |
| `Args` | The operation to be performed (e.g., addition, subtraction, etc.). |
| `val(Type, Value)` | A list of arguments for the operation, which can include variables and values. |