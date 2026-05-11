from __future__ import annotations

import math

import pytest

from constraint_handler.utils.python_statement_analysis import (
    _annotation_to_types,
    analyze_python_statement_types,
)
from constraint_handler.utils.python_type_model import (
    DictOf,
    FunctionType,
    ListOf,
    RepeatedTupleOf,
    ScalarType,
    SetOf,
    TupleOf,
    TypeInfo,
    UnknownType,
)


def _s(t: type) -> ScalarType:
    return ScalarType(t)


def _fs(*types_: TypeInfo) -> frozenset[TypeInfo]:
    return frozenset(types_)


@pytest.mark.parametrize(
    ("snippet", "expected_names"),
    [
        ("x = 1", {"x"}),
        ("x, (y, *rest) = data", {"x", "y", "rest"}),
        ("if cond:\n    a = 1\nelse:\n    b = 2", {"a", "b"}),
        ("while ok:\n    i = i + 1", {"i"}),
        ("for item in items:\n    total = total + item", {"item", "total"}),
        ("x = f(1, y=2)\nz = obj.method(x)", {"x", "z"}),
        ("x: int = 1", {"x"}),
    ],
)
def test_analyze_python_statement_types_collects_names_in_mapping(
    snippet: str,
    expected_names: set[str],
) -> None:
    result = analyze_python_statement_types(snippet)

    assert result.has_unsupported_features is False
    assert result.unsupported_witness is None
    assert set(result.name_types) == expected_names


def test_analyze_python_statement_types_expression_statement_call_is_flagged() -> None:
    snippet = "f(1)\nx = 2"

    result = analyze_python_statement_types(snippet)

    assert result.has_unsupported_features is True
    assert result.unsupported_witness == "f(1)"
    assert result.name_types["x"] == _fs(_s(int))


def test_analyze_python_statement_types_rejects_star_args_call() -> None:
    snippet = "x = f(*args)"

    result = analyze_python_statement_types(snippet)

    assert result.has_unsupported_features is True
    assert result.unsupported_witness == "*args"
    assert result.name_types["x"] == _fs(UnknownType)


def test_analyze_python_statement_types_rejects_kw_unpack_call() -> None:
    snippet = "x = f(**kwargs)"

    result = analyze_python_statement_types(snippet)

    assert result.has_unsupported_features is True
    assert result.unsupported_witness == "**kwargs"
    assert result.name_types["x"] == _fs(UnknownType)


def test_analyze_python_statement_types_rejects_lambda_callee() -> None:
    snippet = "x = (lambda y: y)(1)"

    result = analyze_python_statement_types(snippet)

    assert result.has_unsupported_features is True
    assert result.unsupported_witness == "lambda y: y"
    assert result.name_types["x"] == _fs(UnknownType)


def test_analyze_python_statement_types_syntax_error() -> None:
    result = analyze_python_statement_types("x =")

    assert result.has_unsupported_features is True
    assert result.name_types == {}
    assert result.unsupported_reason == "syntax error"


def test_analyze_python_statement_types_basic_inference() -> None:
    snippet = "x = 1\ny = x + 2\nz = 'a' + 'b'\nw = y if cond else z"

    result = analyze_python_statement_types(snippet)

    assert result.name_types["x"] == _fs(_s(int))
    assert result.name_types["y"] == _fs(_s(int))
    assert result.name_types["z"] == _fs(_s(str))
    assert result.name_types["w"] == _fs(_s(int), _s(str))


def test_analyze_python_statement_types_reassignment_reports_exit_types_only() -> None:
    snippet = "w = 5\nw = 3.2 if x else 'food'"

    result = analyze_python_statement_types(snippet)

    assert result.has_unsupported_features is False
    assert result.name_types["w"] == _fs(_s(float), _s(str))


def test_analyze_python_statement_types_division_result_is_float() -> None:
    snippet = "x = 1 / 2"

    result = analyze_python_statement_types(snippet)

    assert result.has_unsupported_features is False
    assert result.name_types["x"] == _fs(_s(float))


@pytest.mark.parametrize(
    ("snippet", "expected_types"),
    [
        ("x = 5 // 2", _fs(_s(int))),
        ("x = 5.0 // 2", _fs(_s(float))),
        ("x = 5 // 2.0", _fs(_s(float))),
    ],
)
def test_analyze_python_statement_types_floordiv_result_type(
    snippet: str,
    expected_types: frozenset[TypeInfo],
) -> None:
    result = analyze_python_statement_types(snippet)

    assert result.has_unsupported_features is False
    assert result.name_types["x"] == expected_types


def test_analyze_python_statement_types_numeric_matmul_is_unknown() -> None:
    snippet = "x = 1 @ 2"

    result = analyze_python_statement_types(snippet)

    assert result.has_unsupported_features is False
    assert result.name_types["x"] == _fs()


@pytest.mark.parametrize(
    ("snippet", "name", "expected_types"),
    [
        ("x = -1", "x", _fs(_s(int))),
        ("x = +1.5", "x", _fs(_s(float))),
        ("x = ~1", "x", _fs(_s(int))),
        ("x = not True", "x", _fs(_s(bool))),
        ("x = not flag", "x", _fs(UnknownType)),
    ],
)
def test_analyze_python_statement_types_unary_operations(
    snippet: str,
    name: str,
    expected_types: frozenset[TypeInfo],
) -> None:
    result = analyze_python_statement_types(snippet)

    assert result.has_unsupported_features is False
    assert result.name_types[name] == expected_types


def test_analyze_python_statement_types_invalid_unary_numeric_operation_has_no_type() -> None:
    snippet = "x = -'some string'"

    result = analyze_python_statement_types(snippet)

    assert result.has_unsupported_features is False
    assert result.name_types["x"] == _fs()


def test_analyze_python_statement_types_invalid_invert_on_float_has_no_type() -> None:
    snippet = "x = ~1.5"

    result = analyze_python_statement_types(snippet)

    assert result.has_unsupported_features is False
    assert result.name_types["x"] == _fs()


def test_analyze_python_statement_types_boolop_and_compare() -> None:
    snippet = "x = a and b\ny = left < right"

    result = analyze_python_statement_types(snippet)

    assert result.name_types["x"] == _fs(UnknownType)
    assert result.name_types["y"] == _fs(UnknownType)


def test_analyze_python_statement_types_compare_valid_and_invalid_cases() -> None:
    snippet = "a = 1 < 2\nb = 1 < 'x'\nc = 'a' in ['a', 'b']\nd = 1 in 'abc'"

    result = analyze_python_statement_types(snippet)

    assert result.name_types["a"] == _fs(_s(bool))
    assert result.name_types["b"] == _fs()
    assert result.name_types["c"] == _fs(_s(bool))
    assert result.name_types["d"] == _fs()


def test_analyze_python_statement_types_chained_compare_impossible_link_overrides_unknown() -> None:
    snippet = "x = left < 1 < 'z'"

    result = analyze_python_statement_types(snippet)

    assert result.name_types["x"] == _fs()


def test_analyze_python_statement_types_container_literals() -> None:
    snippet = "a = (1, 'x')\nb = [1, 2]\nc = {1, 2}\nd = {'k': 1}"

    result = analyze_python_statement_types(snippet)

    assert result.name_types["a"] == _fs(TupleOf((frozenset({_s(int)}), frozenset({_s(str)}))))
    assert result.name_types["b"] == _fs(ListOf(frozenset({_s(int)})))
    assert result.name_types["c"] == _fs(SetOf(frozenset({_s(int)})))
    assert result.name_types["d"] == _fs(DictOf(frozenset({_s(str)}), frozenset({_s(int)})))


def test_analyze_python_statement_types_attribute_is_unknown_and_subscript_can_be_precise() -> None:
    snippet = "a = [1, 2.0]\nb = a[0]\nx = obj.attr"

    result = analyze_python_statement_types(snippet)

    assert result.name_types["a"] == _fs(ListOf(frozenset({_s(int), _s(float)})))
    assert result.name_types["b"] == _fs(_s(int), _s(float))
    assert result.name_types["x"] == _fs(UnknownType)


def test_analyze_python_statement_types_multi_target_assignment() -> None:
    snippet = "x = y = 1"

    result = analyze_python_statement_types(snippet)

    assert result.name_types["x"] == _fs(_s(int))
    assert result.name_types["y"] == _fs(_s(int))


def test_analyze_python_statement_types_precise_destructuring_from_literal_tuple() -> None:
    snippet = "x, y = (1, 'a')"

    result = analyze_python_statement_types(snippet)

    assert result.name_types["x"] == _fs(_s(int))
    assert result.name_types["y"] == _fs(_s(str))


def test_analyze_python_statement_types_annotation_without_value_defaults_to_unknown() -> None:
    snippet = "x: int"

    result = analyze_python_statement_types(snippet)

    assert result.has_unsupported_features is False
    assert result.name_types["x"] == _fs(UnknownType)


def test_analyze_python_statement_types_unknown_from_call_is_local() -> None:
    snippet = "x = f(1)\ny = 1\nz = y + 2"

    result = analyze_python_statement_types(snippet)

    assert result.name_types["x"] == _fs(UnknownType)
    assert result.name_types["y"] == _fs(_s(int))
    assert result.name_types["z"] == _fs(_s(int))


def test_analyze_python_statement_types_unsupported_is_local() -> None:
    snippet = "x = f(**k)\ny = 1\nz = y + 2"

    result = analyze_python_statement_types(snippet)

    assert result.has_unsupported_features is True
    assert result.unsupported_witness == "**k"
    assert result.name_types["x"] == _fs(UnknownType)
    assert result.name_types["y"] == _fs(_s(int))
    assert result.name_types["z"] == _fs(_s(int))


def test_analyze_python_statement_types_merges_if_branches() -> None:
    snippet = "if cond:\n    a = 1\nelse:\n    a = 'x'"

    result = analyze_python_statement_types(snippet)

    assert result.name_types["a"] == _fs(_s(int), _s(str))


def test_analyze_python_statement_types_while_else_merges_paths() -> None:
    snippet = "while cond:\n    x = 1\nelse:\n    x = 'done'"

    result = analyze_python_statement_types(snippet)

    assert result.has_unsupported_features is False
    assert result.name_types["x"] == _fs(_s(int), _s(str))


def test_analyze_python_statement_types_for_else_merges_paths() -> None:
    snippet = "for item in items:\n    x = 1\nelse:\n    x = 'done'"

    result = analyze_python_statement_types(snippet)

    assert result.has_unsupported_features is False
    assert result.name_types["item"] == _fs(UnknownType)
    assert result.name_types["x"] == _fs(_s(int), _s(str))


def test_analyze_python_statement_types_list_concat_keeps_constituent_types() -> None:
    snippet = "x = [1] + [2.0]"

    result = analyze_python_statement_types(snippet)

    assert result.name_types["x"] == _fs(ListOf(frozenset({_s(int), _s(float)})))


def test_analyze_python_statement_types_tuple_and_dict_subscript_inference() -> None:
    snippet = "t = (1, 'a')\nx = t[1]\nd = {'k': 5}\ny = d['k']"

    result = analyze_python_statement_types(snippet)

    assert result.name_types["x"] == _fs(_s(str))
    assert result.name_types["y"] == _fs(_s(int))


def test_analyze_python_statement_types_repeated_tuple_annotation_preserves_repeat_information() -> None:
    def pick(values: tuple[int, ...]) -> int:
        return values[0]

    result = analyze_python_statement_types("f = pick", {"pick": pick}, None)

    assert result.has_unsupported_features is False
    assert result.name_types["f"] == _fs(FunctionType((_fs(RepeatedTupleOf((_fs(_s(int)),))),), _fs(_s(int))))


def test_analyze_python_statement_types_repeated_tuple_pattern_annotation_preserves_pattern_information() -> None:
    repeated_pattern_annotation = tuple[str, int, float, ...]

    inferred = _annotation_to_types(repeated_pattern_annotation)

    assert inferred == _fs(RepeatedTupleOf((_fs(_s(str)), _fs(_s(int)), _fs(_s(float)))))


def test_analyze_python_statement_types_repeated_tuple_subscript_out_of_pattern_range_uses_last_pattern_type() -> None:
    snippet = "x = values[4]"
    local_types = {
        "values": _fs(RepeatedTupleOf((_fs(_s(str)), _fs(_s(int)), _fs(_s(float))))),
    }

    result = analyze_python_statement_types(snippet, None, local_types)

    assert result.has_unsupported_features is False
    assert result.name_types["x"] == _fs(_s(float))


def test_analyze_python_statement_types_global_math_function_call_infers_float() -> None:
    snippet = "x = math.sqrt(9)"

    result = analyze_python_statement_types(snippet, {"math": math}, None)

    assert result.has_unsupported_features is False
    assert result.name_types["x"] == _fs(_s(float))


def test_analyze_python_statement_types_global_annotated_callable_infers_return_type() -> None:
    def stringify(value: int) -> str:
        return str(value)

    snippet = "x = stringify(3)"

    result = analyze_python_statement_types(snippet, {"stringify": stringify}, None)

    assert result.has_unsupported_features is False
    assert result.name_types["x"] == _fs(_s(str))


def test_analyze_python_statement_types_global_callable_name_infers_function_type() -> None:
    def stringify(value: int) -> str:
        return str(value)

    snippet = "f = stringify"

    result = analyze_python_statement_types(snippet, {"stringify": stringify}, None)

    assert result.has_unsupported_features is False
    assert result.name_types["f"] == _fs(FunctionType((_fs(_s(int)),), _fs(_s(str))))


def test_analyze_python_statement_types_global_math_callable_name_infers_function_type() -> None:
    snippet = "f = math.sqrt"

    result = analyze_python_statement_types(snippet, {"math": math}, None)

    assert result.has_unsupported_features is False
    assert result.name_types["f"] == _fs(FunctionType((_fs(_s(int), _s(float)),), _fs(_s(float))))


@pytest.mark.parametrize(
    ("snippet", "expected_types"),
    [
        (
            "f = math.atan2",
            _fs(FunctionType((_fs(_s(int), _s(float)), _fs(_s(int), _s(float))), _fs(_s(float)))),
        ),
        (
            "f = math.ldexp",
            _fs(FunctionType((_fs(_s(int), _s(float)), _fs(_s(int))), _fs(_s(float)))),
        ),
        (
            "f = math.factorial",
            _fs(FunctionType((_fs(_s(int)),), _fs(_s(int)))),
        ),
    ],
)
def test_analyze_python_statement_types_precise_math_function_signatures(
    snippet: str,
    expected_types: frozenset[TypeInfo],
) -> None:
    result = analyze_python_statement_types(snippet, {"math": math}, None)

    assert result.has_unsupported_features is False
    assert result.name_types["f"] == expected_types
