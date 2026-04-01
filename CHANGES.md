# Changes

## Ongoing
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
