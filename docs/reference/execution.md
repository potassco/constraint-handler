# Execution

This page documents the execution model of the language, focusing on how statements can be used to sequentially manipulate [Valuations].

## Input
To allow the transformation from input to output valuations, the input must first be prepared for execution. This is done by creating
variables that use the `execution_input/2` predicate as a name.

```prolog
execution_input(ExecutionName, Name)
```

| Name | Description |
| :--- | :--- |
| `ExecutionName` | The name of the execution for which the input variable is being created. |
| `Name` | The name of the variable representing the input value. |

!!! Example
    Defining an input variable with some value for a specific execution:

    ```prolog
    variable_define(some_identifier, execution_input(my_execution, a), val(int, 5)).
    ```

    This creates a variable `a` with the integer value `5` for the execution `my_execution`.

## Output
After execution, the output values will appear as variables using the `execution_output/2` predicate as a name.

!!! Note
    Output [Variables] do not necessarily have to appear in the input. Meaning, they also do not have to be
    declared beforehand. They will be created during execution as needed.

```prolog
execution_output(ExecutionName, Name)
```

| Name | Description |
| :--- | :--- |
| `ExecutionName` | The name of the execution for which the output variable is being created. |
| `Name` | The name of the variable representing the output value. |



## Transformation (Assign)

Transformations are done by using the `assign/2` predicate. This assigns the [Valuation] of a given [Expression] to a given variable within the context of a [Statement].

```prolog
assign(Name, Expression)
```

| Name | Description |
| :--- | :--- |
| `Name` | The name of the variable to which the result of the expression will be assigned. |
| `Expression` | The [Expression] whose result will be assigned to the variable. |

!!! Example
    A simple assignment of a constant value to a variable:

    ```prolog
    assign(c, val(int, 5))
    ```

    In this example, the variable `c` is assigned the integer value `5`.

## Declare
In order to execute some statement, first an execution has to be declared.

```prolog
execution_declare(Identifier, Name, Statement, Input, Output)
```

| Name | Description |
| :--- | :--- |
| `Identifier` | A unique identifier for the specific [Declaration]. |
| `Name` | A unique identifier for the execution. |
| `Statement` | The [Statement] to be executed. |
| `Input` | A [List] of terms representing the input to the statement. |
| `Output` | A [List] of terms representing the output of the statement. |

!!! Example
    Declaring an execution with a simple assignment statement:

    ```prolog
    execution_declare(dummy, my_exec, S, (a,()), (a,())) :-
        S = assign(a, val(int, 3)).
    ```

    This declares an execution named `my_execution` that assigns the integer value `3` to the variable `a`, taking `a` as input and producing `a` as output.

## Run
To execute a previously declared execution, the `execution_run/2` predicate is used.

```prolog
execution_run(Identifier, Name)
```

| Name | Description |
| :--- | :--- |
| `Identifier` | The unique identifier for the specific [Declaration] to be executed. |
| `Name` | The unique identifier for the execution to be run. |

!!! Example
    Running a previously declared execution:

    ```prolog
    execution_run(dummy, my_exec).
    ```

    This runs the execution named `my_execution` that was declared earlier.

## Control Flow
