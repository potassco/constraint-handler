# Execution

This page documents the execution model of the language, focusing on how [Statements] can be used to sequentially manipulate [Valuations].

---

## Input
To allow the transformation from input to output valuations, the input must first be prepared for execution. This is done by creating
variables that use the `execution_input/2` function symbol as a name.

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
    variable_define(execution_input(my_execution, a), val(int, 5)).
    ```

    This creates a variable `a` with the integer value `5` for the execution `my_execution`.

---

## Output
After execution, the output values will appear as variables using the `execution_output/2` function symbol as a name.

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

---

## Assign

**[Statement]**{.badge .statement }

Transformations are done by using the `assign/2` function symbol. This assigns the [Valuation] of a given [Expression] to a given variable within the context of a [Statement].

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

---

## Control Flow
For more complex executions, control flow statements can be used to combine multiple statements into one execution, or to create conditional executions.

### Sequence

**[Statement]**{.badge .statement }

Multiple statements can be combined into a sequence using the `seq2/2` function symbol. This allows for executing multiple statements in order.

One crucial aspect of sequences is that the **output of the first statement becomes the input for the second statement**.

```prolog
seq2(Statement1, Statement2)
```

| Name | Description |
| :--- | :--- |
| `Statement1` | The first [Statement] to be executed. |
| `Statement2` | The second [Statement] to be executed after the first. |

!!! Example
    Combining two statements into a sequence:

    ```prolog
    ADD_ONE = assign(a, operation(add, (variable(a), (val(int,1),())))),
    seq2(
        ADD_ONE,
        ADD_ONE
    )
    ```

    In this example, the variable `a` is incremented by `1` twice in sequence. Since the output of the first assignment becomes the input for the second, the final value of `a` will be increased by `2`.

### If

**[Statement]**{.badge .statement }

The `if/3` function symbol allows for conditional execution of statements based on the evaluation of an expression.

```prolog
if(Condition, ThenStatement, ElseStatement)
```

| Name | Description |
| :--- | :--- |
| `Condition` | An [Expression] that evaluates to a boolean value, determining which statement
| `ThenStatement` | The [Statement] to execute if the condition is true. |
| `ElseStatement` | The [Statement] to execute if the condition is false. |

!!! Example
    A conditional execution based on the value of a variable:

    ```prolog
    if(
        operation(gt, (variable(a), (val(int, 10),()))),
        assign(b, val(int, 1)),
        assign(b, val(int, 0))
    )
    ```

    In this example, if the variable `a` is greater than `10`, the variable `b` is assigned the value `1`. Otherwise, `b` is assigned the value `0`.

### No Operation

**[Statement]**{.badge .statement }

The `noop/0` function symbol represents a no-operation statement. It performs no action and leaves the input valuation unchanged.

```prolog
noop
```

!!! Example
    A no-operation statement in an if-else construct:

    ```prolog
    if(
        operation(gt, (variable(a), (val(int, 10),()))),
        assign(a, val(int, 10)),
        noop
    )
    ```

    In this example, if the variable `a` is greater than `10`, it is assigned the value `10`. Otherwise, no operation is performed, and `a` remains unchanged. Effectively, this clamps the value of `a` to a maximum of `10`.

### Assert

**[Statement]**{.badge .statement }

The `assert/1` function symbol is used to enforce conditions during execution. If the condition evaluates to false, the execution fails. A failed execution behaves the same as a failed [ensure], making the entire model unsatisfiable.

```prolog
assert(Condition)
```

| Name | Description |
| :--- | :--- |
| `Condition` | An [Expression] that evaluates to a [bool] value. If false, the execution fails. |

!!! Example
    An assertion to ensure a variable meets a specific condition:

    ```prolog
    assert(
        operation(gt, (variable(a), (val(int, 0),())))
    )
    ```

    In this example, the execution will fail if the variable `a` is not greater than `0`.

### While

**[Statement]**{.badge .statement }

The `while/2` function symbol allows for repeated execution of a statement as long as a given condition holds true.

```prolog
while(Limit, Condition, Body)
```

| Name | Description |
| :--- | :--- |
| `Limit` | A maximum number of iterations to prevent infinite loops. If the limit is reached, the output values will be set to [None].|
| `Condition` | An [Expression] that evaluates to a boolean value, determining whether to continue looping. |
| `Body` | The [Statement] to be executed repeatedly while the condition is true.

!!! Example
    A while loop that increments a variable until it reaches a certain value:

    ```prolog
    while(
        10,
        operation(lt, (variable(a), (val(int, 5),()))),
        assign(a, operation(add, (variable(a), (val(int, 1),()))))
    )
    ```

    In this example, the variable `a` is incremented by `1` repeatedly as long as it is less than `5`, with a maximum of `10` iterations to prevent infinite loops.

---

## Declare

**[Declaration]**{.badge .declaration }

In order to execute some statement, first an execution has to be declared. For this, the `execution_declare/4` predicate is used.

```prolog
execution_declare(Name, Statement, Input, Output)
```

| Name | Description |
| :--- | :--- |
| `Name` | A unique identifier for the execution. |
| `Statement` | The [Statement] to be executed. |
| `Input` | A [List] of terms representing the input to the statement. |
| `Output` | A [List] of terms representing the output of the statement. |

!!! Example
    Declaring an execution with a simple assignment statement:

    ```prolog
    execution_declare(my_exec, S, (a,()), (a,())) :-
        S = assign(a, val(int, 3)).
    ```

    This declares an execution named `my_execution` that assigns the integer value `3` to the variable `a`, taking `a` as input and producing `a` as output.

---

## Run

**[Declaration]**{.badge .declaration }

To execute a previously declared execution, the `execution_run/1` predicate is used.

```prolog
execution_run(Name)
```

| Name | Description |
| :--- | :--- |
| `Name` | The unique identifier for the execution to be run. |

!!! Example
    Running a previously declared execution:

    ```prolog
    execution_run(my_exec).
    ```

    This runs the execution named `my_execution` that was declared earlier.
