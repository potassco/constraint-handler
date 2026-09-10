# Operator Evaluation

The Python implementation separates expression evaluation from the semantics of individual operator categories.

## Operator Vocabulary

`constraint_handler.schemas.operators` defines the built-in operator categories used in expression schemas:

| Category | Operators |
| --- | --- |
| `ComparisonOperator` | `eq`, `neq`, `max`, `min` |
| `StringOperator` | `concat`, `length` |
| `ConditionalOperator` | `if`, `ite`, `getOrElse`, `hasValue` |
| `ArithmeticOperator` | Arithmetic, conversion, and ordering operators |
| `LogicOperator` | Boolean operators |
| `SetOperator` | Set operators |
| `MultimapOperator` | Multimap operators |

`constraint_handler.schemas.expression` defines expression-tree nodes such as `Operation`, `Variable`, and `Val`. Its `Operator` type combines the built-in categories with Python and lambda operators.

## Evaluation

`constraint_handler.evaluator` evaluates expression trees, propagates warnings and `bad` values, and dispatches evaluated operators by category. It also owns evaluator-specific recovery policy: selected operators can still produce a result when an argument is `bad`.

The operator semantics are implemented by category:

| Module | Categories |
| --- | --- |
| `constraint_handler.arithmetic` | `ArithmeticOperator` |
| `constraint_handler.comparison` | `ComparisonOperator` |
| `constraint_handler.conditional` | `ConditionalOperator` |
| `constraint_handler.logic` | `LogicOperator` |
| `constraint_handler.multimap` | `MultimapOperator` |
| `constraint_handler.set` | `SetOperator` |
| `constraint_handler.string` | `StringOperator` |

Each semantic module exposes `evaluate_operator(operator, args)` and returns an `atom.EvalResult`. New built-in operators should be added to their category in `schemas.operators`, implemented in the corresponding semantic module, and dispatched from `evaluator.operator()`.
