# Error Handling

This page documents the types of errors and warnings that can be reported by the constraint handler during model generation or solving.

!!! Warning
    This section may frequently change as error messages get more streamlined.

## Overview

Here, we outline the various warning types that can be reported by the constraint handler.

| Type | Description |
| :--- | :--- |
| **Expressions** | |
| [`expression(pythonError)`](#python-error) | An error occurred in Python during the evaluation of an [Expression]. |
| [`expression(syntaxError)`](#syntax-error) | A syntax error was encountered in an [Expression]. |
| [`expression(notImplemented)`](#not-implemented) | An [Expression] uses a feature that is not (yet) implemented. |
| [`expression(zeroDivisionError)`](#zero-division-error) | An [Expression] attempted to divide by zero. |
| **Statements** | |
| [`statement(evaluatorError)`](#evaluator-error) | An error occurred within the constraint handler's evaluator. |
| [`statement(notImplemented)`](#not-implemented_1) | A [Statement] uses a feature that is not (yet) implemented. |
| [`statement(pythonError)`](#python-error_1) | An error occurred in Python during the evaluation of a [Statement]. |
| **Variables** | |
| [`variable(emptyDomain)`](#empty-domain) | A [Variable] has an empty [Domain], meaning it has no possible [Values]. |
| [`variable(undeclared)`](#undeclared) | A [Variable] has a defined [Domain] but has not been declared. |
| [`variable(multipleDeclarations)`](#multiple-declarations) | A [Variable] has multiple declarations with different [Domains]. |
| [`variable(multipleDefinitions)`](#multiple-definitions) | A [Variable] is defined more than once within the same scope. |
| [`variable(confusingName)`](#confusing-name) | A [Variable] has a name that could be confused with reserved keywords, operators, numbers or types. |
| **Preference** | |
| [`preference(unsupported)`](#unsupported) | A [Preference] uses a feature that is not (yet) supported. |
| **propagator** | |
| [`propagator`](#propagator) | An error occurred in the propagator. |
| **Type** | |
| `[type(failed_operation)]` | An [Operation] failed due to a type error. |
| **Other** | |
| [`otherError`](#other-error) | A generic error that does not fit into the other categories. |

---

## Warning

**[Result]**{.badge .result }

The constraint handler has the ability to capture certain types of errors without interrupting the solving process. Instead, whenever such errors are encountered, a `warning` predicate is used to report these issues.

!!! Note
    In order to get useful warnings, users are advised to provide [Declarations] and [Definitions] with meaningful identifiers in their encodings.

Warnings will appear as atoms of the `warning/3` predicate:

```prolog
warning(Type, Labels, Details)
```

| Name | Description |
| :--- | :--- |
| `Type` | The type of warning being issued. |
| `Labels` | A list of terms, usually identifiers, related to the warning. |
| `Details` | Additional details about the warning (e.g. variable names, expressions, etc.) that can help users understand the issue. |

!!! Example
    The following resembles a warning being issued when a variable is defined multiple times:

    ```prolog
    warning(variable(multipleDefinitions),(d_x,(d_x_2,())),(x,val(int,1),val(int,2)))
    ```

    This warning indicates that the variable `x` was defined multiple times with different values, and it provides the details of the definitions that caused the conflict.

    Here, the variable was once defined in `d_x` with the value `val(int,1)` and then again in `d_x_2` with the value `val(int,2)`, which is not allowed.

---

## Ignore Warning
**[Declaration]**{.badge .declaration }

Users have the option to ignore specific warnings by using the `ignore_warning/1` predicate. This allows users to suppress warnings that they are aware of and do not wish to be notified about.

```prolog
ignore_warning(WarningType)
```

| Name | Description |
| :--- | :--- |
| `WarningType` | The type of warning to ignore. This should match the `Type` field of the warnings you wish to suppress. |

!!! Example
    To ignore warnings about variables with confusing names, you can use:

    ```prolog
    ignore_warning(variable(confusingName)).
    ```

    This will suppress any warnings of the type `variable(confusingName)` from being reported in the future.

---

## Forbid Warning
**[Declaration]**{.badge .declaration }

Users can also choose to forbid specific warnings using the `forbid_warning/1` predicate. This means that if a forbidden warning is encountered, it will be treated as a failed constraint.

!!! Info
    Ignored warnings cannot be forbidden, and vice versa. If a warning type is both ignored and forbidden, it will be treated as ignored.

```prolog
forbid_warning(Identifier, WarningType)
```

| Name | Description |
| :--- | :--- |
| `Identifier` | A unique identifier for this specific statement. |
| `WarningType` | The type of warning to forbid. This should match the `Type` field of the warnings you wish to treat as errors. |

!!! Example
    To forbid warnings about variables with empty domains, you can use:

    ```prolog
    forbid_warning(empty_domain_forbidden, variable(confusingName)).
    ```

    This will cause any warning of the type `variable(confusingName)` to be treated as an error, and it will prevent the model from being generated if such a warning is encountered.

---

## Error Recovery / Partial Models
The constraint handler is designed to handle errors gracefully and provide useful feedback to users without crashing. When an error is encountered during the evaluation of an [Expression] or the execution of a [Statement], the constraint handler first emits a warning to inform the user about the issue. Then, instead of crashing, it sets the result value of the failed operation to `bad`. This allows the model generation process to continue and produce a partial model that includes as much information as possible, even in the presence of errors.

The operations and executions that receive `bad` as an input can then choose how to handle it. For example, they could propagate the `bad` value further, or they could implement some form of error recovery to produce a valid result despite the error.

!!! Example
    Consider the following variable definitions:
    ```
    variable_define(d_x, x, val(int, 6)).
    variable_define(d_y, y, val(int, 2)).
    variable_define(d_a, a, operation(add, (variable(y),(variable(y),(variable(y),()))))).
    variable_define(d_s, s, operation(sub, (variable(x),(variable(a),())))).
    variable_define(d_d, d, operation(div, (variable(x),(variable(s),())))).
    variable_define(d_m, m, operation(mult, (variable(d),(variable(y),())))).
    ```

    We expect `a` to be evaluated as `y + y + y`, which should yield `6`. Then, `s` would be `x - a`, which should yield `0`. Finally, when evaluating `d`, we would attempt to divide `x` by `s`, which would lead to a division by zero error.

    Without error recovery, the system would crash when it encounters this error, leaving neither meaningful information, nor a solution. However, with error recovery, the system can instead set `d` to `bad`, and then propagate this value to `m`, which would also be set to `bad`. This way, we can still obtain a partial model where `x`, `y`, `a`, and `s` have their expected values, while `d` and `m` are marked as `bad` due to the error.

    The output model contains:
    ```
    value(x,val(int,6))
    value(y,val(int,2))
    value(a,val(int,6))
    value(s,val(int,0))
    value(d,bad)
    value(m,bad)
    warning(expression(zeroDivisionError),(),(div,(val(int,6),(val(int,0),()))))
    ```
    It provides the values for `x`, `y`, `a`, and `s`, while indicating that `d` and `m` are `bad` due to the division by zero error, which is also reported as a warning.

---
## Warning Types
This section provides detailed descriptions of the various warning types that can be reported by the constraint handler.

### Expression Warnings
This section covers warnings related to the evaluation of [Expressions].

#### Python Error
An error occurred in Python during the evaluation of an [Expression].

```prolog
warning(expression(pythonError), _, (Operator, Arguments, Message))
```

| Name | Description |
| :--- | :--- |
| `Type` | `expression(pythonError)` |
| `Details` | The operator, arguments, and a message describing the error. |

#### Syntax Error
This warning occurs when there is a syntax error in an [Expression].

```prolog
warning(expression(syntaxError), _, Message)
```

| Name | Description |
| :--- | :--- |
| `Type` | `expression(syntaxError)` |
| `Details` | A message describing the syntax error. |

!!! Example
    ```prolog
    variable_define(d_a, a, val(str, "a")).
    variable_define(d_b, b, val(str, "b")).
    variable_define(d_c, c, val(str, "c")).
    variable_define(d_x,x, operation(eq, (variable(a),(variable(b),(variable(c),()))))).
    ```

    Raises the warning:
    ```prolog
    warning(expression(syntaxError),(),"eq takes two arguments, not ['a', 'b', 'c']")
    ```

#### Not Implemented
This warning occurs when an [Expression] uses a feature that is not (yet) implemented.

```prolog
warning(expression(notImplemented), _, Message)
```

| Name | Description |
| :--- | :--- |
| `Type` | `expression(notImplemented)` |
| `Details` | A message describing the feature that is not implemented. |

#### Zero Division Error
This warning occurs when an [Expression] attempts to divide by zero.

```prolog
warning(expression(zeroDivisionError), _, Message)
```

| Name | Description |
| :--- | :--- |
| `Type` | `expression(zeroDivisionError)` |
| `Details` | A message describing the division by zero error. |

!!! Example
    ```prolog
    variable_define(d_x,x, operation(int_div, (val(int, 2),(val(int, 0),())))).
    ```

    Raises the warning:
    ```prolog
    warning(expression(zeroDivisionError),(),(int_div,(val(int,2),(val(int,0),()))))
    ```
---

### Statement Warnings
This section covers warnings related to the evaluation of [Statements].

#### Evaluator Error
This warning occurs when there is an error within the constraint handler's evaluator.

```prolog
warning(statement(evaluatorError), _, Message)
```

| Name | Description |
| :--- | :--- |
| `Type` | `statement(evaluatorError)` |
| `Details` | A message describing the error that occurred in the evaluator. |

#### Not Implemented
This warning occurs when a [Statement] uses a feature that is not (yet) implemented.

```prolog
warning(statement(notImplemented), _, Message)
```

| Name | Description |
| :--- | :--- |
| `Type` | `statement(notImplemented)` |
| `Details` | A message describing the feature that is not implemented. |

#### Python Error
This warning occurs when there is an error in Python during the evaluation of a [Statement].

```prolog
warning(statement(pythonError), (Label,()), ("error running", Message))
```

| Name | Description |
| :--- | :--- |
| `Type` | `statement(pythonError)` |
| `Labels` | The identifier of the statement that caused the error. |
| `Details` | A message describing the error that occurred in Python. |

!!! Example
    ```prolog
    variable_define(execution_input(my_exec, a), val(int, 5)).

    execution_declare(my_exec, S, (a,()), (a,())) :-
        S = assign(a, operation(int_div, (val(int, 2),(val(int, 0),())))).

    execution_run(my_exec).
    ```

    Raises the warning:
    ```prolog
    warning(statement(pythonError),(my_exec,()),("error running","(Expression(symbol=<ExpressionWarning.zeroDivisionError: 'zeroDivisionError'>), '2/0')"))
    ```
---

### Variable Warnings
This section covers warnings related to [Variable] declarations and definitions.

#### Empty Domain
This warning occurs when a [Variable] does not have any possible values in its [Domain].

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
#### Confusing Name
This warning occurs when a [Variable] has a name that could be confused with reserved keywords,
operators, numbers or types.

```prolog
warning(variable(confusingName), _, ((Scope,Name), Reason))
```

| Name | Description |
| :--- | :--- |
| `Type` | `variable(confusingName)` |
| `Details` | The scope and name of the variable, along with a message describing why the name is confusing. |

!!! Example
    Variable defined with a name that could be confused with a reserved keyword.

    ```prolog
    variable_define(d_and, assert, val(int, 1)).
    ```

    Raises the warning:
    ```prolog
    warning(variable(confusingName),(),(((),assert),keyword))
    ```

---

### Preference Warnings
This section covers warnings related to [Preference] statements.
#### Unsupported
This warning occurs when a [Preference] uses a feature that is not (yet) supported.

```prolog
warning(preference(unsupported), _, Details)
```

| Name | Description |
| :--- | :--- |
| `Type` | `preference(unsupported)` |
| `Details` | A tuple describing the feature that is not supported. |

!!! Example
    Defining multiple preference values for the same variable.

    ```prolog
    preference_variableValue(dummy,z,val(int,2),5).
    preference_variableValue(dummy,z,val(int,2),7).
    ```

    Raises the warning:
    ```prolog
    warning(preference(unsupported),(),("multiple scores for the same expression",operation(eq,(variable(z),(val(int,2),()))),5,7))
    ```

    Here, the details indicate that there are multiple scores defined for the same expression `z == 2`, which is not supported.

---

### Propagator Warnings
This section covers warnings related to the propagator.

#### Propagator
This warning occurs when there is an error in the propagator.

```prolog
warning(propagator, _, Message)
```

| Name | Description |
| :--- | :--- |
| `Type` | `propagator` |
| `Details` | A message describing the error that occurred in the propagator. |

---

### Type Warnings
This section covers warnings related to type errors.

#### Failed Operation
This warning occurs when the type system is not able to resolve the type of an [Operation].

```prolog
warning(type(failed_operation), _, (Scope, Operator, Arguments))
```

| Name | Description |
| :--- | :--- |
| `Type` | `type(failed_operation)` |
| `Details` | The scope, operator, and arguments of the operation that failed. |

---

### Other Warnings
This section covers warnings that do not fit into the previous categories.

#### Other Error

```prolog
warning(otherError, _, Message)
```

| Name | Description |
| :--- | :--- |
| `Type` | `otherError` |
| `Details` | A message describing the error. |
