# Conditionals

This page documents the conditional expressions available in the constraint handler. All conditionals can be used just like normal operators known from the [base_types](base_types.md) or [collections](collections.md) documentation pages.

---

## If (If-Then)

Sometimes operations should only be performed when a certain condition is met. For this, the `if` operator can be used.

| Operator | Name | Signature | Description |
| :--- | :--- | :--- | :--- |
| `if` | If-Then | ([bool](base_types.md#bool), any) $\to$ [none](base_types.md#none) \| any <br><br> **Example:** <br> (true, [int](base_types.md#int)) $\to$ [int](base_types.md#int) <br> (false, [int](base_types.md#int)) $\to$ [none](base_types.md#none)| If the `Condition` holds, then the `Expression` is evaluated. Otherwise, the conditional evaluates to [none](base_types.md#none). |

!!! Example
    ```prolog
    variable_define(name, z, operation(if, (val(bool, true),(val(int,2),())))).
    ```
    Here `z` will be assigned the value `2`, since the condition is `true`.

    The model will contain the atom:
    ```prolog
    value(z,int,2)
    ```

    However:

    ```prolog
    variable_define(name, z, operation(if, (val(bool, false),(val(int,2),())))).
    ```

    Here, since the condition is `false`, `z` will be assigned [none](base_types.md#none).

    The model will contain the atom:
    ```prolog
    value(z,none, none)
    ```

---

## Ite (If-Then-Else)

The `ite` operator expands on the `if` operator by allowing to specify an alternative expression to be evaluated when the condition does not hold.

| Operator | Name | Signature | Description |
| :--- | :--- | :--- | :--- |
| `ite` | If-Then-Else | ([bool](base_types.md#bool), any, any) $\to$ any <br><br> **Example:** <br> (true, [int](base_types.md#int), [bool](base_types.md#bool)) $\to$ [int](base_types.md#int) <br> (false, [int](base_types.md#int), [bool](base_types.md#bool)) $\to$ [bool](base_types.md#bool)| If the `Condition` holds, evaluates the first expression, otherwise the second. |

!!! Example
    ```prolog
    variable_define(name, z, operation(ite, (val(bool, true),(val(int,2),(val(int,5),()))))).
    ```
    Here, just like in the `if` case, `z` will be assigned the value `2`, since the condition is `true`.

    The model will contain the atom:
    ```prolog
    value(z,int,2)
    ```

    However:

    ```prolog
    variable_define(name, z, operation(ite, (val(bool, true),(val(int,2),(val(int,5),()))))).
    ```

    This time, when the condition is `false`, `z` will be assigned the value `5`.

    The model will contain the atom:
    ```prolog
    value(z,int,5)
    ```

---

## Default

The `default` operator is used to provide a fallback value if the first expression is undefined (e.g. evaluates to [`none`](base_types.md#none)).

| Operator | Name | Signature | Description |
| :--- | :--- | :--- | :--- |
| `default` | Default | (any, any) $\to$ any <br><br> **Example:** <br> ([int](base_types.md#int), [bool](base_types.md#bool)) $\to$ [int](base_types.md#int) <br> ([none](base_types.md#none), [bool](base_types.md#bool)) $\to$ [bool](base_types.md#bool) | Returns the first value if it is defined, otherwise the second. |

!!! Example
    ```prolog
    variable_define(name, z, operation(default, (val(int, 2),(val(int,5),())))).
    ```
    Here, because the value is defined, `z` will be assigned the value `2`.

    The model will contain the atom:
    ```prolog
    value(z,int,2)
    ```

    However:

    ```prolog
    variable_define(name, z, operation(default, (val(none, none),(val(int,5),())))).
    ```

    Here, since the first value is [none](base_types.md#none), `z` will be assigned the value `5`.

    The model will contain the atom:
    ```prolog
    value(z,int,5)
    ```

---

## hasValue

The `hasValue` operator checks whether an expression is defined (not `none`).

| Operator | Name | Signature | Description |
| :--- | :--- | :--- | :--- |
| `hasValue` | Has Value | (any) $\to$ [bool](base_types.md#bool) | Returns `true` if the argument is defined, otherwise `false`. |

!!! Example
    ```prolog
    variable_define(name, z, operation(hasValue, (val(none, none),()))).
    ```
    Here, since the value is `none`, `z` will be assigned the value `false`.

---