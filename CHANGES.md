# Changes

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
