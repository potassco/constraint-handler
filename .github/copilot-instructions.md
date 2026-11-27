# Copilot Instructions for constraint-handler

## Scope and Sources of Truth

This Python library implements expression-based constraints over Clingo, with
ASP preprocessing and multiple solving engines. Python requirements,
dependencies, and tool settings are defined in
[pyproject.toml](../pyproject.toml).

Verify implementation details against current code and configuration. These
instructions describe conventions, not proof that commands or behavior have
been validated. Report specific discrepancies between guidance and observed
behavior rather than assuming an environment problem.

Keep changes scoped to the request and preserve unrelated worktree changes,
names, and ordering. Add tests only when requested. Ask before changing Python
requirements, CI workflows, or the testing architecture.

## Implementation Layout

- `src/constraint_handler/main.py` registers ASP modules and templates and
  configures controls through `add_to_control`.
- `src/constraint_handler/data/` contains numbered context, default-argument,
  SSA, sugar, analysis, presolve, module, solve, and output stages. `template/`
  holds phase-instantiated rules. Inspect the owning stage and registration
  before changing a preprocessing rule.
- `evaluator.py`, `python_externals/`, `schemas/`, and `myClorm.py` under
  `src/constraint_handler/` handle evaluation, callbacks, and conversion.
  `propagator/` and `reasoning_modes/` handle propagator evaluation and model
  accumulation.
- `src/flat_ch/` has its own registration, intermediate representation, and
  encodings. `src/clingspector/` contains the diagnostic CLI.

Consult [design.md](../design.md) and [docs/developer/](../docs/developer/) for
architecture. ASP-directory README files are predicate inventories; keep
explanatory semantics in developer documentation.

## Test Placement

Before adding a test, inspect a neighboring test for the same behavioral layer
and the existing harness. Choose placement by behavior, not by whether Python
drives Clingo.

- ASP correctness cases belong under `tests/correctness/`, paired as
  `[name].lp` and `[name].expected.*` in the appropriate category directory.
- `tests/test_encoding.py` is the shared fixture registry and generic runner.
  Register names in the appropriate category list, preserving alphabetical
  order for entries touched. Keep individual test programs, assertions, and
  test-specific helpers out of this file. Change runner behavior only for an
  explicitly requested harness change.
- Shared expectation fixtures assert public output predicates, not internal
  `_variable_declared`, `_passed(...)`, or generated `loc(...)` details that
  other engines may not expose.
- Prefer a public-behavior fixture that exhibits the bug. If internal
  preprocessing inspection is necessary and no existing focused test module
  fits, explain the conflict and ask about placement before adding a new
  testing structure. Do not put the case in the generic runner.
- `tests/test_api.py` is for Python API behavior, not general ASP regressions.
  Other Python test modules cover their named subsystem or interface.
- `tests/utils/testing.py` owns shared encoding utilities.
  `tests/flat_ch/test_correctness.py` consumes shared fixtures with
  FCH-specific exclusions; do not add fixture-specific FCH parameters to the CH
  matrix.
- Preserve skip/xfail reasons and do not mask unrelated engine failures.

Read
[DEVELOPMENT.md#expectation-fixtures](../DEVELOPMENT.md#expectation-fixtures)
for the complete contract. Each nonblank expectation line is one complete
Clingo atom. Unlisted fixtures are not run. `.expected.none` asserts atom
absence, not unsatisfiability; `models=0` in `.expected.stats` asserts no
models. Include model counts and structural statistics only when relevant to
the case.

## Local Validation

Use the existing selected Python environment and pytest directly for focused
local tests. Nox is available for CI and session-based workflows; do not
install nox or recreate environments just to run a local regression.

```bash
python -m pytest tests/test_encoding.py -k 'fixture_name' -m 'not performance'
python -m pytest tests/test_python_domain.py -k 'test_name'
```

Inspect test IDs or parametrization when selecting engines. Verify that the
requested tests actually ran. After an edit, run the smallest meaningful check
before expanding scope. For a reproducer, confirm failure for the intended
reason and report it; do not implement a fix unless requested.

The full suite can take over ten minutes. Use focused tests for small changes;
run the full suite or performance benchmarks only when explicitly requested.
The per-test encoding timeout is not a suite-duration estimate. Disclose checks
that could not run and distinguish existing failures from new ones. Do not fix
unrelated lint/type errors or rely on historical scores.

If dependencies are missing, consult the extras in pyproject.toml; test setup
uses `python -m pip install -e '.[test]'`. Ask before changing a shared
environment. Reuse existing testing and linting tools. Consult
[noxfile.py](../noxfile.py) and [DEVELOPMENT.md](../DEVELOPMENT.md) for session
definitions and benchmark workflows.

## Formatting and Documentation

Python uses Black and isort with a 120-character line length. Pre-commit also
configures autoflake, whitespace checks, and mdformat; inspect
[.pre-commit-config.yaml](../.pre-commit-config.yaml) for exclusions.

Use focused formatting checks while editing. Before a requested commit, run
`pre-commit run --all --show-diff-on-failure` and preserve unrelated changes.
Do not commit unless requested.

Documentation lives in `docs/` and uses MkDocs Material. Validate with
`mkdocs build` or preview with `mkdocs serve`. Reference and user-guide pages
describe current behavior; migration history belongs in changelogs or dedicated
migration documents. Keep engine-specific failures in tests or engine-support
documentation rather than core syntax descriptions.

## CI and Runtime Integration

Consult [.github/workflows/test.yml](workflows/test.yml) for the current matrix
and gates; do not copy version lists, test counts, or timing baselines here. CI
uses nox, checks formatting on Linux, and has a separate performance job.

ASP programs are package data loaded at runtime. Register new modules in the
owning loader/template list. Use a neighboring boilerplate or
`constraint_handler.add_to_control` to enable Clingo integration; do not assume
every `python -m clingo` invocation enables embedded Python.

In callback optimizations, explicitly project relevant keys before invocation;
do not rely on anonymous variables for projection. Shared ASP callback staging
can introduce positive support cycles: preserve stage ownership and validate
relevant tightness expectations when changing it.
