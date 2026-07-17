import math
import typing

from clingo import Function, Number, String
from clingo.symbol import SymbolType

from flat_ch.core.types import Type

_BOOL_MAP = {"true": True, "false": False}
_FLOAT_NORMALIZATION_EPSILON = 1e-9
_FLOAT_NORMALIZATION_DECIMALS = 9


def _normalize_float_string(value: typing.Any) -> str:
    numeric = float(value)
    if math.isfinite(numeric):
        numeric = round(numeric, _FLOAT_NORMALIZATION_DECIMALS)
        nearest_int = round(numeric)
        if abs(numeric - nearest_int) <= _FLOAT_NORMALIZATION_EPSILON:
            numeric = float(nearest_int)
    if numeric == 0.0:
        numeric = 0.0
    return repr(numeric)


def _deserialize_python_set(list_node) -> frozenset[typing.Any]:
    members = []
    current_node = list_node
    while hasattr(current_node, "arguments") and len(current_node.arguments) == 2:
        head, current_node = current_node.arguments
        members.append(clingo_to_python(head)[1])
    return frozenset(members)


def clingo_to_python(clingo_symbol) -> tuple[Type, typing.Any]:
    """Transforms a Clingo Term into a Python primitive along with its associated Type."""
    args = clingo_symbol.arguments
    type_id = Type(args[0].number)
    clingo_value = args[1]

    match type_id:
        case Type.NONE:
            return type_id, None
        case Type.INT:
            return type_id, clingo_value.number
        case Type.FLOAT:
            if clingo_value.type == SymbolType.Number:
                return type_id, float(clingo_value.number)
            return type_id, float(clingo_value.string)
        case Type.BOOL:
            return type_id, _BOOL_MAP.get(clingo_value.name, False)
        case Type.SET:
            return type_id, _deserialize_python_set(clingo_value)
        case Type.FAIL | Type.STRING:
            return type_id, clingo_value.string
        case _:
            return type_id, clingo_value.string


def python_to_clingo(type_id: Type, value: typing.Any) -> Function:
    """Transforms a Python primitive and its associated Type back into a Clingo Term."""
    match type_id:
        case Type.NONE:
            inner_symbol = Function("none", [])
        case Type.BOOL:
            inner_symbol = Function("true" if value else "false", [])
        case Type.INT:
            inner_symbol = Number(int(value))
        case Type.FLOAT:
            inner_symbol = String(_normalize_float_string(value))
        case Type.FAIL | Type.STRING:
            inner_symbol = String(str(value))
        case Type.SET:
            inner_symbol = _serialize_python_set(value)
        case _:
            inner_symbol = String(str(value))

    return Function("", [Number(type_id.value), inner_symbol])


def python_value_to_fch_type(result_value):
    if result_value is None:
        return Type.NONE
    if isinstance(result_value, bool):
        return Type.BOOL
    if isinstance(result_value, int):
        return Type.INT
    if isinstance(result_value, float):
        return Type.FLOAT
    if isinstance(result_value, (set, frozenset)):
        return Type.SET
    return Type.STRING


def _serialize_python_set(py_set: typing.Union[set, frozenset]) -> Function:
    """Recursively encodes a Python set object into a clingo list."""
    list_node = Function("()", [])

    try:
        sorted_elements = sorted(list(py_set))
    except TypeError:
        sorted_elements = list(py_set)

    for element in reversed(sorted_elements):
        elem_type = python_value_to_fch_type(element)
        elem_wrapper = python_to_clingo(elem_type, element)
        list_node = Function("", [elem_wrapper, list_node])

    return list_node
