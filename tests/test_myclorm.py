from __future__ import annotations

import typing

import clingo
import pytest

import constraint_handler.myClorm as myClorm
from constraint_handler.schemas.expression import ConditionalOperator

T = typing.TypeVar("T")


class SampleRecord(typing.NamedTuple):
    count: int
    label: str


class HookedTuple(tuple, typing.Generic[T]):
    def __new__(cls, values=()):
        return super().__new__(cls, values)

    @classmethod
    def pytocl(cls, value, target_args=()):
        return myClorm.nest([myClorm.pytocl(e) for e in value], cons="hook", nil="nil")

    @classmethod
    def cltopy(cls, func, target_args=()):
        subtarget = target_args[0] if target_args else typing.Any
        elements = myClorm.unnest(func, cons="hook", nil="nil")
        return cls(myClorm.cltopy(e, subtarget) for e in elements)


class NoneReturningConverter:
    @classmethod
    def pytocl(cls, value, target_args=()):
        return None

    @classmethod
    def cltopy(cls, func, target_args=()):
        return None


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (True, clingo.Function("true", [])),
        (False, clingo.Function("false", [])),
        (7, clingo.Number(7)),
        ("hello", clingo.String("hello")),
        (None, clingo.Function("none", [])),
    ],
)
def test_pytocl_primitives(value, expected):
    assert myClorm.pytocl(value) == expected


def test_pytocl_float_encodes_as_float_function():
    assert myClorm.pytocl(3.5) == clingo.Function("float", [clingo.String("3.5")])


def test_pytocl_namedtuple_uses_predicate_name_and_fields():
    record = SampleRecord(3, "tag")

    assert myClorm.pytocl(record) == clingo.Function("sampleRecord", [clingo.Number(3), clingo.String("tag")])


def test_pytocl_list_encodes_nested_cons_shape():
    assert myClorm.pytocl([1, 2]) == clingo.Function(
        "",
        [clingo.Number(1), clingo.Function("", [clingo.Number(2), clingo.Function("", [])])],
    )


def test_hashablelist_is_immutable_sequence():
    value = myClorm.HashableList([1, 2])

    with pytest.raises(AttributeError):
        value.append(3)


def test_hashablelist_round_trip_preserves_list_shape():
    value = myClorm.HashableList([1, 2])

    symbol = myClorm.pytocl(value, myClorm.HashableList[int])

    assert symbol == myClorm.pytocl([1, 2])
    assert myClorm.cltopy(symbol, myClorm.HashableList[int]) == myClorm.HashableList([1, 2])


def test_cltopy_without_target_decodes_primitives_and_collections():
    assert myClorm.cltopyNoTarget(clingo.Number(5)) == 5
    assert myClorm.cltopyNoTarget(clingo.String("abc")) == "abc"
    assert myClorm.cltopyNoTarget(clingo.Function("none", [])) is None
    assert myClorm.cltopyNoTarget(clingo.Function("true", [])) is True
    assert myClorm.cltopyNoTarget(myClorm.pytocl([1, 2])) == myClorm.HashableList([1, 2])
    assert myClorm.cltopyNoTarget(myClorm.pytocl(frozenset({1, 2}))) == frozenset({1, 2})


def test_cltopy_typed_namedtuple_decodes_symbol():
    symbol = clingo.Function("sampleRecord", [clingo.Number(4), clingo.String("item")])

    assert myClorm.cltopy(symbol, SampleRecord) == SampleRecord(4, "item")


def test_cltopy_typed_list_and_tuple():
    assert myClorm.cltopy(myClorm.pytocl([1, 2]), list[int]) == myClorm.HashableList([1, 2])
    assert myClorm.cltopy(
        clingo.Function("", [clingo.Number(1), clingo.String("x")]),
        tuple[int, str],
    ) == (1, "x")


def test_cltopy_typed_union_accepts_pep604_union():
    assert myClorm.cltopy(clingo.Number(9), int | str) == 9
    assert myClorm.cltopy(clingo.String("v"), int | str) == "v"


def test_cltopy_namedtuple_failure_raises_failed_instantiation():
    symbol = clingo.Function("differentRecord", [clingo.Number(1), clingo.String("x")])

    with pytest.raises(myClorm.FailedInstantiationExn):
        myClorm.cltopy(symbol, SampleRecord)


def test_pytocl_typing_union_target_is_supported():
    assert myClorm.pytocl(5, typing.Union[int, str]) == clingo.Number(5)


def test_enum_round_trip_uses_enum_value_not_member_name():
    symbol = myClorm.pytocl(ConditionalOperator.IF)

    assert symbol == clingo.Function("if", [])
    assert myClorm.cltopy(symbol, ConditionalOperator) is ConditionalOperator.IF


def test_pytocl_generic_alias_target_is_supported():
    assert myClorm.pytocl([1, 2], list[int]) == myClorm.pytocl([1, 2])


def test_pytocl_typing_optional_target_is_supported():
    assert myClorm.pytocl(None, typing.Optional[int]) == clingo.Function("none", [])


def test_pytocl_tuple_generic_alias_target_is_supported():
    assert myClorm.pytocl((1, "x"), tuple[int, str]) == clingo.Function("", [clingo.Number(1), clingo.String("x")])


def test_pytocl_nested_tuple_is_supported():
    assert myClorm.pytocl((1, ("x", 2))) == clingo.Function(
        "",
        [
            clingo.Number(1),
            clingo.Function("", [clingo.String("x"), clingo.Number(2)]),
        ],
    )


def test_cltopy_without_target_decodes_nested_tuple():
    symbol = clingo.Function(
        "",
        [
            clingo.Number(1),
            clingo.Function("", [clingo.String("x"), clingo.Number(2)]),
        ],
    )

    assert myClorm.cltopyNoTarget(symbol) == (1, ("x", 2))


def test_cltopy_variadic_tuple_target_is_supported():
    symbol = clingo.Function("", [clingo.Number(1), clingo.Number(2), clingo.Number(3)])

    assert myClorm.cltopy(symbol, tuple[int, ...]) == (1, 2, 3)


def test_cltopy_nested_typed_tuple_is_supported():
    symbol = clingo.Function(
        "",
        [
            clingo.Number(1),
            clingo.Function("", [clingo.String("x"), clingo.Number(2)]),
        ],
    )

    assert myClorm.cltopy(symbol, tuple[int, tuple[str, int]]) == (1, ("x", 2))


def test_pytocl_variadic_tuple_target_is_supported():
    assert myClorm.pytocl((1, 2, 3), tuple[int, ...]) == clingo.Function(
        "",
        [clingo.Number(1), clingo.Number(2), clingo.Number(3)],
    )


def test_cltopy_fixed_length_tuple_arity_mismatch_raises_failed_instantiation():
    symbol = clingo.Function("", [clingo.Number(1)])

    with pytest.raises(myClorm.FailedInstantiationExn):
        myClorm.cltopy(symbol, tuple[int, str])


def test_pytocl_generic_alias_uses_origin_custom_converter_hook():
    value = HookedTuple([1, 2])

    symbol = myClorm.pytocl(value, HookedTuple[int])

    assert symbol == clingo.Function(
        "hook",
        [
            clingo.Number(1),
            clingo.Function("hook", [clingo.Number(2), clingo.Function("nil", [])]),
        ],
    )


def test_cltopy_generic_alias_uses_origin_custom_converter_hook():
    symbol = clingo.Function(
        "hook",
        [
            clingo.Number(1),
            clingo.Function("hook", [clingo.Number(2), clingo.Function("nil", [])]),
        ],
    )

    value = myClorm.cltopy(symbol, HookedTuple[int])

    assert isinstance(value, HookedTuple)
    assert value == HookedTuple([1, 2])


def test_cltopy_custom_converter_returning_none_is_honored():
    symbol = clingo.Number(1)

    assert myClorm.cltopy(symbol, NoneReturningConverter) is None


def test_pytocl_custom_converter_returning_none_is_honored():
    assert myClorm.pytocl(1, NoneReturningConverter) is None
