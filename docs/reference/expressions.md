# Expressions

This page describes the different types of expressions supported by the constraint handler. Expressions are the fundamental building blocks in the constraint handler. The goal is to provide a unified way to work with different types of data and operations.

---

## Syntax

The base syntax for expressions follows the syntax of ASP predicates or function symbols.

### Simple
A simple expression with a set number of arguments could be represented as follows:

```prolog
some_expression(Identifier, Term, Term)
```

| Name | Description |
| :--- | :--- |
| `some_expression` | The type of expression. |
| `Identifier` | A unique identifier for the expression. |
| `Term` | An argument specific to the expression type. |

!!! Example
    A simple expression `my_expression` with the unique identifier `expr_1` and three terms:
    ```prolog
    my_expression(expr_1, term_1, term_2, term_3)
    ```

### List

To represent expressions with varying numbers of arguments, the constraint handler uses a list syntax.

Lists are represented as recursive tuples. More precisely, a list is either the empty tuple `()` or a tuple of the form `(Head, Tail)`, where `Head` is the first element of the list and `Tail` is another list representing the rest of the elements. A list has to be terminated by the empty tuple.

```prolog
some_expression(Identifier, Terms)
```

| Name | Description |
| :--- | :--- |
| `some_expression` | The type of expression. |
| `Identifier` | A unique identifier for the expression. |
| `Terms` | A list of terms specific to the expression type. |


!!! Example
    A list expression `my_list_expression` with the unique identifier `list_expr_1` and three terms:
    ```prolog
    my_list_expression(list_expr_1, (term_1, (term_2, (term_3, ()))))
    ```

---

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

Variables represent references to values that can be reused throughout the program. The constraint handler provides multiple ways of assigning values to variables.

### Output
When a variable is assigned a value, an atom of the `value/3` predicate is added to the model.

```prolog
value(Name, Type, Value)
```

| Name | Description |
| :--- | :--- |
| `Name` | The unique identifier for the variable associated with the value. |
| `Type` | The data type of the value. |
| `Value` | The actual value assigned to the variable. |


!!! Example
    If the integer value `42` was assigned to the variable `x` the following atom would be added to the model:

    ```prolog
    value(x, int, 42).
    ```

    This is exactly what the test example from the [Getting Started](../user_guide/getting_started.md#test-example) guide does.


### Define
The simplest way to create variables is to use the `variable_define/3` predicate to define them with a specific value.

```prolog
variable_define(Identifier, Name, Expression).
```

| Name | Description |
| :--- | :--- |
| `Identifier` | A unique identifier for this specific expression. |
| `Name` | A unique identifier for the variable. |
| `Expression` | An expression that evaluates to a value. |

This assigns a specific value to the variable `Name` based on the evaluation of `Expression`. 

The result is a single `value/3` atom in the model.

### Declare
A more advanced technique is to declare variables using the `variable_declare/3` predicate. Instead of creating a single variable with a specific value, this declares possible values from a given set of possible values (domain).

!!! Note
    While [define](#define) creates a single `value/3` atom in all models. The [declare](#declare) approach creates multiple models with different `value/3` atoms based on the domain.

```prolog
variable_declare(Identifier, Name, Domain).
```

| Name | Description |
| :--- | :--- |
| `Identifier` | A unique identifier for this specific expression. |
| `Name` | A unique identifier for the variable. |
| `Domain` | An expression that evaluates to a domain of possible values. |

!!! Example
    Declaring a variable `x` that can take the boolean values `true` or `false`:

    ```prolog
    variable_declare(some_id, x, boolDomain).
    ```

    This creates models for both possible assignments:

    ```prolog
    value(x, bool, true).
    ```
    and

    ```prolog
    value(x, bool, false).
    ```


#### Domain
While the constraint handler provides a shortcut for boolean domains, users can also define custom domains.

##### From List
An easy way to define a domain is to use the `fromList` function symbol together with a list of possible values.

```prolog
fromList(Values)
```

| Name | Description |
| :--- | :--- |
| `Values` | A list of values representing the domain. |

!!! Example
    Creating a variable `y` that can take the integer values `1`, `2`, or `3`:

    ```prolog
    variable_declare(some_id, y, fromList((val(int,1), (val(int,2), (val(int,3), ()))))).
    ```

    This creates models for each possible assignment:

    ```prolog
    value(y, int, 1).
    ```
    ```prolog
    value(y, int, 2).
    ```
    ```prolog
    value(y, int, 3).
    ```

##### From Facts
Another way to define a domain is to use the `fromFacts` function symbol. However, this additionally requires the use of the `variable_domain/2` predicate to extract the possible values from existing facts.

```prolog
variable_domain(Name, Domain).
```

| Name | Description |
| :--- | :--- |
| `Name` | A unique identifier for the variable. |
| `Domain` | The facts representing the domain of possible values. |

!!! Example
    Creating a variable `y` that can take the integer values `1`, `2`, or `3`:
    ```prolog
    variable_declare(some_id, y, fromFacts).
    variable_domain(y, val(int,(1;2;3))).
    ```

    This creates models for each possible assignment:

    ```prolog
    value(y, int, 1).
    ```
    ```prolog
    value(y, int, 2).
    ```
    ```prolog
    value(y, int, 3).
    ```

#### Optional
Variables that are declared using a domain can also be marked as optional. This means that the variable may also not be assigned any value at all.

```prolog
variable_declareOptional(Name).
```

| Name | Description |
| :--- | :--- |
| `Name` | A unique identifier for the variable. |s

!!! Example
    Marking the variable `y` from the previous example as optional:

    ```prolog
    variable_declareOptional(y).
    ```

    This creates models for each possible assignment as before, but also an additional model with the value:

    ```prolog
    value(y, none, none).
    ```

### Usage
While it is technically possible to use the `value/3` predicate to work with the value of a variable, it is **not recommended** for defining logic. Instead, users are advised to use the `variable/1` function symbol within their expressions.

This function symbol retreives the value stored in the specified variable.

```prolog
variable(Name)
```

| Name | Description |
| :--- | :--- |
| `Name` | A unique identifier for the variable. |

!!! Example
    Getting the value assigned to variable `x` and assign it to variable `y`:

    ```prolog
    variable_define(some_name, x, val(int,42)).
    variable_define(some_name, y, variable(x)).
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
| `Arguments` | A list of arguments on which the operator will be applied. Arguments can be [values](#value), [variables](#variable), or even other operations. |

!!! Example
    Adding two variables `x` and `y` and assigning the result to variable `z`
    ```prolog
    variable_define(some_name, x, val(int,5)).
    variable_define(some_name, y, val(int,7)).
    variable_define(some_name, z, operation(add, (variable(x), (variable(y),())))).
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

## Ensure
Ensures allow users to specify conditions that must hold true in the model.

### Input
To specify conditions that must hold true in the model, the constraint handler provides the `ensure/2` predicate.

```prolog
ensure(Identifier, Condition).
```

| Name | Description |
| :--- | :--- |
| `Identifier` | A unique identifier for this specific expression. |
| `Condition` | The condition that must be satisfied in the model. |

### Condition
Conditions can be any expression with a [bool](./base_types.md#bool) result. If the condition evaluates to false, the model is considered invalid.

!!! info "Strict Evaluation"
    The constraint handler is strict. The condition must explicitly evaluate to `true`. If a condition cannot be evaluated (e.g., because it references a variable that was never assigned), the constraint is considered violated.

If a variable itself is of type [bool](./base_types.md#bool), it can be used directly as a condition.

!!! Example
    Ensure that a variable `x` is true:
    ```prolog
    ensure(some_name, variable(x)).
    ```

Conditions can also be more complex expressions, such as comparisons or operations that yield a boolean result.

!!! Example
    Ensure the variable `x` has a greater value than the variable `y`.
    ```prolog
    ensure(some_name, operation(gt, (variable(x),(variable(y),())))).
    ```

Because **all** ensures must hold true for the model to be valid, they can be used to enforce multiple conditions at the same time. It is recommended to use this feature to break down complex constraints into smaller, more manageable parts.

!!! Example
    To ensure that variable `x` is greater than `y` and that variable `z` is true, one could write:

    ```prolog
    ensure(greater_than_and_true, operation(conj, (operation(gt, (variable(x),(variable(y),()))),(variable(z),())))).
    ```

    While this works, it gets harder to read the more conditions are added. A better approach is to use multiple `ensure/2` calls:

    ```prolog
    ensure(greater_than, operation(gt, (variable(x),(variable(y),())))).
    ensure(is_true, variable(z)).
    ```

    This way, each condition is clearly separated and easier to understand and debug.