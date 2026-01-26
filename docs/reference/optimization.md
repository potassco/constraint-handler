# Optimization

This page documents the native optimization capabilities of the constraint handler. While optimization can also be modeled using standard ASP techniques, the constraint handler aims to provide a more convenient and efficient way to express optimization problems.

## Maximize Sum

**[Declaration]**{.badge .declaration }

The optimization module supports maximizing the sum of a set of [Expressions]. This is done using the `optimize_maximizeSum/3` predicate.

```prolog
optimize_maximizeSum(Identifier, Expression, Key)
```

| Name | Description |
| :--- | :--- |
| `Identifier` | A unique identifier for this specific expression. |
| `Expression` | The expression whose value is used in the maximization. |
| `Key` | The key under which the value of the expression is used in the maximization. |


### Single Value

When wanting to optimize over a single value, the result could be captured in a [Variable] which is then optimized using the `optimize_maximizeSum/3` predicate directly. Here, single value doesn't mean the result has to be based on a single variable, just that the result can be captured in a single [Expression].

!!! Example "Example 1: Optimization Over a Single Variable"
    Consider a program that defines the variables `x` with a single value between `1` and `10`.

    ```prolog
    1{variable_define(name, x, val(int, 1..10))}1.
    ```

    The variable `x` can then be maximized using:

    ```prolog
    optimize_maximizeSum(max_x, variable(x), total).
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
    optimize_maximizeSum(max_x_and_y, operation(add, (variable(x),(variable(y),()))), total).
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
    optimize_maximizeSum(dummy_opt,EXPR,X) :- item(X,V),
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
---

## Precision

**[Declaration]**{.badge .declaration }

By default, the optimization module uses a precision of `1` for floating-point calculations. This can be adjusted using the `optimize_precision/1` predicate.

```prolog
optimize_precision(Precision)
```

| Name | Description |
| :--- | :--- |
| `Precision` | The [Value] to be used for floating-point calculations. Must be a positive [Int]. |

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
