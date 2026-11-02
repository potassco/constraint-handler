# Staged Python Interface

The experimental Python interface separates problem preparation from solving.
Import its public classes from `constraint_handler`:

- `Preprocessor` collects a program from text, files, or Python atoms.
- `PreparedProblem` holds an immutable snapshot of the prepared program.
- `Solver` creates an independent solving session for a prepared problem.
- `SolveOptions` configures model limits and variable visibility.
- `Model` contains a solution's values, diagnostics, and optimization data.

## Quick Start

```python
from constraint_handler import PreparedProblem, Preprocessor, Solver

preprocessor = Preprocessor()
preprocessor.add('variable_define("x",val(int,5)).')

prepared, diagnostics = PreparedProblem.from_preprocessor(preprocessor)
solver = Solver(prepared)
solution = solver.solve()

if solution is not None:
    print(dict(solution.values))
```

Output:

```text
{'x': 5}
```

## Program Input

Use the following methods to build a program. Calls can be combined on the
same preprocessor.

| Method | Input |
| --- | --- |
| `add(program: str)` | CH source text. |
| `join(atoms: Iterable[Atom])` | Python atoms from `constraint_handler.schemas.atom`, supplied as a list, tuple, or generator. |
| `load(path: Path)` | Source text read from a UTF-8 file. |

Each call snapshots its input for subsequent preparation. For example,
`join()` captures the contents of a caller-owned list, and `load()` captures
the file's contents at the time of the call.

### Python Atoms

Construct declarations using the existing schema types:

```python
from constraint_handler import Preprocessor
from constraint_handler.schemas.atom import Variable_define
from constraint_handler.schemas.expression import Val, Variable
from constraint_handler.schemas.type_ import BaseType

preprocessor = Preprocessor()
preprocessor.join([
    Variable_define("x", Val(BaseType.int, 5)),
    Variable_define("y", Variable("x")),
    Variable_define("rate", Val(BaseType.float, 3.25)),
])
```

`Val` represents a typed constant, and `Variable` represents a reference to a
variable in an expression. Domain declarations use domain instances such as
`FromFacts()` from `constraint_handler.schemas.domain`.

## Preparation

`PreparedProblem.from_preprocessor(preprocessor)` returns
`(prepared, diagnostics)`. The prepared problem contains normalized CH
declarations and diagnostics. Diagnostics are a tuple of Clingo symbols.

Preparation snapshots the preprocessor's accumulated inputs. The preprocessor
remains available for repeated preparation and further additions. Earlier
prepared problems retain their original contents.

Preparation requires exactly one uninterrupted preparation model. An
unsatisfiable, ambiguous, or interrupted preparation raises `ValueError`.

## Solving

Create a session with `Solver(prepared, options=None)`. Several sessions can
share the same prepared problem; each session manages its own solving state
and visibility overrides.

| Operation | Result |
| --- | --- |
| `solve()` | One solution `Model`, or `None` for UNSAT. |
| `enumerate()` | An iterator of solution models, subject to the model limit; empty for UNSAT. |

Repeated calls start fresh solving operations using the session's options
and visibility settings.

### Solve Options

`SolveOptions` takes keyword arguments:

| Option | Default | Meaning |
| --- | --- | --- |
| `model_limit` | `None` | Maximum number of models per operation. `None` selects unlimited enumeration. |
| `show_by_default` | `True` | Visibility of variables with no session override. |

With optimization, `enumerate()` yields the models produced during the
optimization search. `solve()` returns the last model found within the model
limit.

### Visibility

Use `show(variable)` and `hide(variable)` to override visibility for a
session. Both methods take a `Variable` expression:

```python
from constraint_handler import Solver
from constraint_handler.schemas.expression import Variable

first = Solver(prepared)
second = Solver(prepared)
first.hide(Variable("x"))
second.show(Variable("x"))
```

Each session keeps its own overrides. With
`SolveOptions(show_by_default=False)`, `show()` selects the variables to
include in returned models.

## Models

| Attribute | Meaning |
| --- | --- |
| `values` | A read-only mapping from variable names to native Python scalar values. |
| `diagnostics` | Preparation diagnostics followed by diagnostics from the solution. |
| `optimization_value` | The model's raw Clingo cost tuple. |
| `optimality_proven` | A boolean on models yielded by `enumerate()`, indicating whether optimality is proven. |

The keys in `values` are variable names directly: a string-named variable
`"x"` has the Python key `"x"`, and an ASP identifier `x` has the key
`clingo.Function("x")`.

Scalar values become Python `int`, `float`, `str`, `bool`, or `None`. Symbol
values remain Clingo symbols. Set and multimap conversion currently raises
`NotImplementedError`.

## API Design Targets

The following entry points are API stubs that raise `NotImplementedError`.
Their intended contracts are:

| Entry Point | Intended Contract |
| --- | --- |
| `Preprocessor(options=PreprocessOptions())` | Configure preparation. |
| `Preprocessor.add_context(name, context)` | Bind named preparation dependencies. |
| `PreparedProblem.dump(path)` | Write a versioned, portable prepared artifact. |
| `PreparedProblem.load(path)` | Validate and restore a portable artifact. |
| `Solver.add_context(name, context)` | Bind runtime dependencies and validate their declared interfaces and versions. |
| `Solver.preset(values)` | Add session-local assignments for declared presettable variables. |
| `Solver.enforce_query(query)` | Add a session-local enforced query. |
| `Solver.union()` | Return one aggregate model mapping each variable to a set of values. |
| `Solver.intersection()` | Return bindings present in every solution model. |
| `Solver.supremum()` | Return one supremum aggregate model. |
| `Solver.infimum()` | Return one infimum aggregate model. |

`PreprocessOptions`, `Context`, and `Query` are placeholder types for these
contracts. Portable artifacts are intended to carry normalized data,
diagnostics, declared dynamic inputs, and context requirements.

Under the target contract, solving and aggregation use the session's presets
and enforced queries. Aggregate operations return `None` for UNSAT, and their
models carry values and diagnostics. `optimization_value` belongs to models
returned by `solve()` and `enumerate()`; `optimality_proven` belongs to models
yielded by `enumerate()`.
