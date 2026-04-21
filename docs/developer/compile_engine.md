# Compile Engine

This page documents the internal `compile` engine, one of the supported execution and evaluation strategies in the constraint handler. It is the default engine for declarations that do not request a specific engine through [requestEngine/2] or [defaultEngine/1].

---

## How It Works

The `compile` engine resembles strategy that uses the default ASP behaviour in order to evaluate [Expressions] through a recursive pipeline. Its implementation is distributed across `main.lp`, `direct.lp`, and the operator-specific encoding files, but the control flow is regular: declarations are assigned to the engine, relevant expressions are marked for direct evaluation, values are derived recursively, and only then are public result predicates emitted.

!!! Info
    Because each sub-expression is evaluated independently, the `compile` engine is usually a good default for declarations whose sub-expressions do not have large cross-expression correlations.

### 1. Declaration Routing And Engine Assignment

The first step is to decide which declarations are handled by the `compile` engine at all.

[requestEngine/2] assigns an engine explicitly to a labeled declaration. [defaultEngine/1] provides the fallback for declarations without an explicit request. If no default is declared, the fallback is `compile`.

Once this resolution has happened, compile-specific helper predicates are populated only for declarations whose effective engine is `compile`. In particular:

- [_se_ensure/2] is derived from [ensure/2]
- [_se_assign/3] is derived from [assign/3]
- [_se_evaluate/3] is derived from [evaluate/3]

This routing step is important because the same high-level declaration form may have distinct implementations in other engines. The `compile` engine therefore does not inspect all declarations globally; it operates only on the subset that was explicitly or implicitly assigned to it.

### 2. Queries

After routing, the engine prepares all the sub-expressions that must actually be evaluated via [direct_query/1] by seeding them from the compile-specific entry predicates.

For example, [_se_assign/3] seeds both the assigned variable and the assigned expression into [direct_query/1]. [_se_evaluate/3] seeds the full requested operation into [direct_query/1].

### 3. Sub-Expression Values

Once an expression belongs to [direct_query/1], its value is derived through [_se_value/2]. This predicate is the semantic center of the compile engine.

At the base level, [_se_value/2] handles structural cases directly:

- literal values of the form `val(Type,Term)` evaluate to themselves
- references evaluate to themselves
- lambda expressions become function values

Variable lookup is also expressed through [_se_value/2]. If [direct_query/1] contains a variable expression, the engine searches for a compile-engine assignment through [_se_assign/3], recursively evaluates the assigned expression, and exposes the result as the value of that variable.

However, not all queries correspond to these base cases and have to be handled by invoking more helper predicates.

### 4. Computation of Operations

Operations that cannot be transformed into a [_se_value/2] directly, are prepared for operator-specific evaluation through [_direct_queryArgsValues/3]. This then directly ties into the `computeIdx` interface. This interface is a contract between the global strategy and the operator-specific semantics. It is implemented through three predicates:

- [_computeIdx/2] yields the operator being applied
- [_computeIdx/3] yields the value of each argument at a given position
- [_computedIdx/2] yields the final value of the full operation

The compile engine prepares the computation by filling [_computeIdx/2] and [_computeIdx/3] for the relevant operation and its arguments. The operator module then supplies rules for [_computedIdx/2] that derive the final value based on those inputs.

This separation of concerns allows the global strategy to remain agnostic about operator-specific semantics. The compile engine can evaluate any operation as long as it can query the operator and argument values through [_computeIdx/2] and [_computeIdx/3]. The details of how those values are derived are left to the operator modules.

### 5. Specialized Evaluation Paths

Two specialized paths are worth calling out because they explain why the compile engine is more than a simple bottom-up evaluator.

#### Lambda Application and Beta Reduction

If the operator position evaluates to a lambda value, the compile engine handles the application by first collecting the
list of arguments and then applying beta-reduction through a Python helper. The result is then fed back into the normal evaluation pipeline via [_computedIdx/2].

For this, several helper predicates are involved:
- [_direct_needs_args_list/2] identifies which expression requires the full list of arguments
- [_length/2] computes the length of the argument list using a Python helper.
- [_direct_args_list_aux/3] constructs the argument list by reversely traversing the arguments provided by [_computeIdx/3].
- [_direct_args_list/2] the final argument list.
- [_lambda_aux/2] performs the beta reduction by invoking the Python helper with the lambda body and the argument list.
