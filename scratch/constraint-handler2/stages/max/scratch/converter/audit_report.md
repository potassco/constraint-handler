# Current engine corpus audit

Date: 2026-10-27. Implementation revision: `17a398c9`.

## Scope and reproduction

Run from stages/max with the ch2 interpreter:

```sh
python -m scratch.converter.audit_complex --section all --timeout 15 --cpu-seconds 10 --memory-mib 768 --output scratch/converter/audit_results.json
```

The audit attempted 411 fixtures: 393 correctness and 18 performance cases.
Each isolated worker has 768 MiB address space, 10 CPU seconds, a 15-second
parent wall timeout, and a 1,000-model cap. Core dumps are disabled. Wall
timeouts kill the worker process group. Cases run serially.

Four performance fixtures are local, untracked inputs: `issue_414_fallback`,
`issue_414_lambda`, `issue_414_native`, and `issue_414_python_operation`.
They were not added to the implementation commit. A checkout without these
files audits 407 fixtures, including 14 tracked performance cases. Their
local-only results are identified separately below.

Performance fixtures use their default constants and the explicitly labeled
scratch grounding adapter when direct conversion fails. These are exploratory
bounded runs, not comparable legacy benchmark timings or proof of direct
converter support.

Full evidence: [audit_results.json](audit_results.json). Results retain
diagnostics, callback exceptions, mismatches, engine assignments, Python row
counts, sample models, and resource limits. A limited worker retains its last
checkpoint: elapsed time and RSS there are not final measurements. No fresh
domain-only audit was run; older domain/performance artifacts are not evidence
for this revision.

## Validation

- Package and converter tests: 919 passed.
- Encoding tests after comment whitespace cleanup: 141 passed.
- Ruff lint across production code, package tests, and noxfile: passed.
- Staged whitespace check: passed.
- Full formatting check reports 11 existing files needing formatting; no
  unrelated formatting sweep was included.

## Correctness

| Status | Cases |
| --- | ---: |
| Conversion rejected | 221 |
| Preprocessing errors | 52 |
| Fact generation exception | 13 |
| All supported expectations match | 18 |
| Values match, diagnostic assertions unchecked | 38 |
| No supported value assertions | 35 |
| Value or model-count mismatch | 15 |
| Model limit, incomplete | 1 |

All 172 directly converted cases have an outcome. Of these, 107 reach model
collection, including the capped set case. Conversion rejects comprise 194
`UnsupportedFeatureError` and 27 `ConversionError` cases. Unsupported legacy
syntax, `bad` values, general ASP rules, and unsupported declarations account
for much of the unavailable coverage; these are not solver test failures.

The 13 fact-generation exceptions are:

| Exception | Cases |
| --- | ---: |
| Division by zero in candidate inputs | 7 |
| Unsupported Python tuple contents | 3 |
| Integer/string augmented assignment | 1 |
| Missing legacy evaluator module | 1 |
| Noncallable Python descriptor | 1 |

Defaults are still unimplemented: `default/basic_true` has missing defaulted
values. `expression/tuple_nested` still lacks its reference-based nested tuple.
Other mismatches include optional-choice/model-count differences and the
scratch converter's translation of legacy `ensure` into `check`. For example,
`set/conditional_assign` produces five models rather than three, with no
membership assertion failures. `core/set_execution_input_alias` and
`variable/same_val_multi_expr` also retain model/value mismatches. The JSON
contains all 15 mismatch records; this audit does not establish a single cause
for all of them.

Matching value assertions with unchecked diagnostics are not full legacy
compatibility. Cases with no supported assertions are not correctness passes.
The runner checks typed values and model counts, but not legacy warning/type/
optimization assertions or order-dependent first/last assertions. Fixture
expectations are partial specifications, not exhaustive semantic proofs.

## Sets

| Status | Cases |
| --- | ---: |
| All supported expectations match | 2 |
| Values match, diagnostic assertions unchecked | 5 |
| Model-count mismatch | 1 |
| No supported value assertions | 2 |
| Conversion rejected | 11 |
| Preprocessing rejects nested sets | 3 |
| Model limit, incomplete | 1 |

The seven matching fixtures remain `from_domain`, `same_val_multi_expr`,
`manipulation_flat`, `membership_decomposed`, `membership_python`,
`missing_declare_repair`, and `nondet_simple`. Converter regression tests cover
these fixtures.

`overapprox_boundaries` now emits zero Python rows with 40 native expressions
and reaches the 1,000-model cap, rather than the earlier CPU limit during fact
generation. Its last completed checkpoint is about 0.057 seconds. Enumeration
is not exhausted, and one existential membership expectation has not been
witnessed in the sampled models; neither a pass nor a confirmed mismatch can
be inferred from that incomplete run.

Some set fixtures still emit Python rows because of explicit Python calls or
residual nesting: `comparisons` has 32 rows, `manipulation_flat` 3,
`membership_decomposed` 16, and `membership_python` 28. Native support does not
force additional splitting merely to eliminate these calls.

## Performance

The 14 tracked performance fixtures have four fully enumerated runs without
supported value assertions, six model caps, and four CPU limits.

| Tracked fixture | Python rows | Outcome |
| --- | ---: | --- |
| assignment_chain | 0 | 1 model; no supported value assertions |
| bad_scaling_compile | 0 | 2 models; no supported value assertions |
| bad_scaling_ground | 500 | 1,000-model cap |
| cryptarithm/column | 0 | 1,000-model cap |
| cryptarithm/column_binary | 0 | 1,000-model cap |
| cryptarithm/word | 0 | CPU limit; last stage grounding |
| cryptarithm/word_binary | 0 | CPU limit; last stage grounding |
| cryptarithm/word_binary_easier | 0 | CPU limit; last stage solving |
| cryptarithm/word_ternary | 0 | CPU limit; last stage grounding |
| cryptarithm/word_ternary_easier | 0 | 1,000-model cap |
| large_int_domain | 0 | 2 models; no supported value assertions |
| repeated_constraints | 0 | 1,000-model cap |
| sum_aggregates | 0 | 1,000-model cap |
| sum_chain | 0 | 1 model; no supported value assertions |

All seven cryptarithms now emit zero Python rows. This removes the earlier
Cartesian-table bottleneck, but three variants still hit their CPU limit
during grounding, and one during solving. Native encoding is not sufficient
to eliminate every grounding or search bottleneck.

| Local-only fixture | Python rows | Outcome |
| --- | ---: | --- |
| issue_414_fallback | 54 | 343 models; no supported value assertions |
| issue_414_native | 27 | 343 models; no supported value assertions |
| issue_414_python_operation | 27 | 343 models; no supported value assertions |
| issue_414_lambda | N/A | Preprocessing errors: callable/input binding |

Across all 18 performance inputs, seven runs fully enumerate without supported
value assertions, six reach the model cap, four hit CPU limits, and one stops
in preprocessing. There are no wall timeouts or worker-exit failures in the
full 411-case audit. Unknown-input propagators, defaults, unsupported Python
results, legacy conversion gaps, and residual complex-table costs remain
limitations; no unrelated fixes were made during this audit.