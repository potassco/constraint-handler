# Changes

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
