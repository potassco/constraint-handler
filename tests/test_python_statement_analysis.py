from __future__ import annotations

import builtins
import math
import typing

import pytest

from constraint_handler.utils.python_statement_analysis import (
    analyze_python_statement_types,
)
from constraint_handler.utils.python_type_model import (
    DictOf,
    FunctionType,
    ListOf,
    RepeatedTupleOf,
    Scalar,
    SetOf,
    TupleOf,
    TypeInfo,
    UnknownType,
    UnsupportedType,
)


def _s(t: type) -> Scalar:
    return Scalar(t)


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

    assert result.unsupported_events == ()
    assert set(result.name_types) == expected_names


def test_analyze_python_statement_types_expression_statement_call_is_flagged() -> None:
    snippet = "f(1)\nx = 2"

    result = analyze_python_statement_types(snippet)

    assert result.unsupported_events == (("f(1)", "unsupported statement: Expr"),)
    assert result.name_types["x"] == _fs(_s(int))


def test_analyze_python_statement_types_rejects_star_args_call() -> None:
    snippet = "x = f(*args)"

    result = analyze_python_statement_types(snippet)

    assert result.unsupported_events == (("f(*args)", "unsupported expression: positional/keyword unpacking"),)
    assert result.name_types["x"] == _fs(UnknownType)


def test_analyze_python_statement_types_rejects_kw_unpack_call() -> None:
    snippet = "x = f(**kwargs)"

    result = analyze_python_statement_types(snippet)

    assert result.unsupported_events == (("f(**kwargs)", "unsupported expression: positional/keyword unpacking"),)
    assert result.name_types["x"] == _fs(UnknownType)


def test_analyze_python_statement_types_collects_multiple_unsupported_events() -> None:
    snippet = "x = f(*args)\ny = g(**kwargs)"

    result = analyze_python_statement_types(snippet)

    assert result.unsupported_events == (
        ("f(*args)", "unsupported expression: positional/keyword unpacking"),
        ("g(**kwargs)", "unsupported expression: positional/keyword unpacking"),
    )


def test_analyze_python_statement_types_rejects_lambda_callee() -> None:
    snippet = "x = (lambda y: y)(1)"

    result = analyze_python_statement_types(snippet)

    assert result.unsupported_events == (("lambda y: y", "unsupported expression: callable form"),)
    assert result.name_types["x"] == _fs(UnknownType)


def test_analyze_python_statement_types_syntax_error() -> None:
    result = analyze_python_statement_types("x =")

    assert result.name_types == {}
    assert result.unsupported_events == (("x =", "syntax error"),)


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

    assert result.unsupported_events == ()
    assert result.name_types["w"] == _fs(_s(float), _s(str))


def test_analyze_python_statement_types_division_result_is_float() -> None:
    snippet = "x = 1 / 2"

    result = analyze_python_statement_types(snippet)

    assert result.unsupported_events == ()
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

    assert result.unsupported_events == ()
    assert result.name_types["x"] == expected_types


@pytest.mark.parametrize(
    "snippet",
    [
        "x = True + True",
        "x = 1 + True",
        "x = True << 1",
    ],
)
def test_analyze_python_statement_types_bool_works_in_int_operator_positions(
    snippet: str,
) -> None:
    result = analyze_python_statement_types(snippet)

    assert result.unsupported_events == ()
    assert result.name_types["x"] == _fs(_s(int))


@pytest.mark.parametrize(
    ("snippet", "expected_types"),
    [
        ("x = math.floor(True)", _fs(_s(int))),
        ("x = math.sqrt(True)", _fs(_s(float))),
        ("x = math.factorial(True)", _fs(_s(int))),
    ],
)
def test_analyze_python_statement_types_bool_works_in_math_numeric_positions(
    snippet: str,
    expected_types: frozenset[TypeInfo],
) -> None:
    result = analyze_python_statement_types(snippet, {"math": math}, None)

    assert result.unsupported_events == ()
    assert result.name_types["x"] == expected_types


@pytest.mark.parametrize(
    ("snippet", "expected_types"),
    [
        ("x = True & True", _fs(_s(bool))),
        ("x = True | False", _fs(_s(bool))),
        ("x = True ^ True", _fs(_s(bool))),
        ("x = True & 2", _fs(_s(int))),
        ("x = 1 | False", _fs(_s(int))),
    ],
)
def test_analyze_python_statement_types_bitwise_bool_results_follow_python(
    snippet: str,
    expected_types: frozenset[TypeInfo],
) -> None:
    result = analyze_python_statement_types(snippet)

    assert result.unsupported_events == ()
    assert result.name_types["x"] == expected_types


@pytest.mark.parametrize(
    "snippet",
    [
        "x = True & y",
        "x = y | False",
        "x = y ^ True",
    ],
)
def test_analyze_python_statement_types_bitwise_bool_with_unknown_can_be_bool_or_int(
    snippet: str,
) -> None:
    result = analyze_python_statement_types(snippet)

    assert result.unsupported_events == ()
    assert result.name_types["x"] == _fs(_s(bool), _s(int))


def test_analyze_python_statement_types_numeric_matmul_is_unknown() -> None:
    snippet = "x = 1 @ 2"

    result = analyze_python_statement_types(snippet)

    assert result.unsupported_events == ()
    assert result.name_types["x"] == _fs()


@pytest.mark.parametrize(
    ("snippet", "name", "expected_types"),
    [
        ("x = -1", "x", _fs(_s(int))),
        ("x = +1.5", "x", _fs(_s(float))),
        ("x = ~1", "x", _fs(_s(int))),
        ("x = not True", "x", _fs(_s(bool))),
        ("x = not flag", "x", _fs(_s(bool))),
    ],
)
def test_analyze_python_statement_types_unary_operations(
    snippet: str,
    name: str,
    expected_types: frozenset[TypeInfo],
) -> None:
    result = analyze_python_statement_types(snippet)

    assert result.unsupported_events == ()
    assert result.name_types[name] == expected_types


def test_analyze_python_statement_types_invalid_unary_numeric_operation_has_no_type() -> None:
    snippet = "x = -'some string'"

    result = analyze_python_statement_types(snippet)

    assert result.unsupported_events == ()
    assert result.name_types["x"] == _fs()


def test_analyze_python_statement_types_invalid_invert_on_float_has_no_type() -> None:
    snippet = "x = ~1.5"

    result = analyze_python_statement_types(snippet)

    assert result.unsupported_events == ()
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


def test_analyze_python_statement_types_set_equality_with_unknown_input_extracts_bool() -> None:
    snippet = "result = set(x) == set([])\n__ch_expr = result"
    local_types = {
        "x": _fs(SetOf(UnknownType)),
    }

    result = analyze_python_statement_types(snippet, None, local_types)

    assert result.unsupported_events == ()
    assert result.name_types["result"] == _fs(_s(bool))
    assert result.name_types["__ch_expr"] == _fs(_s(bool))


def test_analyze_python_statement_types_set_equality_with_empty_dict_literal_extracts_bool() -> None:
    snippet = "result = set(x) == set({})\n__ch_expr = result"
    local_types = {
        "x": _fs(SetOf(UnknownType)),
    }

    result = analyze_python_statement_types(snippet, None, local_types)

    assert result.unsupported_events == ()
    assert result.name_types["result"] == _fs(_s(bool))
    assert result.name_types["__ch_expr"] == _fs(_s(bool))


def test_analyze_python_statement_types_dict_equality_with_empty_dict_literal_extracts_bool() -> None:
    snippet = "result = dict(x) == dict({})\n__ch_expr = result"
    local_types = {
        "x": _fs(DictOf(UnknownType, UnknownType)),
    }

    result = analyze_python_statement_types(snippet, None, local_types)

    assert result.unsupported_events == ()
    assert result.name_types["result"] == _fs(_s(bool))
    assert result.name_types["__ch_expr"] == _fs(_s(bool))


def test_analyze_python_statement_types_container_literals() -> None:
    snippet = "a = (1, 'x')\nb = [1, 2]\nc = {1, 2}\nd = {'k': 1}"

    result = analyze_python_statement_types(snippet)

    assert result.name_types["a"] == _fs(TupleOf((_s(int), _s(str))))
    assert result.name_types["b"] == _fs(ListOf(_s(int)))
    assert result.name_types["c"] == _fs(SetOf(_s(int)))
    assert result.name_types["d"] == _fs(DictOf(_s(str), _s(int)))


def test_analyze_python_statement_types_attribute_is_unknown_and_subscript_can_be_precise() -> None:
    snippet = "a = [1, 2.0]\nb = a[0]\nx = obj.attr"

    result = analyze_python_statement_types(snippet)

    assert result.name_types["a"] == _fs(ListOf(_s(int)), ListOf(_s(float)))
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

    assert result.unsupported_events == ()
    assert result.name_types["x"] == _fs(UnknownType)


def test_analyze_python_statement_types_unknown_from_call_is_local() -> None:
    snippet = "x = f(1)\ny = 1\nz = y + 2"

    result = analyze_python_statement_types(snippet)

    assert result.name_types["x"] == _fs()
    assert result.name_types["y"] == _fs(_s(int))
    assert result.name_types["z"] == _fs(_s(int))


def test_analyze_python_statement_types_unsupported_is_local() -> None:
    snippet = "x = f(**k)\ny = 1\nz = y + 2"

    result = analyze_python_statement_types(snippet)

    assert result.unsupported_events == (("f(**k)", "unsupported expression: positional/keyword unpacking"),)
    assert result.name_types["x"] == _fs(UnknownType)
    assert result.name_types["y"] == _fs(_s(int))
    assert result.name_types["z"] == _fs(_s(int))


def test_analyze_python_statement_types_builtin_object_call_is_unsupported_type() -> None:
    snippet = "x = object()"

    result = analyze_python_statement_types(snippet)

    assert result.unsupported_events == ()
    assert result.name_types["x"] == _fs(UnsupportedType)


def test_analyze_python_statement_types_builtin_len_call_infers_int() -> None:
    snippet = "x = len(values)"

    result = analyze_python_statement_types(snippet)

    assert result.unsupported_events == ()
    assert result.name_types["x"] == _fs(_s(int))


def test_analyze_python_statement_types_sum_over_list_literal_infers_int() -> None:
    snippet = "l = [1,2,3]\nx = sum(l)"

    result = analyze_python_statement_types(snippet)

    assert result.unsupported_events == ()
    assert result.name_types["l"] == _fs(ListOf(_s(int)))
    assert result.name_types["x"] == _fs(_s(int))


def test_analyze_python_statement_types_sum_over_bool_list_literal_infers_int() -> None:
    snippet = "l = [True, False]\nx = sum(l)"

    result = analyze_python_statement_types(snippet)

    assert result.unsupported_events == ()
    assert result.name_types["l"] == _fs(ListOf(_s(bool)))
    assert result.name_types["x"] == _fs(_s(int))


def test_analyze_python_statement_types_builtin_signatures_infer_expected_types() -> None:
    snippet = (
        "a = abs(v)\n"
        "b = all(values)\n"
        "c = any(values)\n"
        "d = bool(v)\n"
        "e = chr(code)\n"
        "f = dict(items)\n"
        "g = float(v)\n"
        "h = hash(v)\n"
        "i = int(v)\n"
        "j = list(values)\n"
        "k = ord(ch)\n"
        "l = set(values)\n"
        "m = str(v)"
    )

    result = analyze_python_statement_types(snippet)

    assert result.unsupported_events == ()
    assert result.name_types["a"] == _fs(_s(int), _s(float))
    assert result.name_types["b"] == _fs(_s(bool))
    assert result.name_types["c"] == _fs(_s(bool))
    assert result.name_types["d"] == _fs(_s(bool))
    assert result.name_types["e"] == _fs(_s(str))
    assert result.name_types["f"] == _fs(DictOf(UnknownType, UnknownType))
    assert result.name_types["g"] == _fs(_s(float))
    assert result.name_types["h"] == _fs(_s(int))
    assert result.name_types["i"] == _fs(_s(int))
    assert result.name_types["j"] == _fs(ListOf(UnknownType))
    assert result.name_types["k"] == _fs(_s(int))
    assert result.name_types["l"] == _fs(SetOf(UnknownType))
    assert result.name_types["m"] == _fs(_s(str))


def test_analyze_python_statement_types_list_set_scalar_collection_inference() -> None:
    snippet = "x = list(values)\ny = set(values)"
    local_types = {"values": _fs(ListOf(_s(int)), ListOf(_s(float)))}

    result = analyze_python_statement_types(snippet, None, local_types)

    assert result.unsupported_events == ()
    assert result.name_types["x"] == _fs(ListOf(_s(int)), ListOf(_s(float)))
    assert result.name_types["y"] == _fs(SetOf(_s(int)), SetOf(_s(float)))


def test_analyze_python_statement_types_dict_scalar_collection_inference() -> None:
    snippet = "d1 = dict(mapping)\nd2 = dict(pairs)"
    local_types = {
        "mapping": _fs(DictOf(_s(str), _s(int)), DictOf(_s(str), _s(bool))),
        "pairs": _fs(ListOf(TupleOf((_s(str), _s(float))))),
    }

    result = analyze_python_statement_types(snippet, None, local_types)

    assert result.unsupported_events == ()
    assert result.name_types["d1"] == _fs(DictOf(_s(str), _s(int)), DictOf(_s(str), _s(bool)))
    assert result.name_types["d2"] == _fs(DictOf(_s(str), _s(float)))


def test_analyze_python_statement_types_collection_constructor_non_scalar_uses_fallback() -> None:
    snippet = "x = list(values)"
    local_types = {
        "values": _fs(ListOf(ListOf(_s(int)))),
    }

    result = analyze_python_statement_types(snippet, None, local_types)

    assert result.unsupported_events == ()
    assert result.name_types["x"] == _fs(ListOf(UnknownType))


def test_analyze_python_statement_types_merges_if_branches() -> None:
    snippet = "if cond:\n    a = 1\nelse:\n    a = 'x'"

    result = analyze_python_statement_types(snippet)

    assert result.name_types["a"] == _fs(_s(int), _s(str))


def test_analyze_python_statement_types_while_else_merges_paths() -> None:
    snippet = "while cond:\n    x = 1\nelse:\n    x = 'done'"

    result = analyze_python_statement_types(snippet)

    assert result.unsupported_events == ()
    assert result.name_types["x"] == _fs(_s(int), _s(str))


def test_analyze_python_statement_types_for_else_merges_paths() -> None:
    snippet = "for item in items:\n    x = 1\nelse:\n    x = 'done'"

    result = analyze_python_statement_types(snippet)

    assert result.unsupported_events == ()
    assert result.name_types["item"] == _fs(UnknownType)
    assert result.name_types["x"] == _fs(_s(int), _s(str))


def test_analyze_python_statement_types_list_concat_keeps_constituent_types() -> None:
    snippet = "x = [1] + [2.0]"

    result = analyze_python_statement_types(snippet)

    assert result.name_types["x"] == _fs(ListOf(_s(int)), ListOf(_s(float)))


def test_analyze_python_statement_types_tuple_and_dict_subscript_inference() -> None:
    snippet = "t = (1, 'a')\nx = t[1]\nd = {'k': 5}\ny = d['k']"

    result = analyze_python_statement_types(snippet)

    assert result.name_types["x"] == _fs(_s(str))
    assert result.name_types["y"] == _fs(_s(int))


def test_analyze_python_statement_types_repeated_tuple_annotation_preserves_repeat_information() -> None:
    def pick(values: tuple[int, ...]) -> int:
        return values[0]

    result = analyze_python_statement_types("f = pick", {"pick": pick}, None)

    assert result.unsupported_events == ()
    assert result.name_types["f"] == _fs(FunctionType((RepeatedTupleOf(_s(int)),), _s(int)))


def test_analyze_python_statement_types_repeated_tuple_subscript_infers_repeated_element_type() -> None:
    snippet = "x = values[4]"
    local_types = {
        "values": _fs(RepeatedTupleOf(_s(float))),
    }

    result = analyze_python_statement_types(snippet, None, local_types)

    assert result.unsupported_events == ()
    assert result.name_types["x"] == _fs(_s(float))


def test_analyze_python_statement_types_global_math_function_call_infers_float() -> None:
    snippet = "x = math.sqrt(9)"

    result = analyze_python_statement_types(snippet, {"math": math}, None)

    assert result.unsupported_events == ()
    assert result.name_types["x"] == _fs(_s(float))


def test_analyze_python_statement_types_global_builtins_function_call_uses_module_signature() -> None:
    snippet = "x = builtins.len(values)"

    result = analyze_python_statement_types(snippet, {"builtins": builtins}, None)

    assert result.unsupported_events == ()
    assert result.name_types["x"] == _fs(_s(int))


def test_analyze_python_statement_types_static_math_attribute_call_infers_float_without_runtime_global() -> None:
    snippet = "x = math.sqrt(9)"

    result = analyze_python_statement_types(snippet)

    assert result.unsupported_events == ()
    assert result.name_types["x"] == _fs()


def test_analyze_python_statement_types_indirect_and_direct_sqrt_unknown_arg_infer_float() -> None:
    snippet = "f = math.sqrt\na = f(x)\nb = math.sqrt(x)"

    result = analyze_python_statement_types(snippet, {"math": math}, None)

    assert result.unsupported_events == ()
    assert result.name_types["a"] == _fs(_s(float))
    assert result.name_types["b"] == _fs(_s(float))


def test_analyze_python_statement_types_global_annotated_callable_infers_return_type() -> None:
    def stringify(value: int) -> str:
        return str(value)

    snippet = "x = stringify(3)"

    result = analyze_python_statement_types(snippet, {"stringify": stringify}, None)

    assert result.unsupported_events == ()
    assert result.name_types["x"] == _fs(_s(str))


def test_analyze_python_statement_types_global_callable_name_infers_function_type() -> None:
    def stringify(value: int) -> str:
        return str(value)

    snippet = "f = stringify"

    result = analyze_python_statement_types(snippet, {"stringify": stringify}, None)

    assert result.unsupported_events == ()
    assert result.name_types["f"] == _fs(FunctionType((_s(int),), _s(str)))


def test_analyze_python_statement_types_global_callable_annotation_expands_function_type() -> None:
    def apply_predicate(predicate: typing.Callable[[int, float], bool]) -> bool:
        return predicate(1, 2.0)

    def is_positive(left: int, right: float) -> bool:
        return left < right

    snippet = "f = apply_predicate\nx = f(is_positive)\ny = apply_predicate(is_positive)"

    result = analyze_python_statement_types(
        snippet,
        {
            "apply_predicate": apply_predicate,
            "is_positive": is_positive,
        },
        None,
    )

    assert result.unsupported_events == ()
    assert result.name_types["f"] == _fs(FunctionType((FunctionType((_s(int), _s(float)), _s(bool)),), _s(bool)))
    assert result.name_types["x"] == _fs(_s(bool))
    assert result.name_types["y"] == _fs(_s(bool))


def test_analyze_python_statement_types_global_math_callable_name_infers_function_type() -> None:
    snippet = "f = math.sqrt"

    result = analyze_python_statement_types(snippet, {"math": math}, None)

    assert result.unsupported_events == ()
    assert result.name_types["f"] == _fs(
        FunctionType((_s(bool),), _s(float)),
        FunctionType((_s(int),), _s(float)),
        FunctionType((_s(float),), _s(float)),
        FunctionType((UnknownType,), _s(float)),
    )


def test_analyze_python_statement_types_known_input_unknown_return_should_use_static_overloads() -> None:
    class SqrtProxy:
        __module__ = "math"
        __name__ = "sqrt"

        def __call__(self, value: int):
            return value

    # Force a runtime-resolved annotation object (not a deferred string) so the input is truly known.
    SqrtProxy.__call__.__annotations__ = {"value": int}

    snippet = "f = proxy"
    result = analyze_python_statement_types(snippet, {"proxy": SqrtProxy()}, None)

    assert result.unsupported_events == ()
    # This exposes the current gap: known input + unknown return should still use static overloads.
    assert result.name_types["f"] == _fs(
        FunctionType((_s(bool),), _s(float)),
        FunctionType((_s(int),), _s(float)),
        FunctionType((_s(float),), _s(float)),
        FunctionType((UnknownType,), _s(float)),
    )


@pytest.mark.parametrize(
    ("snippet", "expected_types"),
    [
        (
            "f = math.atan2",
            _fs(
                FunctionType((_s(bool), _s(bool)), _s(float)),
                FunctionType((_s(bool), _s(int)), _s(float)),
                FunctionType((_s(bool), _s(float)), _s(float)),
                FunctionType((_s(bool), UnknownType), _s(float)),
                FunctionType((_s(int), _s(bool)), _s(float)),
                FunctionType((_s(int), _s(int)), _s(float)),
                FunctionType((_s(int), _s(float)), _s(float)),
                FunctionType((_s(int), UnknownType), _s(float)),
                FunctionType((_s(float), _s(bool)), _s(float)),
                FunctionType((_s(float), _s(int)), _s(float)),
                FunctionType((_s(float), _s(float)), _s(float)),
                FunctionType((_s(float), UnknownType), _s(float)),
                FunctionType((UnknownType, _s(bool)), _s(float)),
                FunctionType((UnknownType, _s(int)), _s(float)),
                FunctionType((UnknownType, _s(float)), _s(float)),
                FunctionType((UnknownType, UnknownType), _s(float)),
            ),
        ),
        (
            "f = math.ldexp",
            _fs(
                FunctionType((_s(bool), _s(bool)), _s(float)),
                FunctionType((_s(bool), _s(int)), _s(float)),
                FunctionType((_s(bool), UnknownType), _s(float)),
                FunctionType((_s(int), _s(bool)), _s(float)),
                FunctionType((_s(int), _s(int)), _s(float)),
                FunctionType((_s(int), UnknownType), _s(float)),
                FunctionType((_s(float), _s(bool)), _s(float)),
                FunctionType((_s(float), _s(int)), _s(float)),
                FunctionType((_s(float), UnknownType), _s(float)),
                FunctionType((UnknownType, _s(bool)), _s(float)),
                FunctionType((UnknownType, _s(int)), _s(float)),
                FunctionType((UnknownType, UnknownType), _s(float)),
            ),
        ),
        (
            "f = math.factorial",
            _fs(
                FunctionType((_s(bool),), _s(int)),
                FunctionType((_s(int),), _s(int)),
                FunctionType((UnknownType,), _s(int)),
            ),
        ),
    ],
)
def test_analyze_python_statement_types_precise_math_function_signatures(
    snippet: str,
    expected_types: frozenset[TypeInfo],
) -> None:
    result = analyze_python_statement_types(snippet, {"math": math}, None)

    assert result.unsupported_events == ()
    assert result.name_types["f"] == expected_types
