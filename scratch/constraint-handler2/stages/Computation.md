## Description

The solving pipeline transports the preprocessed constraint store into Clingo,
evaluates native expressions and complex Python rows, and optimizes guarded
integer objectives when present.

## Algorithms

1. `Preprocessor.preprocess()` snapshots the collected store, computes static
	types, normalizes, computes domains, and splits expressions as before.
2. If diagnostics contain no errors, dispatch the final store. Diagnose
	optimization roots with unknown domains or non-native engines. No ASP facts
	are generated during preprocessing. `continue_on_errors=True` retains errors
	but allows the normal preparation passes to continue.
3. Return a `PreparedProblem` containing the detached store, type and domain
	metadata, and `engines: DispatchStore`. Its `asp_facts` property builds a
	`tuple[clingo.Symbol, ...]` on demand using `asp_facts(store, engines)`;
	facts are not an additional constructor input or stored state. See
	[EngineInput](EngineInput.md) and [SharedEngineInput](SharedEngineInput.md).
	A problem blocked before dispatch has empty engine assignments;
	`create_solver()` rejects incomplete dispatch rather than solving an omitted
	program. Unsupported objectives are also rejected during fact generation.
4. `PreparedProblem.create_solver(SolveOptions(...))` creates an isolated Clingo
	`Control`, forwarding `SolveOptions.arguments` to Clingo. Generate facts via
	`PreparedProblem.asp_facts` and add them and the packaged
	bundled `encoding/` rules to `base`, including `native.lp`, `none.lp`,
	`boolean.lp`, `integer.lp`, `eq.lp`, `set.lp`, `tuples.lp`, `complex.lp`, and
	`optimize.lp`. Propagator solving remains unsupported.
5. Ground `base` once when the solver session is created.
6. `Solver.solve(on_model=None)` calls Clingo's synchronous solve operation and
	returns its `clingo.SolveResult`. Repeated calls solve the same ground program.
	Separate sessions own separate controls and do not change the prepared problem.

When objectives are present, set Clingo's optimization mode to `optN`, overriding
any conflicting mode in the forwarded arguments. Only models whose
`optimality_proven` flag is true reach the user callback; improving incumbents
are internal. `SolveOptions(arguments=("0",))` enumerates all optima. Without
objectives, callbacks receive ordinary models and other solver options remain
unchanged. A callback can return `False` to stop enumeration.

`Solver.cost` is `None` before a model is found and otherwise a tuple of costs
ordered by descending declared priority. It includes guarded base contributions;
inactive statements contribute zero, and all declared priorities are retained.
`Solver.optimality_proven` records the latest model's proof flag. Both properties
reset at the start of each solve; unsatisfiable solves retain `None` and `False`.
Interrupted searches may expose an incumbent cost without a proof, but never
deliver that incumbent through the optimal-model callback.

Presets, queries, prepared-problem persistence, runtime context rebinding, and
model-to-variable output remain unimplemented. Preparation-time Python context
bindings are supported.
