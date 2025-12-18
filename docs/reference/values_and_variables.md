# Values & Variables

This page describes how to work with values and variables in the ASP constraint handler.

## Value

Values represent concrete instances of data of some [type](./base_types.md) or [collection](./collections.md) used in rules and constraints.

To work with a value directly, the constraint handler uses the `val/2` function symbol.

```prolog
val(Type, Value)
```

| Name | Description |
| :--- | :--- |
| `Type` | The data type of the value. | 
| `Value` | The actual value, which should correspond to the specified type. |


!!! Example 
    This represents the integer value 42. It can be used in expressions such as operations or assignments.
    ```prolog
    val(int, 42)
    ```

---

## Variable

Variables represent references to values that can be reused throughout the program.


### Input
They are defined by assigning a value to an identifier using the `assign/3` predicate.
```prolog
assign(Name, Identifier, Expression).
```

| Name | Description |
| :--- | :--- |
| `Name` | **TODO** |
| `Identifier` | A unique identifier for the variable. |
| `Expression` | An expression that evaluates to a value. |

### Output
When a variable is assigned a value, an atom of the `value/3` predicate is added to the model.

```prolog
value(Var, Type, Value)
```

| Name | Description |
| :--- | :--- |
| `Var` | The variable associated with the value. |
| `Type` | The data type of the value. |
| `Value` | The actual value assigned to the variable. |


!!! Example
    Assigning the integer value `42` to the variable `x`:

    ```prolog
    assign(some_name, x, val(int, 42)).
    ```

    This adds the following output atom to the model:

    ```prolog
    value(x, int, 42).
    ```

    This is exactly what the test example from the [Getting Started](getting_started.md#test-example) guide does.

### Usage
While it is technically possible to use the `value/3` predicate to work with the value of a variable, it is **not recommended** for defining logic. Instead, users are advised to use the `variable/1` function symbol within their expressions.

This function symbol retreives the value stored in the specified variable.

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