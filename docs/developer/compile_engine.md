# Compile Engine

This page documents the internal `compile` engine, one of the supported execution and evaluation strategies in the constraint handler. It is the default engine for declarations that do not request a specific engine through [requestEngine/2] or [defaultEngine/1].

---

## How It Works

The `compile` engine resembles strategy that uses the default ASP behaviour in order to evaluate [Expressions] through a recursive pipeline. Its implementation is distributed across `main.lp`, `direct.lp`, and the operator-specific encoding files, but the control flow is regular: declarations are assigned to the engine, relevant expressions are marked for direct evaluation, values are derived recursively, and only then are public result predicates emitted.

!!! Info
    Because each sub-expression is evaluated independently, the `compile` engine is usually a good default for declarations whose sub-expressions do not have large cross-expression correlations.

### Declaration Routing And Engine Assignment

The first step is to decide which declarations are handled by the `compile` engine at all.

[requestEngine/2] assigns an engine explicitly to a labeled declaration. [defaultEngine/1] provides the fallback for declarations without an explicit request. If no default is declared, the fallback is `compile`.

Once this resolution has happened, compile-specific helper predicates are populated only for declarations whose effective engine is `compile`. In particular:

- [_se_ensure/2] is derived from [ensure/2]
- [_se_assign/3] is derived from [assign/3]
- [_se_evaluate/3] is derived from [evaluate/3]

This routing step is important because the same high-level declaration form may have distinct implementations in other engines. The `compile` engine therefore does not inspect all declarations globally; it operates only on the subset that was explicitly or implicitly assigned to it.

### Queries

After routing, the engine prepares all the sub-expressions that must actually be evaluated via [direct_query/1] by seeding them from the compile-specific entry predicates.

For example, [_se_assign/3] seeds both the assigned variable and the assigned expression into [direct_query/1]. [_se_evaluate/3] seeds the full requested operation into [direct_query/1].

#### Lazy

The default [direct_query/1] rule for operations is eager. If an operation is queried directly, all of its arguments are queried as well. This is the right behavior for arithmetic and most structural operators, because the value of the operation depends on all argument values.

Some operators, however, require control over the order in which their arguments are explored. Those operators are registered through [_direct_lazy/1]. The canonical example is `ite`.

For `ite`, the engine does not query both branches eagerly. Instead it follows a staged rule set defined in the respective operator module `conditionals.lp`:

1. Query the condition.
2. If the condition becomes `val(bool,true)`, query only the then-branch.
3. If the condition becomes `val(bool,false)`, query only the else-branch.

This matters because it gives `ite` proper short-circuit behavior and prevents unnecessary evaluation work.

### Sub-Expression Values

Once an expression belongs to [direct_query/1], its value is derived through [_se_value/2]. This predicate is the semantic center of the compile engine.

At the base level, [_se_value/2] handles structural cases directly:

- literal values of the form `val(Type,Term)` evaluate to themselves
- references evaluate to themselves
- lambda expressions become function values

Variable lookup is also expressed through [_se_value/2]. If [direct_query/1] contains a variable expression, the engine searches for a compile-engine assignment through [_se_assign/3], recursively evaluates the assigned expression, and exposes the result as the value of that variable.

However, not all queries correspond to these base cases and have to be handled by invoking more helper predicates.

### Computation of Operations

Operations that cannot be transformed into a [_se_value/2] directly, are prepared for operator-specific evaluation through [_direct_queryArgsValues/3]. This then directly ties into the `computeIdx` interface. This interface is a contract between the global strategy and the operator-specific semantics. It is implemented through three predicates:

- [_computeIdx/2] yields the operator being applied
- [_computeIdx/3] yields the value of each argument at a given position
- [_computedIdx/2] yields the final value of the full operation

The compile engine prepares the computation by filling [_computeIdx/2] and [_computeIdx/3] for the relevant operation and its arguments. The operator module then supplies rules for [_computedIdx/2] that derive the final value based on those inputs.

This separation of concerns allows the global strategy to remain agnostic about operator-specific semantics. The compile engine can evaluate any operation as long as it can query the operator and argument values through [_computeIdx/2] and [_computeIdx/3]. The details of how those values are derived are left to the operator modules.

### Specialized Evaluation Paths

Two specialized paths are worth calling out because they explain why the compile engine is more than a simple bottom-up evaluator.

#### Lambda Application

If the operator position evaluates to a lambda value, the compile engine handles the application by first collecting the
list of arguments and then applying beta-reduction through a Python helper. The result is then fed back into the normal evaluation pipeline via [_computedIdx/2].

For this, several helper predicates are involved:

- [_direct_needs_args_list/2] identifies which expression requires the full list of arguments
- [_length/2] computes the length of the argument list using a Python helper.
- [_direct_args_list_aux/3] constructs the argument list by reversely traversing the arguments provided by [_computeIdx/3].
- [_direct_args_list/2] the final argument list.
- [_lambda_aux/2] performs the beta reduction by invoking the Python helper with the lambda body and the argument list.

#### Python Expressions

When the `compile` engine encounters a `python(STR)` operator, it offloads the evaluation to the host environment. This is used for operations that are either too complex for pure ASP or require external libraries. The process involves a full transformation of the argument space before invoking the Python interpreter. After the Python evaluation, the result is fed back into the normal evaluation pipeline.

- [_expression_pythonEval/2] forms the bridge between the ASP operation and the external evaluator.
- [_expression_eval_exec/2] contains the result of the Python evaluation.

Because Python operates on concrete values rather than ASP symbolic terms, the engine must "implode" arguments. This process recursively resolves references and variables into their actual values, ensuring that the Python code receives the correct data structure for evaluation.

- [_direct_implode/1] identifies values that need to be prepared for Python integration.
- [_direct_imploded/2] is the result of the implosion process.
- [_direct_imploded_args_aux/3] just like in the lambda application, this collects the arguments into a list using [_computeIdx/3], but this time the result is the imploded version of the arguments.

### Error Propagation and Recovery

The `compile` engine uses a strict error propagation model to handle partial functions or evaluation failures. The symbol `bad` is used to represent an invalid state (e.g., division by zero or a failed Python execution).

By default, an operation is `bad` if any of its arguments are `bad`. This is checked by expanding the argument list via `@pythonListElements`. This `bad` is then propagated through the expression graph until it reaches the top-level declarations. However, this rule would be too coarse for several operators. For example, some boolean or conditional operators can still determine a unique result even when one argument is `bad`.

Such operators are declared as "recoverable" through [_operator_recoverable/1]. This suppresses the automatic evaluation to `bad` when an argument is `bad`. Instead the respective operator module can then define more precise behavior through [_computedIdx/2].

This is how operators such as `limp`, `conj`, and `pow` retain informative semantics in cases where the default behaviour would collapse the entire expression to `bad`.

!!! Example
    Suppose you have:

    ```prolog
    variable_define(really_bad,bad).
    evaluate(conj, (val(bool,false), (variable(really_bad),()))).
    ```

    Even though one argument is `bad`, the result in `evaluated/3` will be `val(bool,false)` (not `bad`), because once an argument of a conjunction is `val(bool,false)`, the entire conjunction is `val(bool,false)` regardless of the other argument.

Evaluation failures are never silent. When a `bad` value is encountered, the engine emits a [Warning] via [_warning/3], capturing the specific expression context and error kind to ensure traceability.

### Result Projection

The last stage is projection from internal facts to public result predicates.

[value/2] is derived from variable values already established through [_se_value/2]. [evaluated/3] is derived from [_se_evaluate/3] together with the value of the requested operation. Collection and preference outputs follow the same pattern: internal helper predicates build the structure, and then public result predicates expose only the externally relevant view.

Warnings behave similarly. Operator modules and helper layers emit [_warning/3]. That internal warning stream is then filtered by [warning_ignore/1], [warning_ignore/2], [warning_forbid/1], and [warning_forbid/2] before becoming visible through [warning/3] or, in the forbidden case, rejecting the model.

## Worked Example

The following example is intentionally small, but it illustrates the fundamental control flow of the `compile` engine and how the different components interact.

```prolog
variable_define(one,val(int,1)).
variable_define(bad_div,
    operation(
        int_div, 
        (variable(one),
        (val(int,0),
    ())))
).

evaluate(ite, 
    (val(bool,false), 
    (variable(bad_div),
    (variable(one),
())))
).
```

### Step 1. Declaration Routing

Because the example does not specify an engine, the default is `compile`. The `variable` module turns all `variable_define/2` declarations into [assign/3] declarations with the same variable and expression. Furthermore, because we did not specify any labels, the declarations will be assigned the default anonymous label `_label_anonymous`.

This provides the necessary entry points for our example. As stated in the previous [Section](#declaration-routing-and-engine-assignment), declarations meeting these criteria will be transformed into compile-specific entry predicates.

More specifically, all `variable_define/2` declarations are transformed into [_se_assign/3] facts, and the `evaluate/2` declaration is transformed into a [_se_evaluate/3] fact.

### Step 2. Queries

The compile engine then derives [direct_query/1] facts for the relevant sub-expressions. In this case, all [_se_assign/3] facts seed both the variable and the assigned expression into [direct_query/1]. The [_se_evaluate/3] fact seeds the full requested operation into [direct_query/1].

After that, the engine applies the [direct_query/1] expansion rules to derive the full evaluation graph. Because the operation corresponding to `bad_div` is `int_div`, which is not declared as lazy, the engine eagerly queries both arguments of that operation. The first argument was already queried as part of the variable assignment, resulting in no additional queries. The second argument is a new value and is therefore added to [direct_query/1].

However, the same is not true for the `ite` operation. Because `ite` is declared as lazy, the engine does not query both branches immediately. Instead, it first queries the condition, which is `val(bool,false)`, and waits for the result before deciding which branch to query next.

### Step 3. Initial Evaluation

The engine then derives values for the queried expressions through [_se_value/2]. For all base cases, the value is derived directly. Namely, `val/2` evaluates to itself and `variable/1` that contain a direct value also evaluate to that value.

At this point we know:

- `val(int,1)`, `val(int,0)` and `val(bool,false)` evaluate to themselves
- `variable(one)` evaluates to `val(int,1)`

However, we do not know about:

- `variable(bad_div)` yet, because it depends on the value of the `int_div` operation, which has not been evaluated yet.
- the `ite` operation, because its value depends on the value of the selected branch, which has not been queried yet.

### Step 4. Computation of Operations
Then, the engine prepares the `int_div` operation for operator-specific evaluation by filling [_computeIdx/2] and [_computeIdx/3] using [_direct_queryArgsValues/3] and [_direct_compArg/3]. Because all values for the operation are already known, we can proceed to the implementation in the operator module `int.lp`.

The `int` module then applies the semantics of integer division through rules for [_computedIdx/2]. Among these rules, one explicitly derives `bad` for any division by zero. This rule triggers, since we already know that the second argument evaluates to `val(int,0)`, and creates a [computedIdx/2] fact that `int_div` with those arguments is `bad`.

This then propagates through and yields that the value of the operation is bad, which in turn propagates to the value of `variable(bad_div)` being `bad`. The `variable` module then picks up on this and derives a [_warning/3] of type `badValue` for `variable(bad_div)`.

Additionally, we can also find a rule in the `int` module that derives a [_warning/3] of type `expression(zeroDivisionError)` for any division by zero.

### Step 5. Lazy Evaluation and Recovery
Meanwhile, the `ite` operation is evaluated based on the rules in the `conditionals` module. In contrast to the `int_div` evaluation, the `ite` evaluation does not use `computeIdx`. Instead, it provides special rules that produce `direct_query/1` facts for the respective branch based on the condition value. 

We already know that the if-branch would yield `bad` because it contains `variable(bad_div)`, which we just established is `bad` due to the division by zero.

However, that's exactly where the strength of lazy queries comes in. Because the condition is `val(bool,false)`, the engine produces a [direct_query/1] fact for the else-branch, which is `variable(one)`, but doesn't even consider the if-branch at all. This allows the engine to derive the value of the `ite` operation as `val(int,1)`, even though one of its branches contains a `bad` value.

We effectively recovered from the division by zero error, because it wasn't relevant for the final result!

### Step 6. Result Projection

Now that the engine knows all relevant values, it can derive the public result predicates. In particular, we will have:
- `value(one,val(int,1))` from the variable definition with a fixed value
- `value(bad_div,bad)` from the variable definition with an operation that evaluates to `bad`
- `evaluated(ite,(val(bool,false),(variable(bad_div),(variable(one),()))),val(int,1))` from the evaluation of the `ite` operation.

Additionally, we will have the warnings for the `bad` evaluations:
- `warning(expression(zeroDivisionError),(),(int_div,operation(int_div,(variable(one),(val(int,0),())))))`
- `warning(expression(badValue),(),(variable(bad_div)))`

## Practical Reading Guide

For implementation work, the most useful reading order is usually the following.

1. `main.lp`, to understand engine assignment, defaults, public [value/2], and warning projection.
2. `direct.lp`, to understand compile-specific entry predicates, [direct_query/1], [_se_value/2], lambda handling, Python evaluation, and generic `bad` propagation.
3. Operator modules such as `bool.lp`, `conditionals.lp`, `int.lp`, `set.lp`, and `multimap.lp`, to understand how [_computedIdx/2] and specialized [direct_query/1] rules realize individual semantics.
4. The declaration-specific files that seed expressions into the compile engine, such as the variable, execution, optimization, and preference encodings.