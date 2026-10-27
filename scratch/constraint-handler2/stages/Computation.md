## Description

The initial solving pipeline transports the preprocessed constraint store into
Clingo. It does not implement native expression evaluation yet.

## Algorithms

1. `Preprocessor.preprocess()` snapshots the collected store, computes static
	types, normalizes, computes domains, and splits expressions as before.
2. If diagnostics contain no errors, dispatch the final store. No ASP facts are
	generated during preprocessing.
3. Return a `PreparedProblem` containing the detached store, type and domain
	metadata, and `engines: DispatchStore`. Its `asp_facts` property builds a
	`tuple[clingo.Symbol, ...]` on demand using `asp_facts(store, engines)`;
	facts are not an additional constructor input or stored state. See
	[EngineInput](EngineInput.md) and [SharedEngineInput](SharedEngineInput.md).
	A problem with preprocessing errors has empty engine assignments;
	`create_solver()` rejects it rather than solving an omitted program.
4. `PreparedProblem.create_solver(SolveOptions(...))` creates an isolated Clingo
	`Control`, forwarding `SolveOptions.arguments` to Clingo. Generate facts via
	`PreparedProblem.asp_facts` and add them and the packaged
	`constraint_handler/native.lp` encoding to `base`.
5. Ground `base` once when the solver session is created.
6. `Solver.solve()` calls Clingo's synchronous solve operation and returns its
	`clingo.SolveResult`. Repeated calls solve the same ground program. Separate
	sessions own separate controls and do not change the prepared problem.

The initial `native.lp` contains no rules (only a placeholder comment). Therefore
the base program has one stable model consisting of its facts, including when
an `ensure` refers to `boolean(false)`. Neither `check` nor `ensure` has solving
semantics yet. Complex and propagator engine facts are retained but likewise
have no executable semantics in this initial pipeline.

Context binding, presets, queries, prepared-problem persistence, model-to-variable
output, and native constraint rules remain unimplemented. This step establishes
the export, grounding, resource packaging, and solve boundaries for subsequent
native engine work.
