%*! direct_query(Expression)

Marks an expression as needing direct evaluation in the compile engine.

Expressions that occur in [ensure], [evaluate], variable assignments, set or
multimap assignments, and derived helper expressions are collected through this
predicate. Once an expression is a `direct_query`, the direct evaluation
pipeline will recursively inspect its subexpressions and derive its value using
[_se_value].

Args:
    - Expression: The [Expression] that should be evaluated directly.
*%

%*! _direct_lazy(Expression)

Marks an operator whose argument list should not be expanded eagerly by
`direct_query/1`.

Most operations expose their arguments as additional direct queries so that the
direct evaluator can compute them recursively. Lazy operators are excluded from
that default traversal because they need special handling, for example to
preserve short-circuit or error-recovery behavior.

Args:
    - Expression: The [Operator] treated lazily by the direct evaluator.
*%

%*! _operator_recoverable(Operator)

Declares an operator as recoverable. 

This means that if the operator is used with `bad` arguments, it may still be possible to 
recover a non-`bad` value instead of `bad`, depending on the operator and the other arguments.

!!! Example 
    if there are `bad` arguments in a multiplication, but there is also a `0`, 
    the result can be recovered as `0` instead of `bad`.

Args:
    - Operator: The [Operator] declared as recoverable.
*%

%*! ensure(Label, Expression)

Requires an expression to evaluate to `true`.

If the expression evaluates to `false`, the current model is rejected. If it evaluates to `bad`, 
the failure is handled through the usual warning and recovery mechanisms.

Args:
    - Label: The optional [Label] attached to the ensure declaration.
    - Expression: The boolean [Expression] that must hold.
*%

%*! ensure(Expression)

Shorthand for [ensure/2] using an anonymous label.

Args:
    - Expression: The boolean [Expression] that must hold.
*%

%*! evaluate(Label, Operator, Arguments)

Requests the direct evaluation of one operator application.

This predicate is mainly useful for inspecting the value of an expression
without first assigning it to a variable. The result is exposed through the
result predicate [evaluated/3].

Args:
    - Label: The optional [Label] attached to the evaluation request.
    - Operator: The [Operator] to evaluate.
    - Arguments: The argument list passed to the operator.
*%

%*! evaluate(Operator, Arguments)

Shorthand for [evaluate/3] using an anonymous label.

Args:
    - Operator: The [Operator] to evaluate.
    - Arguments: The argument list passed to the operator.
*%

%*! evaluated(Operator, Arguments, Value)

The result of a direct evaluation request.

Args:
    - Operator: The [Operator] that was evaluated.
    - Arguments: The argument list used for the evaluation.
    - Value: The resulting value, possibly `bad` if evaluation failed.
*%