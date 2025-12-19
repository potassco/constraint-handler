# Conditionals

This page documents the conditional expressions available in the constraint handler. All conditionals can be used just like normal operators known from the [base_types](base_types.md) or [collections](collections.md) documentation pages.

---

## If (If-Then)

Sometimes operations should only be performed when a certain condition is met. For this, the `if` operator can be used.

| Operator | Name | Arity | Description | Return Type |
| :--- | :--- | :--- | :--- | :--- |
| `if` | If-Then | 2 | If the `Condition` holds, then the `Expression` is evaluated. | [none](#none) \| [any] |

!!! Example
    ```prolog
    assign(name, z, operation(if, (val(bool, true),(val(int,2),())))).
    ```
    Here `z` will be assigned the value `2`, since the condition is `true`.

    The model will contain the atom:
    ```prolog
    value(z,int,2)
    ```

    However:

    ```prolog
    assign(name, z, operation(if, (val(bool, false),(val(int,2),())))).
    ```

    Here, since the condition is `false`, `z` will be assigned [none](base_types.md#none).

    The model will contain the atom:
    ```prolog
    value(z,none, none)
    ```

---

## Ite (If-Then-Else)

The `ite` operator expands on the `if` operator by allowing to specify an alternative expression to be evaluated when the condition does not hold.

| Operator | Name | Arity | Description | Return Type |
| :--- | :--- | :--- | :--- | :--- |
| `ite` | If-Then-Else | 3 | If the `Condition` holds, evaluates the first expression, otherwise the second. | [any] |

!!! Example
    ```prolog
    assign(name, z, operation(ite, (val(bool, true),(val(int,2),(val(int,5),()))))).
    ```
    Here, just like in the `if` case, `z` will be assigned the value `2`, since the condition is `true`.

    The model will contain the atom:
    ```prolog
    value(z,int,2)
    ```

    However:

    ```prolog
    assign(name, z, operation(ite, (val(bool, true),(val(int,2),(val(int,5),()))))).
    ```

    This time, when the condition is `false`, `z` will be assigned the value `5`.

    The model will contain the atom:
    ```prolog
    value(z,int,5)
    ```

---

## Default

The `default` operator is used to provide a fallback value if the first expression is undefined (e.g. evaluates to [`none`](base_types.md#none)).

| Operator | Name | Arity | Description | Return Type |
| :--- | :--- | :--- | :--- | :--- |
| `default` | Default | 2 | Returns the first value if it is defined, otherwise the second. | [any] |

!!! Example
    ```prolog
    assign(name, z, operation(default, (val(int, 2),(val(int,5),())))).
    ```
    Here, because the value is defined, `z` will be assigned the value `2`.

    The model will contain the atom:
    ```prolog
    value(z,int,2)
    ```

    However:

    ```prolog
    assign(name, z, operation(default, (val(none, none),(val(int,5),())))).
    ```

    Here, since the first value is [none](base_types.md#none), `z` will be assigned the value `5`.

    The model will contain the atom:
    ```prolog
    value(z,int,5)
    ```

---

## hasValue

The `hasValue` operator checks whether an expression is defined (not `none`).

| Operator | Name | Arity | Description | Return Type |
| :--- | :--- | :--- | :--- | :--- |
| `hasValue` | Has Value | 1 | Returns `true` if the argument is defined, otherwise `false`. | [bool](base_types.md#bool) |

!!! Example
    ```prolog
    assign(name, z, operation(hasValue, (val(none, none),()))).
    ```
    Here, since the value is `none`, `z` will be assigned the value `false`.

---