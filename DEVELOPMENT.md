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

## Performance Benchmarks

The encoding performance checks live in
[tests/test_encoding.py](tests/test_encoding.py), and their input programs live
under [tests/example/performance](tests/example/performance). The `performance`
nox session runs the threshold-based regression checks and the
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
individual cases directly.

The default `nox -s test` session excludes `performance` tests so the normal
test matrix stays practical.

## Expectation Fixtures

Encoding tests pair a program named `[name].lp` with optional expectation files
named `[name].expected.<suffix>`. Each nonblank line in an atom expectation
file is one complete Clingo term. Whitespace inside a term is allowed, but
multiple terms must be written on separate lines.

```text
value(x, val(int, 12))
value(y,val(int,13))
```

The supported suffixes are:

- `all`, `any`, `first`, and `last`: atom must occur in every, any, first, or
  last model respectively.
- `none`: atom must occur in no model; it does not assert that the program is
  unsatisfiable.
- `brave` and `cautious`: atom must occur in the final model with the matching
  enumeration mode.
- `optall`, `optany`, and `optnone`: atom must occur in every, any, or no
  optimal model respectively.
- `stats`: one `key=value` entry per line. `models=<count>` asserts the exact
  number of models.

`all`, `none`, `first`, `last`, `optall`, and `optnone` implicitly also require
at least one model unless an `any`, `brave`, `cautious`, or `optany`
expectation is present.

[editable]: https://setuptools.pypa.io/en/latest/userguide/development_mode.html
[nox]: https://nox.thea.codes/en/stable/index.html
[pipx]: https://pypa.github.io/pipx/
[pre]: https://pre-commit.com/
