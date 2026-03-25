# Conditionals

This page documents the conditional expressions available in the constraint handler. All conditionals can be used just like normal operators known from the [Base Types] or [Collections] documentation pages.

## Notation
On this page, we will expand the notation introduced in the [Collections] documentation page to also include conditionals.

Even though a `Condition` is an [Expression] that evaluates to [bool], we will mark it as `C` in the operator signatures to better indicate that this is the condition the respective conditional is based on.

---

## If (If-Then)

Sometimes operations should only be performed when a certain condition is met. For this, the `if` operator can be used.

| Operator | Name | Signature | Description |
| :--- | :--- | :--- | :--- |
| `if` | If-Then | (C, A) $\to$ [none] \| A | If the condition `C` holds, then the [Expression] `A` is evaluated. Otherwise, the conditional evaluates to [none]. |

!!! Example
    ```prolog
    variable_define(z, operation(if, (val(bool, true),(val(int,2),())))).
    ```
    Here `z` will be assigned the value `2`, since the condition is `true`.

    The model will contain the atom:
    ```prolog
    value(z,val(int,2))
    ```

    However:

    ```prolog
    variable_define(z, operation(if, (val(bool, false),(val(int,2),())))).
    ```

    Here, since the condition is `false`, `z` will be assigned [none].

    The model will contain the atom:
    ```prolog
    value(z,val(none, none))
    ```

---

## Ite (If-Then-Else)

The `ite` operator expands on the `if` operator by allowing to specify an alternative [Expression] to be evaluated when the condition does not hold.

| Operator | Name | Signature | Description |
| :--- | :--- | :--- | :--- |
| `ite` | If-Then-Else | (C, A, B) $\to$ A \| B | If the condition [`C`] holds, evaluates the expression `A`, otherwise the expression `B`. |

!!! Example
    ```prolog
    variable_define(z, operation(ite, (val(bool, true),(val(int,2),(val(int,5),()))))).
    ```
    Here, just like in the `if` case, `z` will be assigned the value `2`, since the condition is `true`.

    The model will contain the atom:
    ```prolog
    value(z,val(int,2))
    ```

    However:

    ```prolog
    variable_define(z, operation(ite, (val(bool, true),(val(int,2),(val(int,5),()))))).
    ```

    This time, when the condition is `false`, `z` will be assigned the value `5`.

    The model will contain the atom:
    ```prolog
    value(z,val(int,5))
    ```

---

## Default

The `default` operator is used to provide a fallback value if the first [Expression] is undefined (e.g. evaluates to [`none`]).

| Operator | Name | Signature | Description |
| :--- | :--- | :--- | :--- |
| `default` | Default | (A, B) $\to$ A \| B | Returns the value of `A` if it is defined, otherwise the value of `B`. |

!!! Example
    ```prolog
    variable_define(z, operation(default, (val(int, 2),(val(int,5),())))).
    ```
    Here, because the value is defined, `z` will be assigned the value `2`.

    The model will contain the atom:
    ```prolog
    value(z,val(int,2))
    ```

    However:

    ```prolog
    variable_define(z, operation(default, (val(none, none),(val(int,5),())))).
    ```

    Here, since the first value is [none], `z` will be assigned the value `5`.

    The model will contain the atom:
    ```prolog
    value(z,val(int,5))
    ```

---

## hasValue

The `hasValue` operator checks whether an [Expression] is defined (not `none`).

| Operator | Name | Signature | Description |
| :--- | :--- | :--- | :--- |
| `hasValue` | Has Value | (T) $\to$ [bool] | Returns `true` if the argument is defined, otherwise `false`. |

!!! Example
    ```prolog
    variable_define(z, operation(hasValue, (val(none, none),()))).
    ```
    Here, since the value is `none`, `z` will be assigned the value `false`.

---
