# constraint-handler

A Python constraint-handling library. Requires Python 3.14 or newer and uv.

## Development

```sh
uv sync --locked
uv run pre-commit install
```

```sh
uv run nox -r -s tests
uv run pyright
uv run ruff check .
uv run ruff format .
uv run pre-commit run --all-files
uv build
```

Pre-commit runs linting, formatting, type checking, and tests. Tests report
branch coverage; there is no coverage threshold yet. CI runs tests only.

The distribution is named `constraint-handler`; import it as
`constraint_handler`. Runtime dependencies belong in `[project.dependencies]`,
development tools in `[dependency-groups].dev`. Commit `uv.lock` to keep
development reproducible.

## Complex Expression Evaluation

Integer comparisons normalize to
`linear_comparison("eq" | "neq" | "lt" | "leq" | "gt" | "geq", (coefficient, term), ..., offset)`.
Coefficients and the required offset are integer literals; terms are integer-only.
Flat comparisons remain native and test a gap-weighted order aggregate directly
against zero, deriving true or false only when every input is defined. They do
not enumerate numeric sum results. Real and mixed comparisons are not fused.

After splitting, flat `linear_integer` operations remain native. `encoding/integer.lp`
evaluates multi-term expressions with an indexed weighted `#sum`, guarded so
every input must have an integer value. One-term expressions use direct ASP
arithmetic to avoid unnecessary aggregate grounding. Flat conjunctions and
disjunctions also remain native in `encoding/boolean.lp`: any false
conjunct or true disjunct determines the result even if other operands are
undefined. The opposite result requires every operand to have the corresponding
Boolean value. Empty conjunctions are true; empty disjunctions are false.
Native implementations apply only to simple expressions left by normal
cost-based splitting; no operator forces splitting to become native. Other
operations and residual nesting become Python calls. For each complex call, ASP fact generation
enumerates the Cartesian product of its known input domains and evaluates the
callable for each row:

```asp
solution(ExprId, SolutionId).
input(SolutionId, variable("a"), integer(42)).
input(SolutionId, variable("b"), integer(1)).
output(SolutionId, integer(43)).
```

Solution IDs are unique across calls. Values use the same typed encoding as
`value/2`, including `real("2.5")`, `boolean(true)`, and `none`. The rules
in `encoding/complex.lp` derive a row's output only when all its inputs match.
Candidate calls that raise `ArithmeticError`, `LookupError`, `TypeError`, or
`ValueError` produce no row, leaving the expression undefined for those inputs.
Dependent expressions therefore remain undefined unless their existing semantics
can determine a result without that input. Python domain inference retains only
successful candidate results; it reports evaluation failures as warnings.
The solver loads `native.lp`, `boolean.lp`, `integer.lp`, `set.lp`, and `complex.lp` from
the bundled `encoding/` directory. Shared value, variable, and constraint rules
remain in `native.lp`.

Sets use `value(ExprId, set)` for definedness and `set_value(ExprId, Value)`
for each member. An empty set has the marker but no members; an undefined
expression has neither. Native rules handle constant sets, aliases, conditional
definitions, whole-set choices, and required or optional set-variable members.
Conflicting whole-set definitions are rejected rather than merged.

After ordinary cost-based splitting, flat `union`, `inter`, `diff`, `subset`,
`set_make`, `set_isin`, `set_notin`, and `cardinality` expressions remain native.
Equality, inequality, and `length` also remain native for exclusively set-valued
operands. The rules in `encoding/set.lp` work with individual members rather than
enumerating combinations of complete sets. Every operand must be defined, even
when an empty set would otherwise determine the result. Set construction removes
duplicate members, and construction without arguments produces an empty set.
Residual nesting still becomes a Python call; no set operator forces splitting.

Complex rows require the set marker and exact membership over the input domain:

```asp
input(SolutionId, variable("s"), set).
set_input_include(SolutionId, variable("s"), integer(1)).
set_input_exclude(SolutionId, variable("s"), integer(2)).
output(SolutionId, set).
set_output(SolutionId, integer(3)).
```

Included members must occur in `set_value/2`; excluded members must not occur.
Set outputs use the same marker/membership representation and can feed later
calls. Python callbacks may return `set` or `frozenset`; mutable results are
converted to immutable sets during domain inference and fact generation.

### Python Context

Register external functions or namespace objects before preprocessing:

```python
from constraint_handler import (
	ConstraintStore, Operation, Operator, PreprocessOptions, Preprocessor,
	Python, SolveOptions, VariableRef,
)

store = ConstraintStore()
store.define(
	VariableRef("result"),
	Operation(Operator.python_eval, (Python("lambda value: external_abs(value)"), -3)),
)
preprocessor = Preprocessor(PreprocessOptions())
preprocessor.add_context("external_abs", abs)
preprocessor.add(store)
problem, diagnostics = preprocessor.preprocess()
solver = problem.create_solver(SolveOptions())
result = solver.solve()
```

`Python("external_abs")` can also reference the callable directly. A registered
module or object is available through its bound name, such as
`Python("lambda value: helpers.transform(value)")`. Bindings are globals, so they
are visible inside lambdas and comprehensions; builtins and `math` remain available
unless explicitly overridden. Only use trusted Python source and context objects.

Each prepared problem snapshots the named bindings and uses them for domain
analysis, fact generation, and all solver sessions. Later `add_context` calls
affect only future preprocessing. This is a shallow snapshot: bound objects are
not copied and should remain unchanged. Runtime rebinding through
`Solver.add_context` is not supported because inferred domains depend on the
preparation-time bindings.

Python callbacks must be deterministic for fixed inputs and unchanged context
bindings. Compiled code is cached by source without retaining bound callbacks.
Validated Python input/output tables are retained with the domain metadata and
reused during fact generation and later solver construction. Table keys preserve
exact input representations, including Boolean, integer, and real distinctions.
Clingo symbols are still created independently for each library. Reusing tables
does not repeat callback side effects, and changing bound objects invalidates the
assumptions of the prepared problem.

Python callbacks can raise the public `constraint_handler.FailIntegrityExn` to
leave an input combination undefined. Domain inference and complex enumeration
skip that candidate without a warning; other candidates are still evaluated.
This does not reject the model, and dependent expressions follow their existing
undefined-input semantics.

The scratch converter treats legacy Python statements differently: its callback
wrapper catches `FailIntegrityExn` (including indirect calls), and supports
`solver_environment.constrain(condition)` and `constrain(condition)`. A failed
statement conditionally defines the ordinary variable `__fail` as true under
its SSA path condition. One global `check(not __fail)` rejects those models.
The converter reserves that name and never assigns it false. There is no special
failure variable, value, or rule in the core handler. Generated statement callbacks
use the scratch converter's execution helper, so that module must remain importable.

`ensure` requires a `boolean(true)` value to exist. `check` allows an absent
value, but any existing value must be `boolean(true)`.

Current limits:

- Nested sets remain unsupported. Complex calls enumerate known set input
	domains, including powersets of implicit set elements, so large sets can be
	expensive. Native set operations avoid these tables.
- Unknown input domains require the unimplemented propagator engine; solver
	creation raises `NotImplementedError` rather than omitting those calls.
- Known domains are fully enumerated, including interval approximations; large
	Cartesian products can be expensive. Splitting still uses specialized native
	cost estimates, which may underestimate the current Python-table cost.
- Native weighted sums avoid Python tables, but aggregate result grounding can
	still be large; this does not eliminate cryptarithm grounding limits.
- Unexpected Python exceptions and errors setting up a callable still propagate.
	Calls should be pure because domain analysis and repeated fact generation can
	execute them more than once.
- Unsupported Python return types and non-finite values raise errors. Integers
	must fit Clingo's signed 32-bit representation.
- Defaults remain unsupported by the native encoding.

The scratch legacy converter can audit the old set fixtures with bounded
workers and check both scalar values and set memberships:

```sh
python -m scratch.converter.audit_complex --section sets --output /tmp/constraint-handler-set-audit.json
```

Some legacy fixtures still require unsupported converter features, nested sets,
or diagnostic compatibility. Legacy mandatory scalar choices also differ from
the new optional choices; the audit reports these mismatches explicitly.
