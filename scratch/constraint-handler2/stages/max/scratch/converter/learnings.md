# Learnings: Python statements in compile1 SSA

## How Python statements are handled

- `statement_python(CODE)` is analysed at grounding time by
  `pythonStatementVariables` (`interface.py`). The names it returns are the
  statement's SSA outputs.
- SSA rules live in
  `src/constraint_handler/data/2_single_static_assignment/statement.lp`. Each
  detected name gets a `pythonExtract(CODE, X)` operation whose inputs are
  every name visible in the context.
- Runtime execution is in `evaluator.py`: `cached_exec` runs the code and
  `pythonExtract_operator` evaluates the output name.
- Only statically assigned names are tracked. Side effects such as `global`,
  `globals()[...]` writes, `exec`, and `import` are invisible to the SSA,
  although the runtime environment still holds them.

## Extraction versus declaration

- Extraction is driven by static detection, not by the declared outputs. `OUTS`
  only selects what is exported as `execution_output(PRG, X)`.
- Declared output names are still needed as the interface to the caller.
  Exporting every detected name would leak temporaries and produce more atoms.
- Detection happens at grounding time, so the names must be known then.

## Behaviour observed by running probes

- A single `statement_python` with two lines (`"l = [1,2,3]\nx = sum(l)"`)
  exports `x` = 6 correctly, because both names stay inside one statement.
- Cross-statement visibility works for ints:
  `seq2(statement_python("l = 5"), statement_python("x = l + 1"))` gives `x` =
  6\.
- Python lists have no clingo value representation.
  `statement_python("l = [1,2,3]")` exported as `l` gives `bad`.
- One `bad` name poisons later statements. `_statement_pythonInputMap` passes
  every context name into the next statement, and `cached_exec` returns no
  value when any input is `Bad`. So
  `seq2(statement_python("l = [1,2,3]"), statement_python("x = 1"))` gives `x`
  = `bad` even though `x` does not use `l`.
- Unbound output gives `bad` with a `NameError` pythonError. `Bad` input gives
  `bad` with no warning. `__succeeds` is False after `FailIntegrityExn`.

## Current scratch audit

The observations above describe the legacy implementation. The current audit
queries `DomainCache.get_domain()` for expression roots and variables rather
than inspecting cached metadata. Its domain summaries count unknown, empty,
integer, set, nullable, and tuple domains. Set domains describe possible members,
not exact set alternatives. Unsupported exported Python results, including lists,
now produce preprocessing diagnostics and unknown domains.

Run the scratch tests from `stages/max` with
`uv run --locked python -m pytest scratch/converter/test_converter.py --no-cov`.
Using `python -m pytest` keeps the project root importable by generated callbacks.
