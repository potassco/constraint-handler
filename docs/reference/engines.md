# Engines

The previous section was about [Optimization] with respect to [Values]. This section
describes how to optimize the grounding or search process itself by choosing different
engines.

---

## Concept
An engine resembles a strategy for grounding and searching through the solution space. Different
engines may implement different algorithms and optimizations to improve performance
for specific types of problems.

The following engines are currently supported

| Name | Description |
| :--- | :--- |
| compile | Grounds each subpart of a [Declaration] separately. |
| ground | Grounds the entire [Declaration] as a whole, preserving correlations between variables. |
| propagator | Uses a custom propagator-based approach |

!!! Note
    While choosing the right engine can significantly affect the efficiency
    of solving a problem, it can be challenging to determine which engine is best suited for a particular problem or subproblem.


## Request
The `requestEngine/2` predicate allows users to specify which engine to use for a given
part of the program. This can be particularly useful when different parts of the program
have different characteristics that may benefit from different solving strategies.

```prolog
requestEngine(Identifier, Engine).
```

| Name | Description |
| :--- | :--- |
| Identifier | A unique identifier for the [Declaration] that the engine request applies to. |
| Engine | The engine to be used for the specified [Declaration]. |

## Default
Because it can be very verbose to specify engines for every part of a program, a default engine can be set
using the `defaultEngine/1` predicate. This engine applies to all [Declarations] that do not have a specific
engine requested via `requestEngine/2`.

If no default engine is set, the system will use the [compile](#compile) engine.


```prolog
defaultEngine(Engine).
```

| Name | Description |
| :--- | :--- |
| Engine | The default engine to be used for all [Declarations] without a specific engine request. |

## Examples
This section provides examples of how and when using certain engines can be beneficial.


### Strong Correlation

When expressions in a [Declaration] have strong correlations between variables, using the `ground` engine
can help preserve these correlations during grounding, leading to more efficient solving.

!!! Example
    Given is the following simple problem:
    ```prolog
    max_depth(15).
    variable_declare(declare_x, x, fromFacts).
    variable_domain(x, val(int, 0..1)).

    expression(1, variable(x)).
    expression(N+1, NEXT) :- 
        expression(N, PREV), max_depth(MAX), N < MAX,
        MULT = operation(mult, (val(int, 2), (PREV, ()))),
        NEXT = operation(add, (variable(x), (MULT, ()))).

    variable_define(define_y, y, E) :- expression(N, E), max_depth(N).
    ```
    Here, the variable `y` is defined in terms of `x` through a series of correlated expressions.

    More specifically, `y` is defined as:
    ```
    y = x + 2*x + 4*x + ... + 2^14*x
    ```

    Essentially, each expression "activates" the next higher bit in the binary representation of `y` based on the value of `x`. Since, `x` can only have values `0` or `1`, this means that `y` is either `0` (if `x=0`) or `32767` (if `x=1`). Thus, we only expect two models.

    However, default engine (compile) would ground each expression separately, losing the correlation between different occurrences of `x`. This would lead to a much larger search space, as the solver would have to consider all combinations of `x` values independently for each expression.

    This is where the `ground` engine comes into play. By using `ground`, we can ensure that the correlation between different occurrences of `x` is preserved during grounding. This means that when `x` is assigned a value, all expressions that depend on `x` will reflect that value consistently.

    To use the `ground` engine for this problem, we can add the following line:
    ```prolog
    requestEngine(define_y, ground).
    ```
    This tells the solver to ground the entire definition of `y`, including all sub-expressions, as a whole.


### No Correlation
In cases where there is little to no correlation between variables in a [Declaration],
using the `compile` engine can be more efficient.

!!! Example
    Given the following problem:
    ```prolog
    num_variables(3).
    variable_declare(declare_x, x(1..MAX), fromFacts) :- num_variables(MAX).
    variable_domain(x(1..MAX), val(int, 1..10)):- num_variables(MAX).

    expression(1, variable(x(1))).
    expression(N+1, NEXT) :- 
        expression(N, PREV), num_variables(MAX), N < MAX,
        NEXT = operation(max, (variable(x(N+1)), (PREV, ()))).

    variable_define(define_y, y, E) :- expression(N, E), num_variables(N).
    ```

    Here, we try to calculate the maximum value among a set of variables `x(1)`, `x(2)`, ..., `x(M)`. Each variable `x(i)` is independent of the others.

    For this reason, if we added the `ground` engine here:
    ```prolog
    requestEngine(define_y, ground).
    ```
    All variables would be grounded together. But since they are not correlated, we end up with all possible combinations of their values, leading to a combinatorial explosion.

    Conversely, if we remove the `ground` engine and fall back to the `compile` engine, each variable is grounded separately