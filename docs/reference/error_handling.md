# Error Handling

This page documents the types of errors and warnings that can be reported by the constraint handler during model generation or solving.

## Warning

The constraint handler has the ability to capture certain types of errors without interrupting the solving process. Instead, whenever such errors are encountered, a `warning/1` predicate is used to report these issues.

```prolog
warning(Warning)
```

| Name | Description |
| :--- | :--- |
| `Warning` | Usually a tuple containing information about the identified problem. |

!!! Note
    This is where statement identifiers can be provided to help users locate the source of the warning.

!!! Example
    The following resembles a warning being issued when a variable is defined multiple times:

    ```prolog
    warning((x, "was defined twice:", my_expression_1, my_expression_2)).
    ```

    This warning provides the variable name `x` and the two expressions that defined it, making it easy for users to identify and resolve the issue.

---

## Error Types

Here, we outline the various error types that can be reported by the constraint handler.

### Variable Defined Twice
This error occurs when a variable is defined more than once within the same scope.

```prolog
warning((X,"was defined twice:",E1,E2))
```

| Name | Description |
| :--- | :--- |
| `X` | The name of the variable that was defined multiple times. |
| `E1` | The first expression assigned to the variable. |
| `E2` | The second expression assigned to the variable. |

### Variable Declared Twice
This error occurs when a variable is declared more than once within the same scope.

```prolog
warning((X,"was declared twice:",D1,D2))
```

| Name | Description |
| :--- | :--- |
| `X` | The name of the variable that was defined multiple times. |
| `D1` | The first domain declared for the variable. |
| `D2` | The second domain declared for the variable. |

### Variable Not Declared
This error occurs when a variable has a defined domain but has not been declared.

```prolog
warning((X,"has a domain but was never declared."))
```

| Name | Description |
| :--- | :--- |
| `X` | The name of the variable that was not declared. |

### Expression Evaluation Error
This error occurs when there is an issue evaluating an expression.

```prolog
warning((Operator, Arguments, Message))
```

| Name | Description |
| :--- | :--- |
| `Operator` | The operator involved in the evaluation error. |
| `Arguments` | The arguments passed to the operator that caused the error. |
| `Message` | A message describing the nature of the evaluation error. |