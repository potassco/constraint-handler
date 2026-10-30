## Information

The shared engine input is a ground ASP fact base exported from the preprocessed
`ConstraintStore`. Declarations refer to expressions by their existing store-local
IDs. Export does not evaluate expressions or rewrite IDs, conditions, or labels.
See [EngineInput](EngineInput.md) for expression terms and dispatch facts.

## ASP Format

```asp
variable_choose(var_name, expr_id, condition_id, label).
variable_define(var_name, expr_id, condition_id, label).
variable_default_to(var_name, expr_id, condition_id, priority, label).

check(expr_id, label).
ensure(expr_id, label).
minimize_statement(statement_id, expr_id, condition_id, priority).

set_contain_choose(var_name, expr_id, condition_id, label).
set_contain(var_name, expr_id, condition_id, label).
set_contain_default_to(var_name, expr_id, condition_id, priority, label).
```

These lines describe predicate signatures, not literal facts. `var_name` and
`label` are ASP strings. Expression and condition IDs are integers. Priorities
are signed integers, including negative values. The default label is retained
verbatim, just like an explicit label.

Each scalar variable choice, definition, or default produces the corresponding
`variable_*` fact. Each set-variable base candidate, assigned element, or default
produces the corresponding `set_contain*` fact. Each constraint produces exactly
one `check` or `ensure` fact according to `Constraint.is_check`.

Each optimization produces one `minimize_statement/4` fact. Its statement ID is
its zero-based position in `ConstraintStore.optimizations`, independent of its
expression ID. This identity prevents duplicate objective contributions from
collapsing under Clingo's weighted-tuple set semantics. Labels remain available
in the optimization records; they do not participate in objective tuple keys.

Values and conditions can be assigned to different engines. Their declaration
stays intact and refers to both IDs; it is not split or filtered by engine.
Every referenced ID has an `expr/2` fact and an `engine/2` fact.

Input records are visited in store order. Equal expressions with different IDs
remain distinct. Exact duplicate facts have ordinary ASP set semantics: they do
not create multiple ground atoms. Empty declaration lists produce no declaration
facts; any stored expressions are still exported.

## Python Datastructure

```python
def asp_facts(store: ConstraintStore, engines: DispatchStore) -> tuple[clingo.Symbol, ...]: ...
```

The function is exported from `constraint_handler`. It returns ground Clingo
symbols and does not mutate either input. The engine mapping must classify
exactly the expression IDs in the store, otherwise export raises `ValueError`.
Names, labels, scalar strings, and Python source use Clingo string symbols,
including Clingo's escaping for quotes, backslashes, and newlines.

Clingo integer literals are signed 32-bit integers. Export rejects out-of-range
integer values, IDs, and priorities with `ValueError` rather than silently
wrapping them. This is a limitation of the initial ASP backend, not a change to
the caller-facing expression model.

To render a text fact base, join `f"{fact}."` for each returned symbol with
newlines. No `#show` directives or semantic rules are generated.
