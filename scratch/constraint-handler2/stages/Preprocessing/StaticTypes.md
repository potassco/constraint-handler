## Information

Maps each variable and each expression to its static type.

## Python Datastructure

```python
class SetOf:
	elements: frozenset[ValueType]
	can_be_empty: bool


class TupleType:
	elements: tuple["Type", ...]


class UnknownType:
	pass


Type = frozenset[ValueType | SetOf | TupleType] | UnknownType


class StaticTypes:
	variables: dict[VariableRef, Type]
	exprs: dict[ExprId, Type]
```

## TODO

- this is a representation that only supports non-nested sets
- consider extending `ValueType` and `Type` to support nested sets if needed
