import pytest

import constraint_handler.multimap as multimap
import constraint_handler.schemas.operators as operators


def test_multimap_is_immutable_mapping():
    mm = multimap.Multimap({"k": frozenset({1, 2})})

    with pytest.raises(TypeError):
        mm["k"] = frozenset({3})


def test_multimap_make_returns_immutable_multimap():
    result = multimap.evaluate_operator(
        operators.MultimapOperator.multimap_make,
        [("a", 1), ("a", 2), ("b", 3)],
    )

    assert isinstance(result.value, multimap.Multimap)
    assert result.value == multimap.Multimap({"a": frozenset({1, 2}), "b": frozenset({3})})
