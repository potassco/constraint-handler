# Development

To improve code quality, we use [nox] to run linters, type checkers, unit
tests, documentation and more. We recommend installing nox using [pipx] to have
it available globally.

```bash
# install
python -m pip install pipx
python -m pipx install nox

# run all sessions
nox

# list all sessions
nox -l

# run individual session
nox -s session_name

# run individual session (reuse install)
nox -Rs session_name
```

Note that the nox sessions create [editable] installs. In case there are
issues, try recreating environments by dropping the `-R` option. If your
project is incompatible with editable installs, adjust the `noxfile.py` to
disable them.

We also provide a [pre-commit][pre] config to autoformat code upon commits. It
can be set up using the following commands:

```bash
python -m pipx install pre-commit
pre-commit install
```

Each test in [tests/test_encoding.py](tests/test_encoding.py) has a 10-second
`pytest-timeout` thread watchdog covering setup, grounding, solving, and
teardown. On timeout, pytest prints thread stacks and terminates the test run.

## Performance Benchmarks

The encoding performance checks live in
[tests/test_performance_engines.py](tests/test_performance_engines.py), and
their input programs live under [tests/performance](tests/performance). The
`performance` nox session runs the threshold-based regression checks and the
`pytest-benchmark` capture tests together. Each run automatically stores a
saved benchmark file directly under `.benchmarks/` using a branch-and-timestamp
name.

```bash
# threshold checks plus automatic benchmark capture
nox -s performance

# run only one compile benchmark (-k parameter is for pytest)
nox -s performance -- -k compile-sum_aggregates

# run all propagator benchmark
nox -s performance -- -k propagator

# compare saved benchmark runs with a concise mean-only table
nox -s benchmark_compare -- .benchmarks/0008_master-20260420-203125.json .benchmarks/0009_feature-20260420-203125.json
```

The benchmark ids follow the pattern `compile-...`, `ground-...`,
`propagator-check-...`, and `propagator-solve-...`, so `pytest -k` can target
individual cases directly. Each encoding benchmark also times out after its
aggregate runtime threshold plus one second. The `pytest-timeout` thread
watchdog covers setup, grounding, solving, and teardown; on expiry it prints
thread stacks and terminates pytest. The aggregate threshold is the configured
average multiplied by the number of measured and warmup runs, so individual
runs may exceed the average when the overall mean still passes.

The default `nox -s test` session excludes `performance` tests so the normal
test matrix stays practical.

### Float Computation Benchmarks

The ASP programs under `tests/performance/float/` cover addition chains,
integer and fractional multiplication, equality and ordering near a small
separation, cancellation after adding a large offset, division with
multiplicative recovery, square root with squaring, and sine/cosine with the
sum of their squares. A shared three-value input domain includes negative,
exact dyadic, and repeating-fraction inputs. The workloads have three models
regardless of size and expose `value/2`.

Each workload runs at sizes 16 and 64 with `compile`, `compile2`, `fch`,
`ground`, `propagator`, and `propagator_check`. FCH trigonometry cases are
skipped because its native operator set lacks `sin` and `cos`. Timings include
control setup, loading, grounding, and solving, using one warmup and three
measured runs. The 30-second mean limit is a generous safety ceiling for
comparing implementations, rather than a calibrated baseline.

```bash
# capture all float benchmarks
nox -s performance -- -k 'float/'

# capture only FCH float benchmarks
nox -s performance -- -k 'fch and float/'

# smoke-run the workloads once each, without timing repetitions
nox -Rs test -- tests/test_performance_engines.py -m performance -k 'float/' --benchmark-disable
```

Use the same workload sizes and engine selection when comparing saved runs with
`nox -s benchmark_compare`. Engine and workload constants are recorded in the
benchmark metadata. Additional representations can use these same ASP inputs
through their engine implementations.

## Expectation Fixtures

Encoding tests pair a program named `[name].lp` with optional expectation files
named `[name].expected.<suffix>`. Each nonblank line in an expectation file is
one complete Clingo atom. Whitespace inside an atom is allowed, but distinct
atoms must be written on separate lines.

The fixture is run only when its name is listed in the appropriate category in
`tests/test_encoding.py`; add new fixtures there as well as creating their
`.lp` and `.expected.*` files.

```text
value(x, val(int, 12))
value(y,val(int,13))
```

The supported suffixes are:

- `all`, `any`, `first`, and `last`: atom must occur in every, any, first, or
  last model respectively.
- `none`: atom must occur in no model; it does not assert that the program is
  unsatisfiable.
- `brave` `cautious`, `union`, `intersection`, `supremum`, and `infimum`: atom
  must occur in the final model with the matching enumeration mode.
- `optall`, `optany`, and `optnone`: atom must occur in every, any, or no
  optimal model respectively.
- `stats`: one `key=value` entry per line. All keys are optional.
  `models=<count>` asserts the exact number of models. `tight=true` asserts
  zero strongly connected components, and `tight=false` asserts at least one.
  `choices=false` asserts zero solver choices, and `choices=true` asserts at
  least one. Boolean values are lowercase `true` or `false`; omitted fields are
  unchecked.

`all`, `none`, `first`, `last`, `optall`, and `optnone` implicitly also require
at least one model unless an `any`, `brave`, `cautious`, or `optany`
expectation is present.

[editable]: https://setuptools.pypa.io/en/latest/userguide/development_mode.html
[nox]: https://nox.thea.codes/en/stable/index.html
[pipx]: https://pypa.github.io/pipx/
[pre]: https://pre-commit.com/
