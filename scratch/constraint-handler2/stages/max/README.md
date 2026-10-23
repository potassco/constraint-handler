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
