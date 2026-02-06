# Copilot Instructions for constraint-handler

## Project Overview

**constraint_handler** is a Python library built on top of Clingo (Answer Set
Programming solver) for solving discrete combinatorial decision or optimization
problems where constraints and variables are defined through expressions. The
project is part of the Potassco suite.

- **Language**: Python 3.12+
- **Primary Dependency**: clingo>=5.7.1
- **Project Type**: Python library with ASP (Answer Set Programming) logic
  files
- **Size**: Small to medium (~20 Python files in src/, ~150 test cases)
- **Build System**: setuptools with setuptools-scm for versioning
- **Documentation**: MkDocs with Material theme

## Build and Test Commands

### Initial Setup

**ALWAYS install nox first** before running any build/test commands:

```bash
python -m pip install nox
```

For development with all tools (recommended):

```bash
pip install -e .[dev]
```

### Running Tests

**Default test command** (runs pytest with Python 3.12):

```bash
nox
# OR explicitly:
nox -s test
```

- Tests take ~20-25 seconds to complete
- 149 tests across test_api.py, test_encoding.py, test_operator_validation.py,
  and clingspector tests
- **All tests must pass** before submitting changes

### Linting and Type Checking

**Pylint** (currently has many warnings - existing baseline is 7.97/10):

```bash
nox -s lint_pylint
```

**Mypy type checking** (currently has type errors - not enforced in CI):

```bash
nox -s typecheck
```

**Pre-commit hooks** (formatting with black, isort, autoflake):

```bash
# Install pre-commit (one time):
python -m pip install pre-commit
pre-commit install

# Run manually on all files:
pre-commit run --all
```

### Documentation

**Build documentation**:

```bash
nox -s doc
```

**Serve documentation locally** (runs on
http://localhost:8000/systems/constraint_handler/):

```bash
mkdocs serve
```

Note: The documentation build takes ~2-3 seconds and uses mkdocs-material
theme.

## CI/CD Pipeline

### GitHub Actions Workflows

**Test workflow** (.github/workflows/test.yml):

- Triggered on: push to devel/main/master/wip branches, all pull requests
- Runs on: ubuntu-latest, macos-latest, windows-latest
- Python versions: 3.9, 3.11 (note: project requires 3.12+, but CI uses
  3.9/3.11)
- Steps:
  1. Checkout code
  1. Setup Python 3.9 and 3.11
  1. Install nox and pre-commit
  1. Run pre-commit on all files (ubuntu-latest only)
  1. Run `nox` (executes test session)

**IMPORTANT**: On ubuntu-latest, pre-commit formatting checks run first. If
formatting is incorrect, the CI will fail. Always run `pre-commit run --all`
before committing.

**Deploy workflow** (.github/workflows/deploy.yml):

- Triggered on: version tags (v\*.*.*) or manual workflow_dispatch
- Calls test workflow first, then builds and deploys to PyPI/TestPyPI

## Project Structure

### Source Code Layout

```
src/
├── constraint_handler/          # Main library
│   ├── __init__.py             # Main entry point with add_to_control()
│   ├── data/                   # ASP logic programs (*.lp files)
│   │   ├── main.lp            # Main ASP encoding
│   │   ├── int.lp, bool.lp, float.lp, string.lp  # Type handlers
│   │   ├── set.lp, multimap.lp                   # Data structures
│   │   ├── execution.lp, conditionals.lp         # Control flow
│   │   └── propagator.lp, pythonHelper.lp        # Solver integration
│   ├── propagator.py           # Constraint handler propagator
│   ├── evaluator.py            # Expression evaluator
│   ├── schemas/                # Data schemas (Clorm-based)
│   └── utils/                  # Utility modules
└── clingspector/                # Diagnostic tool
    ├── main.py                  # CLI entry point
    └── diagnostic.py            # Diagnostics engine
```

### Test Structure

```
tests/
├── test_api.py                  # API integration tests
├── test_encoding.py             # Main test suite with parametrized tests
├── test_operator_validation.py  # Operator validation tests
├── clingspector/                # Clingspector-specific tests
└── example/                     # Test fixtures (*.lp files)
    ├── boilerplate.lp          # Standard test boilerplate
    ├── boilerplate_ground.lp
    ├── boilerplate_propagator.lp
    └── [test_name].lp          # Test case files
    └── [test_name].expected.*  # Expected outputs
```

### Configuration Files

- **pyproject.toml**: Main project config (dependencies, build system, tool
  configs)
- **noxfile.py**: Nox session definitions for testing, linting, docs
- **.pre-commit-config.yaml**: Pre-commit hook config (autoflake, isort, black,
  mdformat)
- **mkdocs.yml**: Documentation configuration
- **.envrc**: direnv configuration (optional)

## Important Development Notes

### Python and Clingo Integration

- The library uses clingo.script.enable_python() to enable Python expressions
  in ASP
- Logic program files in src/constraint_handler/data/ are loaded at runtime
- The main API is `constraint_handler.add_to_control(ctrl)` which configures a
  Clingo Control instance

### Testing Patterns

Tests use clintest library for ASP testing. Test files in tests/example/ follow
this pattern:

- `[name].lp`: Test input
- `[name].expected.all`: Expected atoms in all models
- `[name].expected.any`: Expected atoms in any model
- `[name].expected.first`: Expected atoms in first model
- `[name].expected.none`: Expect no models (UNSAT)

### Editable Installs

The project uses **editable installs** (`pip install -e .`) for development:

- Nox sessions create editable installs by default (controlled by
  EDITABLE_TESTS variable)
- In GitHub Actions, EDITABLE_TESTS is set to False for non-editable installs
- If you encounter import issues, try recreating the nox environment:
  `nox -Rs [session]` (without -R to force recreate)

### Common Issues and Workarounds

1. **Pre-commit formatting failures**: Always run `pre-commit run --all` before
   committing to avoid CI failures

1. **Pylint warnings**: The codebase has ~100+ pylint warnings. Don't aim for a
   perfect score - maintain existing quality level (7.97/10)

1. **Mypy errors**: Type checking has many errors and is not enforced in CI.
   Type annotations are partial.

1. **Clingo Python support**: When running examples manually with
   `python -m clingo`, you may see "python support not available" errors. Use
   the Python API with `constraint_handler.add_to_control()` instead.

1. **Nox session reuse**: Use `nox -Rs [session]` to reuse existing virtualenv.
   Drop `-R` if you need to recreate the environment.

## Making Changes

### Workflow

1. **Install nox and dev dependencies**:

   ```bash
   python -m pip install nox
   pip install -e .[dev]
   ```

1. **Make your changes** to Python or ASP files

1. **Run tests** immediately after changes:

   ```bash
   nox -Rs test  # Reuse environment for speed
   ```

1. **Format code** before committing:

   ```bash
   pre-commit run --all
   ```

1. **Verify tests pass**:

   ```bash
   nox  # Full test run
   ```

### File Modification Guidelines

- **Python files**: Located in src/constraint_handler/ and src/clingspector/
- **ASP logic files**: Located in src/constraint_handler/data/ (\*.lp files)
- **Tests**: Add test cases to tests/example/ following the naming convention
- **Documentation**: Edit files in docs/ and test with `mkdocs serve`

### Do NOT Modify

- Do not add new linting or testing tools unless necessary
- Do not aim to fix all pylint/mypy warnings unless related to your changes
- Do not modify .github/workflows/ unless specifically required
- Do not change Python version requirements in pyproject.toml without
  discussion

## Key Facts to Remember

- **ALWAYS run nox for testing**, not pytest directly
- **ALWAYS run pre-commit** before committing
- **Tests must complete in ~20-25 seconds** - if they take much longer,
  something is wrong
- **CI runs pre-commit on ubuntu-latest** - formatting issues will fail CI
- **The project requires Python 3.12+** but CI tests with 3.9/3.11 (legacy
  compatibility)
- **Clingo is the core dependency** - the library cannot work without it
- **ASP logic files are part of the package** - they're installed as package
  data

## Trust These Instructions

These instructions have been validated by running all commands and examining
the codebase thoroughly. If you encounter behavior that differs from what's
documented here, investigate the specific issue rather than assuming these
instructions are incorrect. The most likely causes of differences are:

1. Missing nox installation
1. Using pytest directly instead of nox
1. Not running pre-commit before committing
1. Environment/cache issues (solved by recreating nox environments without -R)
