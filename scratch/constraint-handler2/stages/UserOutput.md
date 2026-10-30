## Information

`Solver.solve(on_model=callback)` returns Clingo's `SolveResult` and calls the
callback with live Clingo `Model` objects. Read model data inside the callback;
the objects are not retained snapshots. Return `False` to stop enumeration.

When optimization statements exist, callbacks receive only proven optima, never
improving incumbents. Use `SolveOptions(arguments=("0",))` to enumerate all
optimal models. Without optimization, callbacks receive ordinary stable models.

`solver.cost` is `None` until a model is found, then a tuple in descending
priority order, including guarded bases. Every declared priority has an entry,
even if all its statements are inactive. `solver.optimality_proven` reports the
latest model's proof flag. Metadata resets on each solve; an unsatisfiable solve
has cost `None` and no optimality proof. An interrupted solve can have an
incumbent cost without a proven optimum.

## ASP Format

## Python Datastructure

## TODO
