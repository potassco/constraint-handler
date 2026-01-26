# Language Concepts
This page details the core concepts of the constraint handler's modeling language.

!!! Note
    Here, we will use simpler syntax in order to not distract from the unterlying core concepts. The actual syntax used in the constraint handler will be explained in [Core Syntax] and other reference pages.

---

## Valuation
A Valuation is a mapping (association) from variables to values. It represents the "state" of the system at a specific point in time or in a specific solution.

We denote such mappings as:
```json
{ variable_1: value_1, variable_2: value_2, ... }
```

!!! Example
    Such a mapping might look like this:
    ```json
    { x: 5 , y: "hello"}
    ```

    This valuation indicates that the variable `x` has the value `5`.

---

## Expression
An Expression is a term that takes a specific value in the context of a valuation.

!!! Example
    Given some valuation
    ```json
    { x: 5 , y: "hello"}
    ```

    the expression `x + 2` takes the value `7`. 

In order to constrain the set of possible values that an expression can take, they can be associated with specific types. 

!!! Example
    The valuation
    ```json
    { x: 5 , y: "hello"}
    ```

    would not represent a valid context for the expression `x + y` of type `int`.

### Overview
A list of expressions used in the constraint handler.

| Expression | Description |
|-|-|
| [val] | Refers to a specific value in the current valuation. |
| [variable] | Retrieves the value of a variable from the current valuation. |
| [operation] | Combines multiple expressions using operators based on [Types] and [Collections]. |
| [lambda] | Defines anonymous functions that can be applied to expressions. |
| [tuple expression] | Multiple expressions combined into one [List]. |

---

## Statement
In contrast to expressions, statements do not yield values directly. Instead, they represent actions that either transform a given input valuation into an output valuation, or fail.


A simple way to achieve a transformation is through assignment statements of the form:
```json
variable := value
```

!!! Example
    The statement `x := 7` represents an assignment that transforms any input valuation into a new valuation where the variable `x` has the value `7`.

    Given some valuation
    ```json
    { x: 5 , y: "hello"}
    ```

    the statement produces a new valuation
    ```json
    { x: 7 , y: "hello"}
    ```

However, statements are neither required to always succeed nor to perform transformations that change the input valuation.

We can use
```
assert Condition
```
to denote a statement that fails if the given condition does not hold in the context of the input valuation. If the condition does hold, the statement succeeds and produces the same valuation as output.

!!! Example
    Given some input valuation
    ```json
    { x: 5 , y: "hello"}
    ```

    The statement 
    ```
    assert x > 0
    ``` 
    succeeds and produces the same valuation as output.

    While the statement 
    ```
    assert x < 0
    ``` 
    fails.

### Overview
A list of statements used in the constraint handler.

| Statement | Description |
|-|-|
| [assert] | Checks whether a given condition holds in the current valuation; fails if the condition is not met. |
| [assign][Assign Statement] | Assigns a value to a variable within the context of the statement. |
| [if][If Statement] | Conditionally executes one of two statements based on whether a condition holds. |
| [while] | Repeats a statement while a condition holds (up to a fixed iteration limit). |
| [seq2] | Executes two statements in sequence: the first transforms the valuation, then the second operates on the result. |
| [noop] | A "no-operation" statement (pass). It succeeds without changing the valuation. |
| [statement_python] | Embeds a Python script that can manipulate the valuation. |

---

## Fact

Facts correspond to ASP atoms or predicate instances that appear at the top level of an encoding or model. The constraint handler differentiates between two types of facts:

- **Declarations**: These define the structure of the problem, such as variables, collections, and constraints.
- **Results**: These represent the result or output atoms produced by the constraint handler.


### Declaration

Declarations are top-level definitions that structure the problem. Unlike expressions (which compute values) or statements (which define imperative steps), declarations exist to set up the variables, collections, and constraints that the solver must satisfy.

We can imagine a simple variable declaration of the form:
```json
var Variable in Domain
```
!!! Example
    The declaration
    ```json
    var x in [1, 2, 3]
    ```
    defines a variable `x` that can take any value from the list `[1, 2, 3]`.

    These values are not yet assigned to `x`; they merely specify the range of possible values that `x` can assume in different valuations.

#### Overview
A list of declarations used to define problems.

| Declaration | Description |
|-|-|
| [ensure] | Declares a constraint that must hold in all valid solutions. |
| [compute] | Experimental and not documented. |
| [computed] | Experimental and not documented. |
| [evaluate] | Experimental and not documented. |
| **Variable** | |
| [domain] | Defines a domain of possible values for variables. |
| [variable_declare] | Declares a variable with a specified domain. |
| [variable_declareOptional] | Declares an optional variable with a specified domain. |
| [variable_define] | Declares and defines a variable with a specific value. |
| [variable_domain] | Retrieves the domain of a declared variable. |
| **Set** | |
| [set_declare] | Declares a set variable with a specified domain. |
| [set_assign] | Declares a set variable and assigns it a value from a specified domain. |
| **Multimap** | |
| [multimap_declare] | Declares a multimap variable with a specified domain. |
| [multimap_assign] | Declares a multimap
| **Optimization** | |
| [optimize_maximizeSum] | Declares a maximization objective based on the sum of values. |
| [optimize_precision] | Declares the precision floats in the optimization are handled with. |
| **Engine** | |
| [requestEngine] | Requests a specific engine for solving a part of the program. |
| [defaultEngine] | Sets the default engine for solving all parts of the program without a specific engine request. |
| **Preference** | |
| [preference_maximizeScore] | Indicates that the solver should order solutions based on the total preference score. |
| [preference_holds] | Declares a preference based on a condition. |
| [preference_variableValue] | Declares a preference for a variable having a specific value. |
| **Execution** | |
| [execution_declare] | Prepares a statement for execution by declaring it with a specific name and providing input and output. |
| [execution_run] | Runs a previously declared execution. |

---

### Result
Output facts represent the results produced by the constraint handler after solving a problem. They indicate which variables have been assigned specific values in a solution, warnings and preferences.

!!! Example
    Given some valuation
    ```json
    { x: 5 , y: "hello"}
    ```

    One could imagine an output fact like this:
    ```json
    output(x, 5)
    ```

#### Overview
A list of output facts used to represent results.

| Result | Description |
|-|-|
| [value] | Indicates the assigned value of a variable in the solution. |
| [set_value] | Indicates the assigned value of a variable in the solution. |
| [multimap_value] | Indicates the assigned value of a variable in the solution. |
| [warning] | Represents a warning message generated during solving. |
| [evaluated] | Experimental and not documented. |
| [preference_score] | Represents the total score of preferences satisfied in the solution. |