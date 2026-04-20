%*! _expression_query(Scope, Expression)

Collects expressions that participate in validation or evaluation.

This predicate is mainly used for type checking and checking for well-formedness. It gathers
expressions from variable definitions, domains, executions, optimization
declarations, etc.

Args:
    - Scope: The scope in which the expression occurs.
    - Expression: The [Expression] that should be inspected.
*%

%*! _expression_wellformed(Expression)

Signifies that an expression is structurally well formed.

Args:
    - Expression: The [Expression] determined to be well formed.
*%