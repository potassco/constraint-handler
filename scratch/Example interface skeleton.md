# Example Interface Skeleton

The public interface does not subclass `clingo.Control` or expose control
identity. Each stage owns its controls internally; preprocessing and solving
are explicit, separate operations.

`PreparedProblem` is a logically immutable, shareable artifact. It contains
normalized problem data, declared dynamic inputs, context requirements, and
diagnostics, but no live controls, solver-local literal IDs, or Python
callables. Its portable format is versioned and validated when loaded.

Public construction belongs to the target class. Preparation snapshots the
preprocessor's current inputs and bindings without consuming or clearing it;
later additions do not affect previously prepared artifacts.

`solve()` returns one solution model, while `enumerate()` returns an iterator
of solution models subject to the model limit. `union()`, `intersection()`,
`supremum()`, and `infimum()` each return one aggregate model. For UNSAT,
`enumerate()` yields no models and the other methods return `None`. All
operations use the session's presets and enforced queries. Each model contains
`values` and diagnostics. In a union model, each variable maps to a set of
values; in other models, each variable maps to a single value. An intersection
model contains a binding if and only if it is present in every solution model.
`optimization_value` is defined only on models returned by `solve()` and
`enumerate()`. `optimality_proven` is defined only on models yielded by
`enumerate()` and states whether the solution is proven optimal.

```python

class Preprocessor:
    def __init__(self, options: PreprocessOptions | None = None) -> None:
        # This pre processor owns a preparation control.
        # No caller may depend on its existence or reuse it for solving.
        raise NotImplementedError

    def add(self, program: str) -> None:
        # Collect textual input; do not implicitly ground or preprocess it.
        # A future Python-object input adapter feeds the same normalized IR.
        raise NotImplementedError

    def load(self, path: Path) -> None:
        """Add problem source from a file to the preprocessor's inputs."""
        raise NotImplementedError

    def add_context(self, name: str, context: Context) -> None:
        # Bind preparation dependencies.
        raise NotImplementedError


class PreparedProblem:
    @classmethod
    def from_preprocessor(cls, preprocessor: Preprocessor) -> tuple[PreparedProblem, Diagnostics]:
        # Snapshot input and return detached, immutable data.
        # May normalize, ground, solve, or combine them internally.
        # Ambiguity/failure/interruption must not publish a partial artifact.
        raise NotImplementedError

    def dump(self, path: Path) -> None:
        # Serialize PreparedProblem
        raise NotImplementedError

    @classmethod
    def load(cls, path: Path) -> PreparedProblem:
        # Validate schema and compatibility; do not preprocess implicitly.
        raise NotImplementedError

class Model:
    values: Mapping[ch.Variable, ch.Value | set[ch.Value]]
    diagnostics: Diagnostics
    optimization_value: OptimizationValue
    optimality_proven: bool


class SolveOptions:
    def __init__(
        self,
        *,
        model_limit: int | None = None,
        show_by_default: bool = True,
    ) -> None:
        """Select the model limit and default variable visibility.

        None means no model limit. show_by_default determines visibility for
        variables without a Solver.show() or Solver.hide() override.
        """
        raise NotImplementedError


class Solver:
    def __init__(self, problem: PreparedProblem, options: SolveOptions | None = None) -> None:
        # Artifact data may be shared, but controls, contexts, propagators,
        # configuration, and callback state belong exclusively to this session.
        raise NotImplementedError

    def add_context(self, name: str, context: Context) -> None:
        # Bind runtime dependencies and validate the declared interface/version.
        raise NotImplementedError

    def preset(self, values: Mapping[ch.Variable, ch.Value]) -> None:
        # Add preset
        raise NotImplementedError

    def enforce_query(self, query: Query) -> None:
        # Add constraint
        raise NotImplementedError

    def show(self, variable: ch.Variable) -> None:
        """Override visibility to show a variable in this session's returned models."""
        raise NotImplementedError

    def hide(self, variable: ch.Variable) -> None:
        """Override visibility to hide a variable in this session's returned models."""
        raise NotImplementedError

    def solve(self) -> Model | None:
        """Return one solution model, or None for UNSAT."""
        raise NotImplementedError

    def enumerate(self) -> Iterator[Model]:
        """Yield solution models subject to the model limit; yield none for UNSAT."""
        raise NotImplementedError

    def union(self) -> Model | None:
        """Return the union model, or None for UNSAT."""
        raise NotImplementedError

    def intersection(self) -> Model | None:
        """Return the intersection model, or None for UNSAT."""
        raise NotImplementedError

    def supremum(self) -> Model | None:
        """Return the supremum model, or None for UNSAT."""
        raise NotImplementedError

    def infimum(self) -> Model | None:
        """Return the infimum model, or None for UNSAT."""
        raise NotImplementedError



def example() -> None:
    # Usage illustration only: the skeleton methods above are unimplemented.
    preprocessor = Preprocessor()
    preprocessor.load(Path("problem.lp"))
    prepared, diagnostics = PreparedProblem.from_preprocessor(preprocessor)
    prepared.dump(Path("problem.ch-prepared"))

    restored = PreparedProblem.load(Path("problem.ch-prepared"))
    first = Solver(restored, SolveOptions(model_limit=None))
    second = Solver(restored)
    # problem.lp must explicitly declare color as presettable with these values.
    color = ch.Variable("color")
    first.preset({color: ch.String("red")})
    second.preset({color: ch.String("blue")})

    # Independent results; neither session changes restored or the other one.
    for model in first.enumerate():
        print(model.values)
    second_solution = second.union()
    if second_solution is not None:
        print(second_solution.values)
```
