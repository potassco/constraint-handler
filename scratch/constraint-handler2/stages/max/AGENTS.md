# constraint-handler

Python 3.14+ library managed with uv. Import name: `constraint_handler`.

## Structure

- `src/constraint_handler/`: library code and typing marker.
- `tests/`: pytest tests.
- `pyproject.toml`: packaging, dependencies, and tool configuration.
- `uv.lock`: locked development dependencies; keep committed.
- `noxfile.py`: installed-package tests with branch coverage.
- `.github/workflows/test.yml`: test-only CI.

## Documentation

Every explicitly defined Python class, function, and method must have a concise
docstring describing its purpose or contract. This includes private helpers,
tests, and tooling functions.

## Commands

Run from this directory:

```sh
uv sync --locked                      # Set up environment
uv run pre-commit install             # Install commit hooks
uv run nox -r -s tests                 # Run tests with coverage
uv run pyright                        # Strict type checking
uv run ruff check .                    # Lint
uv run ruff format .                   # Format
uv run pre-commit run --all-files      # All commit checks
uv build                              # Build wheel and source distribution
```
