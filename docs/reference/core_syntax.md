# Core Syntax

This page documents the core syntax and fundamental building blocks of the constraint handler.

---

## Notation

In the following sections, we will introduce the notation used throughout the documentation to describe the various elements of the constraint handler.

While in the previous [Language Concepts] page we used an abstract syntax to introduce general concepts such as [Expressions] and [Declarations], this page mainly focuses on the specific syntax used by the constraint handler to represent these concepts in ASP.

However, for documentation purposes, we will often use more meaningful names for arguments instead of the generic ones introduced previously and will refer to their respective concepts accordingly.

For example, we will use `Identifier` to refer to unique names assigned to specific [Declarations]. These identifiers can be any term, but we want to make it more specific. They typically appear as the first argument in their respective predicates.

Similarly, we will use the term `Name` to refer to unique names assigned to variables. Like `Identifier`, these can be any term. They typically appear as the second argument in their respective predicates.

---

## Syntax

The base syntax follows standard ASP predicates and function symbols.

### Simple
A simple [Declaration] with a fixed number of arguments could be represented as follows:

```prolog
some_predicate(Identifier, Term, Term)
```

| Name | Description |
| :--- | :--- |
| `some_predicate` | The identifier of the predicate. |
| `Identifier` | A term used as a unique identifier of this specific atom. |
| `Term` | Some argument of the predicate. |

!!! Example
    A simple declaration `some_predicate` with the unique identifier `my_predicate` and three terms:
    ```prolog
    some_predicate(my_predicate, term_1, term_2, term_3)
    ```

### List

For arguments with varying numbers of elements, the constraint handler uses a list syntax.

Lists are represented as recursive tuples. More precisely, a list is either the empty tuple `()` or a tuple of the form `(Head, Tail)`, where `Head` is the first element of the list and `Tail` is another list representing the rest of the arguments. A list has to be terminated by the empty tuple.

!!! Example
    Given some predicate with a definition like:

    ```prolog
    some_predicate(Identifier, Terms)
    ```

    where Terms represents a list of terms, one could represent a list with three terms as follows:

    ```prolog
    some_predicate(my_predicate, (term_1, (term_2, (term_3, ()))))
    ```

---

## Value

**[Expression]**{.badge .expression }

Values represent concrete instances of data of some [Type] or [Collection] used in rules and constraints.

To work with a value directly, the constraint handler uses the `val/2` function symbol.

```prolog
val(Type, Term)
```

| Name | Description |
| :--- | :--- |
| `Type` | The data type of the value. This should correspond to one of the supported types in the constraint handler, such as [int], [bool], etc. | 
| `Term` | The actual value, which should correspond to the specified type. |


!!! Example 
    This represents the integer value 42. It can be used in expressions such as operations or assignments.
    ```prolog
    val(int, 42)
    ```

---

## Variable

Variables represent references to values that can be reused throughout the program. The constraint handler provides multiple ways of assigning values to variables.

### Output

**[Result]**{.badge .result }

When a variable is assigned a value, an atom of the `value/2` predicate is added to the model.

```prolog
value(Name, Value)
```

| Name | Description |
| :--- | :--- |
| `Name` | The unique identifier for the variable associated with the value. |
| `Value` | The actual value assigned to the variable using the `val/2` predicate. |


!!! Example
    If the integer value `42` was assigned to the variable `x` the following atom would be added to the model:

    ```prolog
    value(x, val(int, 42)).
    ```

    This is exactly what the test example from the [Getting Started](../user_guide/getting_started.md#test-example) guide does.


### Define

**[Declaration]**{.badge .declaration }

The simplest way to create variables is to use the `variable_define/3` predicate to define them with a specific value.

```prolog
variable_define(Identifier, Name, Expression).
```

| Name | Description |
| :--- | :--- |
| `Identifier` | A unique identifier for this specific [Declaration]. |
| `Name` | A unique identifier for the variable. |
| `Expression` | An [Expression] to be associated with the variable. |

This assigns a specific value to the variable `Name` based on the [Valuation] of `Expression`. 

The result is a single `value/2` atom in the model.

### Declare

**[Declaration]**{.badge .declaration }

A more advanced technique is to declare variables using the `variable_declare/3` predicate. Instead of creating a single variable with a specific value, this declares possible values from a given set of possible values (domain).

!!! Note
    While [Define](#define) creates a single `value/2` atom in all models. The [Declare](#declare) approach creates multiple models with different `value/2` atoms based on the domain.

```prolog
variable_declare(Identifier, Name, Domain).
```

| Name | Description |
| :--- | :--- |
| `Identifier` | A unique identifier for this specific [Declaration]. |
| `Name` | A unique identifier for the variable. |
| `Domain` | An [Expression] that evaluates to a domain of possible values. |

!!! Example
    Declaring a variable `x` that can take the boolean values `true` or `false`:

    ```prolog
    variable_declare(some_id, x, boolDomain).
    ```

    This creates models for both possible assignments:

    ```prolog
    value(x, val(bool, true)).
    ```
    and

    ```prolog
    value(x, val(bool, false)).
    ```


#### Domain

**[Fact]**{.badge .fact }

While the constraint handler provides a shortcut for boolean domains, users can also define custom domains.

##### From List

An easy way to define a domain is to use the `fromList` function symbol together with a list of possible values.

```prolog
fromList(Values)
```

| Name | Description |
| :--- | :--- |
| `Values` | A [List] of [Values] representing the domain. |

!!! Example
    Creating a variable `y` that can take the integer values `1`, `2`, or `3`:

    ```prolog
    variable_declare(some_id, y, fromList((val(int,1), (val(int,2), (val(int,3), ()))))).
    ```

    This creates models for each possible assignment:

    ```prolog
    value(y, val(int, 1))
    ```
    ```prolog
    value(y, val(int, 2))
    ```
    ```prolog
    value(y, val(int, 3))
    ```

##### From Facts

Another way to define a domain is to use the `fromFacts/0` predicate. However, this additionally requires the use of the `variable_domain/2` predicate to extract the possible values from existing facts.

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
    value(y, val(int, 1))
    ```
    ```prolog
    value(y, val(int, 2))
    ```
    ```prolog
    value(y, val(int, 3))
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
    value(y, val(none, none)).
    ```

### Usage

While it is technically possible to use the `value/2` [Result] to work with the value of a variable, it is **not recommended** for defining logic. Instead, users are advised to use the `variable/1` function symbol within their [Expressions].

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

**[Expression]**{.badge .expression }

Operations are the key aspect of the constraint handler that allow expressing arbitrary computations. To achieve this, the constraint handler uses the `operation/2` predicate together with a collection of operators.

```prolog
operation(Operator, Terms).
```

| Name | Description |
| :--- | :--- |
| `Operator` | The operator to be applied. For a full list of supported operators by specific types, please refer to the respective pages in the reference. |
| `Terms` | A list of arguments on which the operator will be applied. Terms can be [Values], [Variables], or even other operations. |

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

**[Declaration]**{.badge .declaration }

Ensures allow users to specify conditions that must hold true in the model.

### Input
To specify conditions that must hold true in the model, the constraint handler provides the `ensure/2` predicate.

```prolog
ensure(Identifier, Condition).
```

| Name | Description |
| :--- | :--- |
| `Identifier` | A unique identifier for this specific statement. |
| `Condition` | The condition that must be satisfied in the model. |

### Condition
Conditions can be any expression with a [Bool] result. If the condition evaluates to false, the model is considered invalid.

!!! info "Strict Evaluation"
    The constraint handler is strict. The condition must explicitly evaluate to `true`. If a condition cannot be evaluated (e.g., because it references a variable that was never assigned), the constraint is considered violated.

If a variable itself is of type [Bool], it can be used directly as a condition.

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