# Constraints

This page documents how the constraint handler enforces specific conditions on values and variables within models.

## Ensure
The constraint handler deals with constraints by allowing users to specify conditions that must hold true in the model.

### Input
To specify conditions that must hold true in the model, the constraint handler provides the `ensure/2` predicate.

```prolog
ensure(Name, Condition).
```

| Name | Description |
| :--- | :--- |
| `Name` | **TODO** |
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