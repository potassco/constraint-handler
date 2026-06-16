# Changes

## Ongoing

- introduce warnings `type(notImplemented)` and `type(notSupported)`
- fix a tuple evaluation bug
- introduce `set` and `multimap` as possible variable declarations
- support optimization in the ground engine
- implement float equality operators extensionally
- normalize float constant representation
- avoid generating badValue warnings for internal variables
- avoid displaying detailed pytest-benchmarks statistics
- unify testing of reasoning modes with testing of base solving
- replace `.expected.models` with `.expected.stats` contains key-value pairs
- use pytests's xfail and skip

## v0.0.2.dev13

- introduce caching for Clorm type resolution within `myClorm.py`.
- fix typo in commented-out alternative variable guessing implementation inside
  `finiteDomain.lp`.

## v0.0.2.dev12

- introduce caching for Python functions and dynamic Python executions and
  evaluations.
- split `pythonIsTuple` and `pythonReify` in rule bodies to prevent
  `pythonReify` from being called for non-tuples.
- drop support for predicates `conditional_hasValue` and
  `conditional_hasNoValue`
- fix typo in different-arity tuple equality and add a corresponding unit test
- introduce `variable(reservedName)` warning
- update the correction format.

## v0.0.2.dev11

## v0.0.2.dev10

- introduce the phase_request/2 predicate.
- avoid badValue warnings for ssa internal variables
- introduce a correction mechanism to adjust the solving
- reorganize preprocessing into phases
- introduce `variable_declare(X,definition)`, `variable_declare(X,set)`, and
  `variable_declare(X,multimap)`
- restrict engine interpreation to compile, ground, propagator, none
- drop support for `assign/2` declarations
- drop support for while statements
- rewrite the handling of executions to be entirely SSA-based
- add optimization result atoms `optimize_value/3`

## v0.0.2.dev9

## v0.0.2.dev8

- no changes, rerelease due to missing ci

## v0.0.2.dev7

- add supoort for tuple-expressions
- deprecate `assign/3`
- allow python expression as expression and not only as operators
- ensure that `execution_declare` defines its output variables regardless of
  `execution_run`. If there is no corresponding `execution_run` the variables
  take the value `none`.
- raise warning `atom(syntaxError)` when a set, variable, or multimap atom is
  malformed
- introduce `bool_evaluate`
- fix `optimize_maximizeSum` and `declare_variable` regressions introduced in
  v0.0.2.dev6
- add engine-specific performance benchmark sessions and pytest-benchmark
  compare workflow for saved benchmark runs

## v0.0.2.dev6

- remove `define` from the supported declarations
- add `ceil` and `floor` operator to int in compile engine, they behave like
  identity
- raise warning `atom(syntaxError)` when an execution, optimize, or preference
  atom is malformed
- rename `forbid_warning` and `ignore_warning` to `warning_forbid` and
  `warning_ignore`; allow an optional label argument for `warning_ignore`
- raise warning `statement(syntaxError)` when a statement is malformed
- Use `bad` instead of `none` for set operator python evaluation
- Update CI to run fewer smoke tests and to test only one configuration on
  routine commits. Enable caching for routine commit tests.
- Support `ceil` operator in compile engine and add corresponding test.
- Support non-fact `variable_domain` declarations in the propagator engine.
- Rename the string type from `str` to `string` and update examples, tests, and
  documentation accordingly.

## v0.0.2.dev5

- improve performance for integer addition
- turn `variable_declare`'s non-determinism to be between values rather than
  expressions
- introduce optional label argument to `variable_domain` and
  `variable_declareOptional`, if unspecified, it defaults to the label of the
  corresponding `variable_declare` atom.
- introduce optional label argument to `evaluate`
- raise warning `expression(syntaxError)` when an expression is malformed
- `evaluate` declarations now also generate expression-related warnings
- Introduce warning `variable(badValue)` that is emitted when the value of some
  variable is bad
- Introduce set_baseDomain/2 to allow non-deterministic set definitions.
- remove `recoverable`
- introduce `_operator_recoverable/1` and use it for every currently
  recoverable operator
- `isin` for sets is now `set_isin`
- `notin` for sets is now `set_notin`
- `isin` for multimaps is now `multimap_isin`

## v0.0.2.dev4

- Use an aggregate to compute sum in the compute engine
- Remove negated hypothesis in the compile implementation of multiplication
- Add handling of bad values in the propagator
- make the following operators recoverable: `conj`, `disj`, `pow`, `limp`,
  `ite`, `if`, `default`
- declaration `Identifiers` are now optional `Labels`
- convenience case `optimize_maximizeSum/3` has the label removed and is now
  `optimize_maximizeSum/2`
- convenience case `preference_variableValue/3` has the label removed and is
  now `preference_variableValue/2`
- convenience case `preference_holds/2` has the label removed and is now
  `preference_holds/1`

## v0.0.2.dev3

- use computeIdx instead of compute
- avoid patterns of the form "p(A) :- q(A), r(A), not s(A), A=some(term)." in
  favor of "p(some(term)) :- q(some(term)), r(some(term)), not s(some(term))."
  to work around gringo's heuristic getting it wrong.

## v0.0.2.dev1

- updated python version in CI
- updated docs

## 2026-03-10

- Drop blanket declaration of `eq` and `neq` for any type `T`.
- Fix type declaration of some operators that do not return floats
  (int_div,leq,etc.)
- Fix #167 and fix multimap_fold only working for some operators in compile
  engine

## 2026-02-24

- `max` operator now available for `int` (previously only `float` supported
  `max`)
- `min` operator now available for `int`
- `min` operator now available for `float`

## 2026-02-23

### Functionality

- `int_div` (previously `div`) now always returns an `int` value on success.

### Renames

| Old Name       | New Name        |
| -------------- | --------------- |
| **External**   |                 |
| `makeSet`      | `set_make`      |
| `div`          | `int_div`       |
| `fdiv`         | `float_div`     |
| **Internal**   |                 |
| `compute`      | `_compute`      |
| `computeIdx`   | `_computeIdx`   |
| `computed`     | `_computed`     |
| `computedIdx`  | `_computedIdx`  |
| `stageCompute` | `_stageCompute` |

## v0.1.0

- create project
