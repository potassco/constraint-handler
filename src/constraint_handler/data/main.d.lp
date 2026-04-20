#include "bool.d.lp".
#include "conditionals.d.lp".
#include "equality.d.lp".
#include "direct.d.lp".
#include "execution.d.lp".
#include "expression.d.lp".
#include "float.d.lp".
#include "int.d.lp".
#include "multimap.d.lp".
#include "optimize.d.lp".
#include "preference.d.lp".
#include "set.d.lp".
#include "type.d.lp".
#include "variable.d.lp".

%*! requestEngine(Label, Engine)

Requests a specific engine for one labeled declaration.

If no engine is requested for a label, the declaration falls back to the value
of [defaultEngine/1], or to `compile` if no default has been set.

Args:
    - Label: The [Label] identifying the declaration to which the request applies.
    - Engine: The engine to use, currently one of `compile`, `ground`, or `propagator`.
*%

%*! defaultEngine(Engine)

Sets the engine used for declarations that do not have an explicit
`requestEngine/2` fact.

If this predicate is omitted, the default engine is `compile`.

Args:
    - Engine: The default engine used for unlabeled or unrequested declarations.
*%

%*! value(Name, Value)

The final value assigned to a variable.

This is the main result predicate for variables and also for collection
references such as sets or multimaps. The second argument is normally a
`val(Type,Term)` expression or a collection reference.

Args:
    - Name: The name of the variable whose value is reported.
    - Value: The computed value of the variable.
*%

%*! warning_forbid(Kind)

Escalates one warning kind to a hard failure.

If a warning of this kind is produced and it is not ignored, the current model
is rejected in the same spirit as an integrity constraint violation.

Args:
    - Kind: The warning kind that should be treated as forbidden.
*%

%*! warning_ignore(Kind)

Suppresses one warning kind from the public result.

Ignored warnings are not shown through [warning/3] and also take precedence
over `warning_forbid/1` when both are declared for the same kind.

Args:
    - Kind: The warning kind that should be ignored.
*%

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

The computed value of a sub-expression.

This is the central value relation used throughout the compile engine. It maps
a Sub-[Expression] to its current value after recursive evaluation.
Result predicates such as [value/2], [set_value/2], or [multimap_value/3] are
ultimately derived from `_se_value/2`.

Args:
    - SubExpression: The [Expression] for which the value is being computed.
    - Value: The [Expression] assigned as the value of `SubExpression`.
*%

%%%%%%%%%%%%%%%%%%%%%%%%%%
% warning
%%%%%%%%%%%%%%%%%%%%%%%%%%

%*! warning(Kind,Information,Message)

A warning emitted during grounding or solving.

If a warning kind is forbidden using `warning_forbid/1`, the warning
behaves like a failed integrity constraint.

Args:
    - Kind: The kind of warning being emitted.
    - Information: Usually a list of labels or identifiers related to the warning.
    - Message: Additional details that help explain the issue.
*%
