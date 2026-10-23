## Information

## ASP Format

## Python Datastructure

Real values use Python `float` as their representation.

type SetValue = bool | int | float | str | None | tuple[SetValue, ...]

```python
class Domain:
	bools: frozenset[bool] = frozenset()
	ints: frozenset[int] = frozenset()
	int_range: tuple[int, int] | None = None  # Inclusive bounds.
	reals: frozenset[float] = frozenset()
	has_none: bool = False
	strings: frozenset[str] = frozenset()
	tuples: frozenset[tuple[SetValue, ...]] = frozenset()
	explicit_sets: frozenset[frozenset[SetValue]] = frozenset()
	implicit_set_elements: frozenset[SetValue] | None = None
	unknown: bool = False
```

The integer part of a numeric domain is `ints` together with every integer in
`int_range` (inclusive); the real part is `reals`. `int_range` is a compact
representation and does not require materializing its values. These parts stay
separate during domain computation: integer-only results may use `int_range`,
while real results are stored explicitly in `reals` or cause the result to
become `unknown` when they cannot be computed within the threshold.

`explicit_sets` contains complete set values. `implicit_set_elements` describes
the elements of an implicit set domain, where every subset is possible; `None`
means there is no implicit set domain, while an empty frozenset allows only the
empty set. `has_none` adds `None` to the domain, and `tuples` contains complete
tuple values. `unknown` means any supported value may occur and therefore
represents the top domain. sets can't be nested.

A boolean domain uses `bools` for its possible boolean values and `has_none` to
indicate whether `None` is also possible. The full boolean domain is
`bools={false, true}`; a nullable boolean domain also sets `has_none=true`.

## TODO:

- this is a representation that only supports non-nested sets
- consider extending `SetValue` and `Domain` to support nested sets if needed
