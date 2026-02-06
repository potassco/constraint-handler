# Optimization

This page documents the native optimization capabilities of the constraint handler. While optimization can also be modeled using standard ASP techniques, the constraint handler aims to provide a more convenient and efficient way to express optimization problems.

## Maximize Sum

**[Declaration]**{.badge .declaration }

The optimization module supports maximizing the sum of a set of [Expressions]. This is done using the `optimize_maximizeSum/4` predicate.

```prolog
optimize_maximizeSum(Identifier, Expression, Key, Priority)
```

| Name | Description |
| :--- | :--- |
| `Identifier` | A unique identifier for this specific expression. |
| `Expression` | The expression whose value is used in the maximization. |
| `Key` | The key under which the value of the expression is used in the maximization. |
| `Priority` | The priority level for this optimization criterion. Higher priorities are optimized first. |

For convenience, there also exists a shorthand version `optimize_maximizeSum/3` where the `Priority` is set to `0` by default.


### Single Value

When wanting to optimize over a single value, the result could be captured in a [Variable] which is then optimized using the `optimize_maximizeSum/4` predicate directly. Here, single value doesn't mean the result has to be based on a single variable, just that the result can be captured in a single [Expression].

!!! Example "Example 1: Optimization Over a Single Variable"
    Consider a program that defines the variables `x` with a single value between `1` and `10`.

    ```prolog
    1{variable_define(name, x, val(int, 1..10))}1.
    ```

    The variable `x` can then be maximized using:

    ```prolog
    optimize_maximizeSum(max_x, variable(x), total, 0).
    ```

    The result will be the model where `x` takes the value `10`.

    ```prolog
    value(x,val(int,10))
    ```

!!! Example "Example 2: Optimization Over Multiple Variables"
    Consider a program that defines two variables `x` and `y`, each with values between `1` and `10`.

    ```prolog
    1{variable_define(name, x, val(int, 1..10))}1.
    1{variable_define(name, y, val(int, 1..10))}1.
    ```
    The sum of the variables `x` and `y` can then be maximized using:

    ```prolog
    optimize_maximizeSum(max_x_and_y, operation(add, (variable(x),(variable(y),()))), total, 0).
    ```

    The result will be the model where both `x` and `y` take the value `10`, maximizing their sum to `20`.

    ```prolog
    value(x,val(int,10))
    value(y,val(int,10))
    ```
### Multiple Values

Sometimes, the exact number of [Variables] is unknown or represents the optimization taget itself. In these cases, the optimization can be expressed using multimaps to capture all [Values] that should be optimized over.

!!! Example "Example 3: Optimization Over Multiple Values"
    Consider a program that defines some items as follows:
    ```prolog
    item(a,2).
    item(b,4).
    item(c,-1).
    ```

    Here, each item has some identifier and a value.

    To let the program freely select any set of items, we use a choice rule together with a multimap to declare items as taken:

    ```prolog
    multimap_declare(dummy,taken).
    { multimap_assign(dummy,taken,val(symbol,X),val(int,V)) } :- item(X,V).
    ```

    We can now optimize the selection such that we get the highest possible sum of values as follows:

    ```prolog
    optimize_maximizeSum(dummy_opt,EXPR,X,0) :- item(X,V),
        ITEM = val(symbol,X),
        COND = operation(isin,(ITEM,(variable(taken),()))),
        VALU = val(int,V),
        EXPR = operation(if,(COND,(VALU,()))).
    ```

    The result will be the model where items `a` and `b` are taken, maximizing the sum to `6`.

    ```prolog
    multimap_value(taken,symbol,a,int,2)
    multimap_value(taken,symbol,b,int,4)
    ```

!!! Example "Example 4: Optimization with Priorities"
    Priorities allow you to specify multiple optimization criteria where higher-priority goals are optimized first. Consider a program with two criteria: maximizing value (priority 1) and minimizing weight (priority 0).

    ```prolog
    item(a,2,5).
    item(b,4,3).
    item(c,3,4).

    multimap_declare(dummy,taken).
    { multimap_assign(dummy,taken,val(symbol,X),val(int,W)) } :- item(X,W,V).

    % Maximize value with priority 1 (higher priority)
    optimize_maximizeSum(opt_value,EXPR,X,1) :- item(X,W,V),
        ITEM = val(symbol,X),
        COND = operation(isin,(ITEM,(variable(taken),()))),
        VALU = val(int,V),
        EXPR = operation(if,(COND,(VALU,()))).

    % Minimize weight with priority 0 (lower priority) by maximizing negative weight
    optimize_maximizeSum(opt_weight,EXPR,X,0) :- item(X,W,V),
        ITEM = val(symbol,X),
        COND = operation(isin,(ITEM,(variable(taken),()))),
        WGHT = val(int,-W),  % Negate weight to minimize it
        EXPR = operation(if,(COND,(WGHT,()))).
    ```

    The solver will first maximize value (priority 1), and among solutions with equal value, it will minimize weight (priority 0).

---

## Precision

**[Declaration]**{.badge .declaration }

By default, the optimization module uses a precision of `1` for floating-point calculations. This can be adjusted using the `optimize_precision/2` predicate.

```prolog
optimize_precision(Precision, Priority)
```

| Name | Description |
| :--- | :--- |
| `Precision` | The [Value] to be used for floating-point calculations. Must be a positive [Int]. |
| `Priority` | The priority level for which to set the precision. |

For convenience, there also exists a shorthand version `optimize_precision/1` where the precision applies to all priorities that don't have a specific precision set.

!!! Example
    Given the following variable `x` with a set of possible [Float] values:

    ```prolog
    variable_declare(declare_x, x, fromFacts).
    variable_domain(x, val(float, float("-2.239"))).
    variable_domain(x, val(float, float("-2.235"))).
    variable_domain(x, val(float, float("-2.21"))).
    variable_domain(x, val(float, float("-2.1"))).
    variable_domain(x, val(float, float("-1.0"))).
    variable_domain(x, val(float, float("4.0"))).
    variable_domain(x, val(float, float("5.0"))).
    ```

    Assuming optimization for the lowest possible value without setting any precision:

    ```prolog
    optimize_maximizeSum(min_x, operation(mult,(variable(x),(val(int, -1),()))), total).
    ```

    Because the default precision is `1`, this would yield all models containing the floats starting with `-2.` as optimal models.

    Increasing the precision to `100`
    ```prolog
    optimize_precision(val(int,100)).
    ```

    would yield only the models containing `-2.239` and `-2.235` as optimal models.

    The precision could be increased to `1000`

    ```prolog
    optimize_precision(val(int,1000)).
    ```

    to yield the single optimal model containing only `-2.239` as a result.
