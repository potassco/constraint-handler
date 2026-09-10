from __future__ import annotations

import typing
from dataclasses import dataclass, field

import clingo
import pytest

import constraint_handler.myClorm as myClorm
from constraint_handler.schemas.operators import ConditionalOperator

T = typing.TypeVar("T")
U = typing.TypeVar("U")


class SampleRecord(typing.NamedTuple):
    count: int
    label: str


class GenericNamedTuple(typing.NamedTuple, typing.Generic[T, U]):
    first: T
    second: U


class CustomRecord:
    count: int
    label: str

    def __init__(self, count, label):
        self.count = count
        self.label = label


class KeywordRecord:
    count: int
    label: str

    def __init__(self, *, count, label):
        self.count = count
        self.label = label


@dataclass(frozen=True)
class SampleDataclass:
    count: int
    label: str


@dataclass
class GenericDataclass(typing.Generic[T]):
    value: T


@dataclass(frozen=True)
class MultiGenericDataclass(typing.Generic[T, U]):
    first: T
    second: T
    third: U
    label: str


@dataclass
class NestedGenericDataclass(typing.Generic[T, U]):
    values: list[tuple[T, U]]


@dataclass
class DataclassWithName:
    name: str


@dataclass
class DataclassWithDerivedField:
    count: int
    label: str
    display: str = field(init=False)

    def __post_init__(self):
        self.display = f"{self.label}:{self.count}"


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


def test_pytocl_dataclass_uses_predicate_name_and_init_fields():
    record = DataclassWithDerivedField(3, "tag")

    assert myClorm.pytocl(record) == clingo.Function(
        "dataclassWithDerivedField", [clingo.Number(3), clingo.String("tag")]
    )


def test_pytocl_dataclass_uses_class_name_when_it_has_a_name_field():
    assert myClorm.pytocl(DataclassWithName("tag")) == clingo.Function("dataclassWithName", [clingo.String("tag")])


def test_pytocl_list_encodes_nested_cons_shape():
    assert myClorm.pytocl([1, 2]) == clingo.Function(
        "",
        [clingo.Number(1), clingo.Function("", [clingo.Number(2), clingo.Function("", [])])],
    )


def test_immutablelist_is_immutable_sequence():
    value = myClorm.ImmutableList([1, 2])

    assert repr(value) == "ImmutableList([1, 2])"

    with pytest.raises(AttributeError):
        value.append(3)


def test_immutablelist_round_trip_preserves_list_shape():
    value = myClorm.ImmutableList([1, 2])

    symbol = myClorm.pytocl(value, myClorm.ImmutableList[int])

    assert symbol == myClorm.pytocl([1, 2])
    assert myClorm.cltopy(symbol, myClorm.ImmutableList[int]) == myClorm.ImmutableList([1, 2])


def test_cltopy_without_target_decodes_primitives_and_collections():
    assert myClorm.cltopyNoTarget(clingo.Number(5)) == 5
    assert myClorm.cltopyNoTarget(clingo.String("abc")) == "abc"
    assert myClorm.cltopyNoTarget(clingo.Function("none", [])) is None
    assert myClorm.cltopyNoTarget(clingo.Function("true", [])) is True
    assert myClorm.cltopyNoTarget(myClorm.pytocl([1, 2])) == myClorm.ImmutableList([1, 2])
    assert myClorm.cltopyNoTarget(myClorm.pytocl(frozenset({1, 2}))) == frozenset({1, 2})


def test_cltopy_set_is_encoded_with_clingo_ordered_elements():
    elements = [2, 1, "b", "a"]  # note: Python doesn't support`sorting of mixed types but clingo does.
    symbol = myClorm.pytocl(frozenset(elements))
    clingo_elements = sorted([clingo.Number(1), clingo.Number(2), clingo.String("a"), clingo.String("b")])
    assert symbol == clingo.Function("set", [myClorm.pytocl(clingo_elements)])


def test_cltopy_typed_namedtuple_decodes_symbol():
    symbol = clingo.Function("sampleRecord", [clingo.Number(4), clingo.String("item")])

    assert myClorm.cltopy(symbol, SampleRecord) == SampleRecord(4, "item")


def test_cltopy_typed_generic_namedtuple_decodes_symbol():
    symbol = clingo.Function("genericNamedTuple", [clingo.Number(4), clingo.String("item")])

    assert myClorm.cltopy(symbol, GenericNamedTuple[int, str]) == GenericNamedTuple(4, "item")


def test_cltopy_typed_custom_class_decodes_symbol():
    symbol = clingo.Function("customRecord", [clingo.Number(4), clingo.String("item")])

    value = myClorm.cltopy(symbol, CustomRecord)

    assert value.count == 4
    assert value.label == "item"


def test_cltopy_typed_keyword_only_class_decodes_symbol():
    symbol = clingo.Function("keywordRecord", [clingo.Number(4), clingo.String("item")])

    value = myClorm.cltopy(symbol, KeywordRecord)

    assert value.count == 4
    assert value.label == "item"


def test_cltopy_typed_dataclass_decodes_symbol():
    symbol = clingo.Function("sampleDataclass", [clingo.Number(4), clingo.String("item")])

    assert myClorm.cltopy(symbol, SampleDataclass) == SampleDataclass(4, "item")


def test_cltopy_typed_generic_dataclass_decodes_symbol():
    symbol = clingo.Function("genericDataclass", [clingo.Number(4)])

    assert myClorm.cltopy(symbol, GenericDataclass[int]) == GenericDataclass(4)


def test_cltopy_typed_multi_generic_dataclass_decodes_symbol():
    symbol = clingo.Function(
        "multiGenericDataclass",
        [clingo.Number(4), clingo.Number(5), clingo.String("item"), clingo.String("tag")],
    )

    assert myClorm.cltopy(symbol, MultiGenericDataclass[int, str]) == MultiGenericDataclass(4, 5, "item", "tag")


def test_cltopy_typed_nested_generic_dataclass_decodes_symbol():
    symbol = clingo.Function(
        "nestedGenericDataclass",
        [myClorm.pytocl([(4, "item"), (5, "other")])],
    )

    assert myClorm.cltopy(symbol, NestedGenericDataclass[int, str]) == NestedGenericDataclass(
        myClorm.ImmutableList([(4, "item"), (5, "other")])
    )


def test_pytocl_typed_multi_generic_dataclass_encodes_symbol():
    value = MultiGenericDataclass(4, 5, "item", "tag")

    assert myClorm.pytocl(value, MultiGenericDataclass[int, str]) == clingo.Function(
        "multiGenericDataclass",
        [clingo.Number(4), clingo.Number(5), clingo.String("item"), clingo.String("tag")],
    )


def test_cltopy_dataclass_reconstructs_derived_fields():
    symbol = clingo.Function("dataclassWithDerivedField", [clingo.Number(4), clingo.String("item")])

    assert myClorm.cltopy(symbol, DataclassWithDerivedField) == DataclassWithDerivedField(4, "item")


def test_find_in_model_decodes_dataclass_atoms():
    symbol = clingo.Function("sampleDataclass", [clingo.Number(4), clingo.String("item")])

    class Model:
        def symbols(self, **_):
            return [symbol]

    assert myClorm.findInModel(Model(), SampleDataclass) == {symbol: SampleDataclass(4, "item")}


def test_find_in_control_and_propagate_init_decode_custom_class_atoms():
    symbol = clingo.Function("customRecord", [clingo.Number(4), clingo.String("item")])
    unknown = clingo.Function("unknown", [])

    class Atom:
        def __init__(self, symbol, literal):
            self.symbol = symbol
            self.literal = literal

    class Control:
        def __init__(self):
            self.atom = Atom(symbol, 1)
            self.unknown_atom = Atom(unknown, 2)
            self.symbolic_atoms = self

        def by_signature(self, name, arity):
            assert (name, arity) == ("customRecord", 2)
            return [self.atom]

        def __iter__(self):
            return iter([self.atom, self.unknown_atom])

        def solver_literal(self, literal):
            return literal

    control = Control()

    assert vars(next(iter(myClorm.findInControl(control, CustomRecord).values()))) == {"count": 4, "label": "item"}
    assert vars(next(iter(myClorm.findInPropagateInit(control, CustomRecord)))) == {"count": 4, "label": "item"}

    found = myClorm.findInControl(control, CustomRecord | typing.Any)
    assert vars(found[control.atom]) == {"count": 4, "label": "item"}
    assert found[control.unknown_atom] == unknown
    assert myClorm.findInPropagateInit(control, CustomRecord | typing.Any)[unknown] == 2


def test_cltopy_typed_list_and_tuple():
    assert myClorm.cltopy(myClorm.pytocl([1, 2]), list[int]) == myClorm.ImmutableList([1, 2])
    assert myClorm.cltopy(
        clingo.Function("", [clingo.Number(1), clingo.String("x")]),
        tuple[int, str],
    ) == (1, "x")


def test_cltopy_typed_union_accepts_pep604_union():
    assert myClorm.cltopy(clingo.Number(9), int | str) == 9
    assert myClorm.cltopy(clingo.String("v"), int | str) == "v"


@pytest.mark.xfail(strict=True, reason="Annotated targets are not decoded")
def test_cltopy_typed_annotated_decodes_symbol():
    assert myClorm.cltopy(clingo.Number(4), typing.Annotated[int, "metadata"]) == 4


@pytest.mark.xfail(strict=True, reason="Literal targets are not decoded")
def test_cltopy_typed_literal_decodes_symbol():
    assert myClorm.cltopy(clingo.Number(4), typing.Literal[4]) == 4


def test_cltopy_namedtuple_failure_raises_failed_instantiation():
    symbol = clingo.Function("differentRecord", [clingo.Number(1), clingo.String("x")])

    with pytest.raises(myClorm.FailedInstantiationExn):
        myClorm.cltopy(symbol, SampleRecord)


def test_cltopy_dataclass_failure_raises_failed_instantiation():
    symbol = clingo.Function("differentRecord", [clingo.Number(1), clingo.String("x")])

    with pytest.raises(myClorm.FailedInstantiationExn):
        myClorm.cltopy(symbol, SampleDataclass)


def test_pytocl_typing_union_target_is_supported():
    assert myClorm.pytocl(5, typing.Union[int, str]) == clingo.Number(5)


@pytest.mark.xfail(strict=True, reason="record field annotations are not validated while encoding")
def test_pytocl_rejects_generic_dataclass_field_with_wrong_type():
    with pytest.raises(myClorm.FailedInstantiationExn):
        myClorm.pytocl(GenericDataclass("item"), GenericDataclass[int])


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
