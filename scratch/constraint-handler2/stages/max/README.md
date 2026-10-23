# constraint-handler

A Python constraint-handling library. Requires Python 3.15 or newer and uv.

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

## Domain Contracts

`constraint_handler.domains.domain_from_values` constructs an exact explicit
domain from enumerated values. It does not widen at a threshold, fill integer
gaps, or merge powerset universes. If compound Boolean/numeric values would
collide in Python collections, it conservatively returns an unknown domain.

`constraint_handler.domains.join_domains` soundly approximates the union of
input domains. It is not exact runtime set union and need not be a least upper
bound in the full representation space. Existing integer intervals and explicit
integers are enclosed by one interval, filling gaps even below the threshold.
Merging implicit powerset universes can introduce sets mixing members from
different inputs. Explicit sets outside the merged powerset remain explicit.
Above the threshold, explicit integers widen to an enclosing interval and
explicit reals widen to unknown. Unknown inputs and compound Boolean/numeric
collisions also produce unknown.

`Domain` equality and hashing compare stored representations, not denotations.
For example, `Domain(ints=frozenset({3}))` and `Domain(int_range=(3, 3))`
denote the same singleton but compare unequal and remain distinct dictionary
keys. Constructors do not canonicalize these representations.

Currently not under version control, do not commit or pre-commit this file but
always ensure it's correctly formatted and up to date.
