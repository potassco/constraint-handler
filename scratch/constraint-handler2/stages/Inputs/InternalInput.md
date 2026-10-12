## Information

This file describes a possible internal representation of the input accepted by
the `ConstraintStore` interface in [PythonInput](PythonInput.md). The store
retains declarations and expressions for later processing; it does not evaluate
expressions or solve constraints.

## ASP Format

TBD

## Python Datastructure

```python
class VariableDefault:
	value: ExprId
	condition: ExprId
	priority: int
	label: str


class Variable:
	variable_kind: VariableKind
	domain: Optional[tuple[ExprId, ...]]
	definition: Optional[ExprId]
	defaults: list[VariableDefault]
    label: str # can we have several declarations/definitions?


@dataclass(frozen=True)
class Constraint:
	expr: ExprId
	is_check: bool
	label: str


@dataclass
class ConstraintStore:
	variables: dict[VariableRef, Variable]
	constraints: list[Constraint]
	_expressions: dict[ExprId, Expr]
```

## TODO
