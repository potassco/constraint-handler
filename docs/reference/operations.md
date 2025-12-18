# Operations

This page explains how to perform operations on values in the ASP constraint handler.

---

## List Syntax

Before starting with operations, it's important to understand the list syntax used for representing multiple arguments in expressions.

Lists are represented as recursive tuples. More precisely, a list is either the empty tuple `()` or a tuple of the form `(Head, Tail)`, where `Head` is the first element of the list and `Tail` is another list representing the rest of the elements. A list has to be terminated by the empty tuple.

!!! Example
    The list containing the integers `1`, `2`, and `3` is represented as follows:
    ```prolog
    (val(int, 1), (val(int, 2), (val(int, 3), ())))
    ```

---

## Operation
Operations are the key aspect of the constraint handler that allow expressing arbitrary computations. To achieve this, the constraint handler uses the `operation/2` predicate together with a collection of operators.

```prolog
operation(Operator, Arguments).
```

| Name | Description |
| :--- | :--- |
| `Operator` | The operator to be applied. For a full list of supported operators by specific types, please refer to the respective pages in the reference. |
| `Arguments` | A list of arguments on which the operator will be applied. Arguments can be [values](./values_and_variables.md#value), [variables](./values_and_variables.md#variable), or even other operations. |

!!! Example
    Adding two variables `x` and `y` and assigning the result to variable `z`
    ```prolog
    assign(some_name, x, val(int,5)).
    assign(some_name, y, val(int,7)).
    assign(some_name, z, operation(add, (variable(x), (variable(y),())))).
    ```

While simple operations may be sufficient for many use cases, more complex programs often require combining multiple operations together. For this reason, the constraint handler fully supports nesting operations within each other.

In this case, one or more elements of the argument list will be entire `operation` terms rather than simple values or variables.

!!! Example
    Consider the expressions `a+x` and `b+c`:
    ```prolog
    operation(add, (variable(a), (variable(x),())))
    operation(add, (variable(b), (variable(c),())))
    ```

    Graphically, they can be represented like this:

    ```mermaid
    flowchart LR
    subgraph S1 ["Expression 1: a + x"]
      direction TB
      Op1[add] --> Va[variable a]
      Op1 --> Vx[variable x]
    end

    subgraph S2 ["Expression 2: b + c"]
      direction TB
      Op2[add] --> Vb[variable b]
      Op2 --> Vc[variable c]
    end

    S1 ~~~ S2
    ```

    If we now wanted to represent `a + b + c` directly, we can imagine to simply move the entire graph of `Expression 2` into the slot of `variable x` like so:

    ```mermaid
    graph TD
    subgraph S1 ["Expression 3: a + b + c"]
      direction TB
      Op1[add] --> A[variable a]
      Op1 --> Op2[add]
      Op2 --> B[variable b]
      Op2 --> C[variable c]
    end
    ```

    In ASP, we do this by replacing the term `variable(x)` in the first operation by the entirety of the second operation:
    ```prolog
    operation(add, (variable(a), (operation(add, (variable(b), (variable(c),()))),())))
    ```