%*! optimize_maximizeSum(Label, Expression, Id, Priority)

Adds one optimization contribution that should be maximized.

The contribution is identified by `Id` and belongs to one priority level.
Shorter forms default the label and optionally the priority.

Args:
    - Label: The optional [Label] attached to the optimization declaration.
    - Expression: The [Expression] whose value contributes to the objective.
    - Id: An identifier distinguishing this contribution from other contributions.
    - Priority: The priority level of the optimization criterion.
*%

%*! optimize_maximizeSum(Expression, Id, Priority)

Shorthand for [optimize_maximizeSum/4] using an anonymous label.

Args:
    - Expression: The [Expression] whose value contributes to the objective.
    - Id: An identifier distinguishing this contribution from other contributions.
    - Priority: The priority level of the optimization criterion.
*%

%*! optimize_maximizeSum(Expression, Id)

Shorthand for [optimize_maximizeSum/3] with priority `0`.

Args:
    - Expression: The [Expression] whose value contributes to the objective.
    - Id: An identifier distinguishing this contribution from other contributions.
*%

%*! optimize_precision(Precision, Priority)

Sets the integer precision used to lower floating-point optimization values at
one priority level.

Args:
    - Precision: A positive integer-valued [Expression] used as scaling factor.
    - Priority: The priority level for which the precision applies.
*%

%*! optimize_precision(Precision)

Sets the default precision for all priorities.

This can be overridden for specific priority levels through [optimize_precision/2].

Args:
    - Precision: A positive integer-valued [Expression] used as scaling factor.
*%