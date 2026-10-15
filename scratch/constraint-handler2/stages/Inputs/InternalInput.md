## Information

This file describes a possible internal representation of the input accepted by
the `ConstraintStore` interface in [PythonInput](PythonInput.md). The store
retains declarations and expressions for later processing; it does not evaluate
expressions or solve constraints.

## ASP Format

TBD

## Python Datastructure

```python
enum ValueType {
	boolean,
	integer,
	floating_point,
	string,
	none,
}

# Internal scalar literals retain their type explicitly.
# The value is the corresponding Python base-type value.
#
ValueDef(value_type: ValueType, value: Any)


@dataclass(frozen=True)
class VariableChoice:
	value: ExprId
	label: str


@dataclass(frozen=True)
class VariableDefinition:
	value: ExprId
	label: str


@dataclass(frozen=True)
class VariableDefault:
	value: ExprId
	condition: ExprId
	priority: int
	label: str


class Variable:
	choices: list[VariableChoice]
	definitions: list[VariableDefinition]
	defaults: list[VariableDefault]


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


# Expr is the internal recursive expression type. Its forms use the same
# simple names as the Python-facing types, in a distinct namespace.
#
Expr = ValueDef | VariableRef | Set | Tuple | Operation
Set = frozenset[Expr]
Tuple = tuple[Expr, ...]
OperationArg = Expr | Lambda | Python


@dataclass(frozen=True)
class Operation:
	op: Operator
	args: tuple[OperationArg, ...]


Lambda(vars: tuple[VariableRef, ...], expr: Expr)
Python(fn: str)
```

## Usage

Stages that consume this representation can import its types explicitly:

```python
from internal_input import Operation, Operator, ValueDef, ValueType

sum_expr = Operation(
	Operator.add,
	(ValueDef(ValueType.integer, 1), ValueDef(ValueType.integer, 2)),
)
```

## TODO
