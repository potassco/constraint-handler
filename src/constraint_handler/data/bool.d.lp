%*! bool_evaluate(Label, Expression)

Initiate an evaluation of a boolean expression.

This is similar to [evaluate/2] but only evaluates boolean expressions.

!!! Info
    Unlike most [Declarations] in constraint-handler,
    `bool_evaluate/2` can also be used in the body of ASP rules.

Args:
    - Label: The optional [Label] to identify the evaluation (e.g., for warnings or errors).
     If not provided, a default label will be used. (see: [bool_evaluate/1])
    - Expression: The boolean [Expression] to evaluate.
*%

%*! bool_evaluate(Expression)

Initiate an evaluation of a boolean expression without providing a label.

This is a convenience predicate for [bool_evaluate/2] that provides a default label for the evaluation.

!!! Info
    Like [bool_evaluate/2], this predicate can also be used in the body of ASP rules.

Args:
    - Expression: The boolean [Expression] to evaluate.
*%

%*! bool_evaluated(Expression, Value)

The result of the evaluation of a boolean expression.

Args:
    - Expression: The boolean [Expression] that was evaluated.
    - Value: The result of the evaluation, which can be a [Bool], or [Bad].
*%
