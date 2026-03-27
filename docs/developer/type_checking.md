# Type Checking
This page documents the type checking system of the constraint handler responsible for resolving the types of expressions and executions. This system provides several predicates for finding the types of variables, expressions, and executions. Additionally, some of these predicates can be used to implement custom type checking.

!!! Warning "Important"
    The type system is still a work in progress and is not yet fully implemented. For example, some operations require the concept of union types, which are not yet supported.

## Variable
If the type of a variable can be resolved, it results in an atom from the `type_variable/3` predicate.

```prolog
type_variable(Scope, Name, Type).
```

| Name | Description |
| --- | --- |
| Scope | The scope the variable is defined in. |
| Name | The identifier of the variable. |
| Type | The type of the variable, like a [Base Type] or [Collection]. |

!!! Example
    The variable `x` is defined as an integer in the current scope.
    ```prolog
    variable_define(d_x, x, val(int,3)).
    ```

    This results in the type variable:
    ```prolog
    type_variable((),x,int)
    ```

## Expression
Similar to variables, the type of an expression can be resolved using the `type_expression/3` predicate.

```prolog
type_expression(Scope, Expression, Type).
```

| Name | Description |
| --- | --- |
| Scope | The scope the expression is defined in. |
| Expression | The expression to resolve the type of. |
| Type | The type of the expression, like a [Base Type] or [Collection]. |

!!! Example
    Given the same variable definition as before:

    ```prolog
    variable_define(d_x, x, val(int,3)).
    ```

    The expression for the value itself is also typed.

    ```prolog
    type_expression((),val(int,3),int)
    ```

## Operations
Going beyond simple variables and their values we find operations. In order to resolve these, each operation requires a declaration that specifies the operator name and the types of its arguments and return value.

Any operator that is used with types that do not match any of its declarations throws the `[type(failed_operation)]` warning.

### Fixed Arity
For operations with a fixed number of arguments, the `operator_declare/3` predicate is used.

```prolog
operator_declare(Name, ArgumentTypes, ReturnType).
```

| Name | Description |
| --- | --- |
| Name | The name of the operator. |
| ArgumentTypes | A list of types for the operator's arguments. |
| ReturnType | The type of the operator's return value. |

!!! Example
    If we wanted to define the addtion only between two integers we could declare the operator as follows:

    ```prolog
    operator_declare(int_add, (int,(int,())), int).
    ```

    This would lead the type system to be able to resolve the variable:

    ```prolog
    variable_define(d_x, x, operation(int_add, (val(int,1),(val(int,2),())))).
    ```

    to the type variable:

    ```prolog
    type_variable((),x,int)
    ```

### Variable Arity
For operations with a variable number of arguments, the `operator_declare_variadic/4` predicate is used.

In the current implementation, we employ a ranking system to determine the return type of variadic operators. More precisely, each declaration specifies some element or argument type corresponding to some return type together with a rank. The return type of the operator is then determined by the argument with the highest rank.

```prolog
operator_declare_variadic(Name, ArgumentType, ReturnType, Rank).
```

| Name | Description |
| --- | --- |
| Name | The name of the operator. |
| ArgumentType | The type of the operator's arguments. |
| ReturnType | The type of the operator's return value. |
| Rank | The rank of the return type, used to determine the return type when multiple arguments of differing types are present. |

!!! Example
    If we wanted to define the addition between integers and floats we could declare the operator as follows:

    ```prolog
    operator_declare_variadic(add, int, int, 1).
    operator_declare_variadic(add, float, float, 2).
    ```

    If an addition only uses integers it would resolve to an integer, because all arguments result in a type with rank 1. However,
    if even a single float is present it would resolve to a float, because float represents a type with a higher rank than int. For example, the variable:

    ```prolog
    variable_define(d_x, x, operation(add, (val(int,1),(val(float,float("2.0")),(val(int,3),()))))).
    ```
    would resolve to the type variable:

    ```prolog
    type_variable((),x,float)
    ```

## Sub Expressions
Sub expressions are treated exactly the same as expressions and also have their type resolved using the `type_expression/3` predicate. This means that for each type resolution of an expression, the types of all its sub expressions are also resolved. This allows for a more fine-grained type checking and can be used to implement a warning system for potentially bad operations, such as adding an integer and a string inside of a larger expression.

!!! Example
    Given the same variable definition as before:

    ```prolog
    variable_define(d_x, x, operation(add, (val(int,1),(val(float,float("2.0")),(val(int,3),()))))).
    ```

    While it is true that this adds the atom
    ```prolog
    type_variable((),x,float)
    ```

    it actually adds the following atoms in total:
    ```prolog
    type_expression((),val(int,1),int)
    type_expression((),val(float,float("2.0")),float)
    type_expression((),val(int,3),int)
    type_expression((),operation(add,(val(int,1),(val(float,float("2.0")),(val(int,3),())))),float)
    type_variable((),x,float)
    ```

    Here, we can see one resolution for each argument of the addition operation, as well as a resolution for the entire expression.
