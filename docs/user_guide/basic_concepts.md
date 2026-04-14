# Basic Concepts

This section introduces the fundamental concepts of the **constraint_handler** library. It explains how to define data, perform calculations, and enforce rules within your ASP programs.

For a complete specification of every predicate and operator, please consult the Reference section. It's recommended to start with the [Language Concepts] to better understand the overall design philosophy.

---

## Input & Output
The constraint handler operates on a simple principle:

1.  **Input:** You write declarative rules using the handler's predicates and function symbols (like `variable_define`, `ensure`, `operation`) to define your problem.
2.  **Output:** The handler processes these rules and adds new atoms (like `value`) to the final stable model, representing the computed results.

---

## Types
One of the main advantages of the constraint handler is its ability to seamlessly manage data types that are not natively supported by standard ASP solvers.

While Clingo primarily handles integers and symbolic constants, the constraint handler extends this to include:

* **Primitives:** [Floats], [Strings], and [Bools].
* **Collections:** [Sets] and [Multimaps].

> For a comprehensive list of supported types, please refer to the [Base Types] and [Collections] sections in the reference.

---

## Values
Because the handler supports many types, it needs a way to distinguish between them (e.g., the integer `5` vs. the string `"5"`). We use the `val/2` wrapper for this purpose.

**Syntax:** `val(Type, Data)`

!!! Example
    ```prolog
    val(int, 42)
    val(string, "Hello World")
    val(float, float("3.14"))
    ```

> For full details, see the [Value] reference.

---

## Variables & Assignment
Variables allow you to store specific values and reuse them later. You can create them using the `variable_define/2` predicate.

**Syntax:** `variable_define(Name, Expression)`

* **Name:** The name you will use to refer to this data.
* **Expression:** The value or calculation to assign.

!!! Example
    Assigning the integer `42` to a variable named `x`:
    ```prolog
    variable_define(x, val(int, 42)).
    ```

To use this variable in a later [Expression], you reference it using `variable(x)`.

> For full details, see the [Variable] reference.

---

## Operations
To perform calculations—such as arithmetic, logical comparisons, or set manipulations—you use **Operations**.

**Syntax:** `operation(Operator, Arguments)`

* **Operator:** The specific action (e.g., `add`, `mult`, `union`, `eq`).
* **Arguments:** A recursive list of inputs.

!!! Example
    Adding two variables `x` and `y`:
    ```prolog
    operation(add, (variable(x), (variable(y), ())))
    ```

> For more information, refer to the [Operation] reference. A list of operators is attached to each respective type in the [Base Type] or [Collections] sections.

---

## Constraints
While assignments *create* data, constraints *validate* it.

The `ensure/1` predicate asserts that a specific condition must be true. If the condition fails, the constraint handler rejects the current model (similar to an integrity constraint `:- ...` in standard ASP).

**Syntax:** `ensure(Condition)`

!!! Example
    Ensuring that variable `z` is greater than 10:
    ```prolog
    ensure(operation(gt, (variable(z), (val(int, 10), ())))).
    ```

> For more details, see [Ensure] in the reference.
