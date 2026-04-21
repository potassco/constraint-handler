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

%*! _se_ensure(Label, Expression)

Compile-engine-local representation of an [ensure/2] declaration.

Only `ensure` declarations whose effective engine is `compile` are translated
into this helper predicate. It acts as the entry point for seeding the checked
expression into [direct_query/1] and for later enforcing the integrity
constraint associated with the declaration.

Args:
    - Label: The [Label] of the `ensure` declaration.
    - Expression: The boolean [Expression] that must hold.
*%

%*! _se_assign(Label, Variable, Expression)

Compile-engine-local representation of an [assign/3] declaration.

This helper predicate stores the assignment relation only for declarations
handled by the `compile` engine. It is used both to seed [direct_query/1] for
the assigned variable and right-hand side expression, and to resolve variable
values recursively through [_se_value/2].

Args:
    - Label: The [Label] of the assignment declaration.
    - Variable: The variable [Expression] being assigned.
    - Expression: The assigned [Expression].
*%

%*! _se_evaluate(Label, Operator, Arguments)

Compile-engine-local representation of an [evaluate/3] declaration.

Only evaluation requests routed to the `compile` engine appear through this
predicate. It seeds the requested operator application into [direct_query/1]
and later supports the derivation of the public result predicate [evaluated/3].

Args:
    - Label: The [Label] of the evaluation request.
    - Operator: The [Operator] to evaluate.
    - Arguments: The argument list passed to the operator.
*%

%*! _direct_queryArgsValues(Expression, Operator, Arguments)

Exposes the operator and raw argument list of a queried operation.

This predicate is the bridge between [direct_query/1] and the `computeIdx`
interface. It normalizes an operation into the operator being applied and its
argument list, including the case where the operator position itself evaluates
to a function value such as a lambda.

Args:
    - Expression: The queried operation [Expression].
    - Operator: The resolved [Operator] of the operation.
    - Arguments: The operation's argument list.
*%

%*! _direct_compArg(Arguments, Index, Argument)

Enumerates one argument at a given position from an argument list.

This helper predicate is used to populate [_computeIdx/3] by pairing each
argument expression with its zero-based index in the operation's argument list.

Args:
    - Arguments: The argument list to enumerate.
    - Index: The zero-based position of the argument.
    - Argument: The [Expression] stored at that position.
*%

%*! _direct_needs_args_list(Expression, Arguments)

Marks a queried lambda application that requires a full evaluated argument
list.

Lambda application in the compile engine is implemented by first collecting all
argument values into a list and then performing beta reduction. This predicate
identifies the operations for which that additional preparation step is needed.

Args:
    - Expression: The queried operation [Expression].
    - Arguments: The raw argument list of the lambda application.
*%

%*! _length(Arguments, Length)

The length of a list of arguments.

Args:
    - Arguments: The list of arguments.
    - Length: The length of the list.
*%

%*! _direct_args_list_aux(Expression, Index, Arguments)

Auxiliary predicate for assembling the evaluated argument list of a lambda
application.

This helper walks through the lambda application's argument positions via
[_computeIdx/3] and constructs the list representation expected by the beta
reduction helper.

Args:
    - Expression: The lambda-application [Expression].
    - Index: The current zero-based argument position.
    - Arguments: The suffix of the evaluated argument list constructed from
      `Index` onward.
*%

%*! _direct_args_list(Expression, Arguments)

The evaluated argument list of a queried lambda application.

This predicate collects all argument values of a lambda application into a
single list term that can be passed to the beta reduction helper.

Args:
    - Expression: The lambda-application [Expression].
    - Arguments: The evaluated argument list.
*%

%*! _lambda_aux(Expression, ReducedExpression)

Performs beta reduction for a queried lambda application.

Once the argument values of a lambda application have been assembled,
this helper invokes the Python beta-reduction routine and produces the reduced
body expression. That reduced expression is then inserted back into
[direct_query/1] and evaluated through the ordinary compile-engine pipeline.

Args:
    - Expression: The original lambda-application [Expression].
    - ReducedExpression: The reduced [Expression] obtained after substituting
      the evaluated arguments into the lambda body.
*%

%*! _direct_implode(Value)

Marks a value that must be converted to its external representation for Python
evaluation.

Before the `python(...)` operator can be executed, its arguments must be
resolved into concrete values that the host-side evaluator understands. This
predicate identifies those values that participate in that implosion process.

Args:
    - Value: The [Expression] or value to prepare for Python evaluation.
*%

%*! _direct_imploded_args_aux(Expression, Index, Arguments)

Auxiliary predicate for assembling the imploded argument list of a Python
expression.

This helper traverses the argument positions of a queried `python(...)`
operation, resolves each argument through [_computeIdx/3], implodes it through
[_direct_imploded/2], and accumulates the resulting list in the representation
required by the Python bridge.

Args:
    - Expression: The queried `python(...)` [Expression].
    - Index: The current zero-based argument position.
    - Arguments: The suffix of the imploded argument list constructed from
      `Index` onward.
*%

%*! _expression_pythonEval(Expression, PythonExpression)

Builds the host-evaluable Python expression for a queried `python(...)`
operation.

This predicate combines the resolved operator with the imploded argument list
and produces the expression term that is passed to the external Python
evaluator.

Args:
    - Expression: The queried `python(...)` [Expression].
    - PythonExpression: The constructed [Expression] passed to the Python
      bridge.
*%

%*! _expression_eval_exec(Expression, Result)

The result returned by the external evaluator for a queried Python expression.

This helper invokes the Python bridge on the expression prepared by
[_expression_pythonEval/2]. The result is either a normal value term or an
error term, which is then translated into [_computedIdx/2] and [_warning/3]
facts.

Args:
    - Expression: The queried Python [Expression] being evaluated.
    - Result: The result returned by the Python bridge.
*%

%*! _direct_imploded(Value, ImplodedValue)

The external representation of a value prepared for Python evaluation.

This predicate records the result of the implosion process used by the
`python(...)` operator. It translates supported values, variable references,
and other compile-engine structures into the concrete representation expected
by the host-side Python evaluator.

Args:
    - Value: The original value or [Expression] to convert.
    - ImplodedValue: The converted external representation.
*%