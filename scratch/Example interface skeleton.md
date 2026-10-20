# Example Interface Skeleton

The public interface does not subclass `clingo.Control` or expose control
identity. Each stage owns its controls internally; preprocessing and solving
are explicit, separate operations.

`PreparedProblem` is a logically immutable, shareable artifact. It contains
normalized problem data, declared dynamic inputs, context requirements, and
diagnostics, but no live controls, solver-local literal IDs, or Python callables.
Its portable format is versioned and validated when loaded.

```python

class Preprocessor:
    def __init__(self, options: PreprocessOptions | None = None) -> None:
        self._control = clingo.Control(self._options.arguments)
        # This pre processor owns a preparation control.
        # No caller may depend on its existence or reuse it for solving.

    def add(self, program: str) -> None:
        # Collect textual input; do not implicitly ground or preprocess it.
        # A future Python-object input adapter feeds the same normalized IR.
        raise NotImplementedError

    def add_context(self, name: str, context: Context) -> None:
        # Bind preparation dependencies.
        raise NotImplementedError

    def preprocess(self) -> tuple [PreparedProblem, Diagnostics]:
        # Snapshot input and return detached, immutable data.
        # May normalize, ground, solve, or combine them internally.
        # Ambiguity/failure/interruption must not publish a partial artifact.
        raise NotImplementedError


class PreparedProblem:
    ...

    def dump(self, path: Path) -> None:
        # Serialize PreparedProblem
        raise NotImplementedError

    @classmethod
    def load(cls, path: Path) -> PreparedProblem:
        # Validate schema and compatibility; do not preprocess implicitly.
        raise NotImplementedError

    def create_solver(self, options: SolveOptions | None = None) -> Solver:
        # Each call creates an isolated mutable state.
        return Solver(self, options or SolveOptions())


class Solver:
    def __init__(self, problem: PreparedProblem, options: SolveOptions) -> None:
        self._control = clingo.Control(options.arguments)
        # Artifact data may be shared, but controls, contexts, propagators,
        # configuration, and callback state belong exclusively to this session.

    def add_context(self, name: str, context: Context) -> None:
        # Bind runtime dependencies and validate the declared interface/version.
        raise NotImplementedError

    def preset(self, values: Mapping[ch.Variable, ch.Value]) -> None:
        # Add preset
        raise NotImplementedError

    def enforce_query(self, query: Query) -> None:
        # Add constraint
        raise NotImplementedError

    def solve(self,  *) -> ch.SolveResult | ch.SolveHandle:
        # Maybe additional grounding.
        # Return SolveResult or SolveHandle with clingo-compatible iteration/wait/cancel/get behavior.
        # Model validity follows clingo: copy symbols before retaining results.
        raise NotImplementedError



def example() -> None:
    # Usage illustration only: the skeleton methods above are unimplemented.
    preprocessor = Preprocessor()
    preprocessor.load(Path("problem.lp"))
    prepared = preprocessor.preprocess()
    prepared.dump(Path("problem.ch-prepared"))

    restored = PreparedProblem.load(Path("problem.ch-prepared"))
    first = restored.create_solver(SolveOptions(arguments=("0",)))
    second = restored.create_solver(SolveOptions(arguments=("brave",)))
    # problem.lp must explicitly declare color as presettable with these values.
    color = ch.Variable("color")
    first.preset({color: ch.String("red")})
    second.preset({color: ch.String("blue")})

    def collect(model: ch.Model) -> None:
        print(tuple(model.symbols(shown=True)))

    # Independent results; neither session changes restored or the other one.
    first.solve(on_model=collect)
    second.solve(on_model=collect)
```
