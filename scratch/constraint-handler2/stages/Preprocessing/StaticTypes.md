## Information

Maps each variable and visited expression to its static type. Lambda-local
expressions are stored separately for each binding environment.

## Python Datastructure

```python
class SetOf:
	elements: frozenset[ValueType]
	can_be_empty: bool


class TupleType:
	elements: tuple["Type", ...]


class UnknownType:
	"""Immutable singleton; every UnknownType() call returns UNKNOWN."""


UNKNOWN: UnknownType


type TypeMember = ValueType | SetOf | TupleType
type Type = frozenset[TypeMember] | UnknownType
type TypeScope = frozenset[tuple[VariableRef, Type]]


class StaticTypeStore(ExpressionStore[Type]):
	scoped_expressions: dict[tuple[Expr, TypeScope], Type]

	def lookup(self, expr: Expr, *, scope: TypeScope = frozenset()) -> Type:
		"""Use the scoped map when scope is nonempty, otherwise the global map."""

	def record(self, expr: Expr, value: Type, *, scope: TypeScope = frozenset()) -> None:
		"""Write to the scoped map when scope is nonempty, otherwise the global map."""
```

`ExpressionStore` is the generic `dict` subclass shared with `DomainStore`. The
store itself holds global entries and owns a separate `scoped_expressions`
dictionary. Both start independently empty, and initial global entries are
copied into the store. Variable references are expression keys in the same
dictionary, not a separate variable table. Keys are structural expressions, not
`ExprId`s: obtain an expression from `ConstraintStore.expressions[expr_id]`
before looking it up. Visited subexpressions are retained even if they have no
separate store ID.

A scope is an immutable set of parameter/type bindings, including outer lambda
bindings. The same body may have multiple scoped entries. Scoped lookup does
not fall back to a global entry, because that could silently use a different
binding. Missing entries raise `KeyError`.

## Type Meaning

`ValueType` distinguishes `boolean`, `integer`, `real`, `string`, and `none`. A
known type is a frozenset of alternative scalar, set, or tuple members. The
empty frozenset means no possible values; it is distinct from the unknown
singleton, which means type information is unavailable or invalid.

`SetOf.elements` contains only scalar types. `can_be_empty` is a conservative
possibility flag, not a claim that an empty value occurs. A definitely empty
set is `SetOf(frozenset(), True)`; the empty type is not an empty set. Nested
set or tuple elements inside sets are unsupported and diagnosed.

`TupleType.elements` stores the type of each position. Tuples have fixed
length, may be empty, and may contain scalars or recursively nested tuples, but
not sets. See [StaticTypeChecking](StaticTypeChecking.md) for propagation and
union rules.
