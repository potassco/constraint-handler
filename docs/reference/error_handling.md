# Error Handling

This page documents the types of errors and warnings that can be reported by the constraint handler during model generation or solving.

!!! Warning
    This section may frequently change as error messages get more streamlined.

## Warning

**[Result]**{.badge .result }

The constraint handler has the ability to capture certain types of errors without interrupting the solving process. Instead, whenever such errors are encountered, a `warning` predicate is used to report these issues.

!!! Note
    In order to get useful warnings, users are advised to provide statements with meaningful identifiers in their encodings.

Currently, there are two such predicates in use.

```prolog
warning(Warning)
```

| Name | Description |
| :--- | :--- |
| `Warning` | Usually a tuple containing information about the identified problem. |

A version that provides more details:

```prolog
warning(Type, Identifiers, Details)
```

| Name | Description |
| :--- | :--- |
| `Type` | The type of warning being issued. |
| `Identifiers` | A list of statement identifiers related to the warning. |
| `Details` | Additional details about the warning. |

!!! Example
    The following resembles a warning being issued when a variable is defined multiple times:

    ```prolog
    warning((x, "was defined twice:", my_expression_1, my_expression_2)).
    ```

    This warning provides the variable name `x` and the two expressions that defined it, making it easy for users to identify and resolve the issue.

---

## Error Types

Here, we outline the various error types that can be reported by the constraint handler.

### Variable
This section covers errors related to [Variable] declarations and definitions.

#### Empty Domain
This error occurs when a [Variable] does not have any possible values in its [Domain].

```prolog
warning(variable(emptyDomain), _,Variable)
```

| Name | Description |
| :--- | :--- |
| `Type` | `variable(emptyDomain)` |
| `Details` | The name of the variable that is empty. |

!!! Example
    Variable declared with an empty list as its domain.

    ```prolog
    variable_declare(d_a,a,fromList(())).
    ```
    
    Raises the warning:
    ```prolog
    warning(variable(emptyDomain),(d_a,()),a)
    ```

#### Undeclared
This error occurs when a [Variable] has a defined [Domain] but has not been [declared][variable_declare].

```prolog
warning(variable(undeclared), (), Variable)
```

| Name | Description |
| :--- | :--- |
| `Type` | `variable(undeclared)` |
| `Details` | The name of the variable that was not declared. |

!!! Example
    Variable defined with a domain but not declared.

    ```prolog
    variable_domain(c,val(symbol,(red;green;blue))).
    ```
    
    Raises the warning:
    ```prolog
    warning(variable(undeclared),(),c)
    ```

#### Multiple Declarations
This error occurs when a [Variable] has multiple declarations with different [Domains].

```prolog
warning(variable(multipleDeclarations), _, (Variable, Domains...))
```

| Name | Description |
| :--- | :--- |
| `Type` | `variable(multipleDeclarations)` |
| `Details` | The name of the variable and the different domains it was declared with. |

!!! Example
    Variable declared multiple times with different domains.

    ```prolog
    variable_declare(d_u,u,fromFacts).
    variable_declare(d_u,u,boolDomain).
    ```
    
    Raises the warning:
    ```prolog
    warning(variable(multipleDeclarations),(d_u,(d_u,())),(u,boolDomain,fromFacts))
    ```

#### Multiple Definitions
This error occurs when a [Variable] is defined more than once within the same scope.

```prolog
warning(variable(multipleDefinitions), _, (Variable, Expressions...))
```

| Name | Description |
| :--- | :--- |
| `Type` | `variable(multipleDefinitions)` |
| `Details` | The name of the variable and the expressions that defined it. |

!!! Example
    Variable defined multiple times.

    ```prolog
    variable_define(d_x,x,val(int, 1)).
    variable_define(d_x,x,val(int, 2)).
    ```
    
    Raises the warning:
    ```prolog
    warning(variable(multipleDefinitions),(d_x,(d_x,())),(x,val(int,1),val(int,2)))
    ```

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