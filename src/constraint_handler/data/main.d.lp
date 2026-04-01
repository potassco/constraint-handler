#include "conditionals.d.lp".
#include "equality.d.lp".
#include "direct.d.lp".
#include "float.d.lp".
#include "int.d.lp".
#include "type.d.lp".

%%%%%%%%%%%%%%%%%%%%%%%%%%
% Compute
%%%%%%%%%%%%%%%%%%%%%%%%%%

%*! _computeIdx(Expression,Operator)

Initiate the computation of an operation.

Args:
    - Expression: The [Expression] representing the operation to be computed.
    - Operator: The [Operator] used in the expression.
*%

%*! _computeIdx(Expression,Index,Argument)

The argument at a specific index of an operation.

Args:
    - Expression: The [Expression] representing the operation to be computed.
    - Index: The index of the argument in the computation (starting from 0).
    - Argument: The [Expression] assigned as the argument at the specified index.
*%

%*! _computedIdx(Expression,Result)

The result of the computation of an operation.

Args:
    - Expression: The [Expression] representing the operation that was computed.
    - Result: The [Expression] assigned as the result of the computation.
*%

%%%%%%%%%%%%%%%%%%%%%%%%%%
% _se_value
%%%%%%%%%%%%%%%%%%%%%%%%%%

%*! _se_value(SubExpression,Value)

The value of a sub-expression.

Args:
    - SubExpression: The [Expression] for which the value is being computed.
    - Value: The [Expression] assigned as the value of `SubExpression`.
*%

%%%%%%%%%%%%%%%%%%%%%%%%%%
% warning
%%%%%%%%%%%%%%%%%%%%%%%%%%

%*! warning(Kind,Information,Message)

A warning emitted during the computation.

Args:
    - Kind: The kind of warning being emitted.
    - Information: Additional information about the warning.
    - Message: A message describing the warning.
*%