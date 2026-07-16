"""Declarative function signatures for Python statement analysis."""

from __future__ import annotations

import ast
import itertools

from constraint_handler.utils.python_type_model import (
    DictOf,
    FunctionType,
    ListOf,
    Scalar,
    SetOf,
    TupleOf,
    TypeInfo,
    UnknownType,
    UnsupportedType,
)

_INT = (Scalar.BOOL, Scalar.INT, UnknownType)
_FLOAT = (Scalar.FLOAT, UnknownType)
_BOOL = (Scalar.BOOL, UnknownType)
_NUMERIC = (Scalar.BOOL, Scalar.INT, Scalar.FLOAT, UnknownType)


_NUMERIC_BINARY = (
    frozenset(FunctionType((left_type, right_type), Scalar.INT) for left_type in _INT for right_type in _INT)
    | frozenset(FunctionType((left_type, right_type), Scalar.FLOAT) for left_type in _FLOAT for right_type in _NUMERIC)
    | frozenset(FunctionType((left_type, right_type), Scalar.FLOAT) for left_type in _NUMERIC for right_type in _FLOAT)
)
_NUMERIC_NUMERIC_TO_FLOAT = frozenset(
    FunctionType((left_type, right_type), Scalar.FLOAT) for left_type in _NUMERIC for right_type in _NUMERIC
)
_NUMERIC_NUMERIC_TO_BOOL = frozenset(
    FunctionType((left_type, right_type), Scalar.BOOL) for left_type in _NUMERIC for right_type in _NUMERIC
)
_NUMERIC_INT_TO_FLOAT = frozenset(
    FunctionType((left_type, right_type), Scalar.FLOAT) for left_type in _NUMERIC for right_type in _INT
)
_NUMERIC_NUMERIC_NUMERIC_TO_BOOL = frozenset(
    FunctionType((first_type, second_type, third_type), Scalar.BOOL)
    for first_type in _NUMERIC
    for second_type in _NUMERIC
    for third_type in _NUMERIC
)
_NUMERIC_NUMERIC_NUMERIC_NUMERIC_TO_BOOL = frozenset(
    FunctionType((first_type, second_type, third_type, fourth_type), Scalar.BOOL)
    for first_type in _NUMERIC
    for second_type in _NUMERIC
    for third_type in _NUMERIC
    for fourth_type in _NUMERIC
)
_NUMERIC_TO_FLOAT = frozenset(FunctionType((input_type,), Scalar.FLOAT) for input_type in _NUMERIC)
_NUMERIC_TO_INT = frozenset(FunctionType((input_type,), Scalar.INT) for input_type in _NUMERIC)
_INT_TO_INT = frozenset(FunctionType((input_type,), Scalar.INT) for input_type in _INT)
_FLOAT_TO_FLOAT = frozenset(FunctionType((input_type,), Scalar.FLOAT) for input_type in _FLOAT)
_BOOL_TO_INT = frozenset(FunctionType((input_type,), Scalar.INT) for input_type in _BOOL)
_NUMERIC_TO_BOOL = frozenset(FunctionType((input_type,), Scalar.BOOL) for input_type in _NUMERIC)
_NUMERIC_NUMERIC_INT_TO_FLOAT = frozenset(
    FunctionType((left_type, right_type, step_type), Scalar.FLOAT)
    for left_type in _NUMERIC
    for right_type in _NUMERIC
    for step_type in _INT
)
_INT_INT_TO_INT = frozenset(
    FunctionType((left_type, right_type), Scalar.INT) for left_type in _INT for right_type in _INT
)
_BITWISE_BINARY = frozenset(
    {
        FunctionType((Scalar.BOOL, Scalar.BOOL), Scalar.BOOL),
        FunctionType((Scalar.BOOL, UnknownType), Scalar.BOOL),
        FunctionType((UnknownType, Scalar.BOOL), Scalar.BOOL),
        FunctionType((UnknownType, UnknownType), Scalar.BOOL),
    }
) | frozenset(
    FunctionType((left_type, right_type), Scalar.INT)
    for left_type in _INT
    for right_type in _INT
    if (left_type, right_type) != (Scalar.BOOL, Scalar.BOOL)
)

_SCALAR_TYPES = (Scalar.BOOL, Scalar.INT, Scalar.FLOAT, Scalar.STRING, Scalar.NONE)
_SCALAR = _SCALAR_TYPES + (UnknownType,)
_LIST_ADD_BINARY = tuple(
    FunctionType(
        (
            ListOf(left_element_type),
            ListOf(right_element_type),
        ),
        ListOf(result_element_type),
    )
    for left_element_type in _SCALAR
    for right_element_type in _SCALAR
    for result_element_type in {left_element_type, right_element_type}
)
_SUM_FUNCTION = frozenset(
    {
        FunctionType((ListOf(Scalar.BOOL),), Scalar.INT),
        FunctionType((SetOf(Scalar.BOOL),), Scalar.INT),
    }
) | frozenset(
    FunctionType((source_shape,), result_type)
    for result_type in (Scalar.INT, Scalar.FLOAT, UnknownType)
    for source_shape in (ListOf(result_type), SetOf(result_type))
)

CONSTRUCTOR_FUNCTION = {
    "list": frozenset(
        FunctionType((source_shape,), ListOf(scalar_type))
        for scalar_type in _SCALAR_TYPES
        for source_shape in (ListOf(scalar_type), SetOf(scalar_type))
    )
    | frozenset({FunctionType((Scalar.STRING,), ListOf(Scalar.STRING))}),
    "set": frozenset(
        FunctionType((source_shape,), SetOf(scalar_type))
        for scalar_type in _SCALAR_TYPES
        for source_shape in (ListOf(scalar_type), SetOf(scalar_type))
    )
    | frozenset({FunctionType((Scalar.STRING,), SetOf(Scalar.STRING))}),
    "dict": frozenset(
        FunctionType((source_shape,), DictOf(key_type, value_type))
        for key_type in _SCALAR_TYPES
        for value_type in _SCALAR_TYPES
        for source_shape in (
            DictOf(key_type, value_type),
            ListOf(TupleOf((key_type, value_type))),
            SetOf(TupleOf((key_type, value_type))),
        )
    ),
}

BUILTIN_FUNCTION = {
    "abs": _INT_TO_INT | _FLOAT_TO_FLOAT,
    "all": frozenset({FunctionType(None, Scalar.BOOL)}),
    "any": frozenset({FunctionType(None, Scalar.BOOL)}),
    "bool": frozenset({FunctionType(None, Scalar.BOOL)}),
    "chr": frozenset({FunctionType(None, Scalar.STRING)}),
    "dict": CONSTRUCTOR_FUNCTION["dict"] | frozenset({FunctionType(None, DictOf(UnknownType, UnknownType))}),
    "float": frozenset({FunctionType(None, Scalar.FLOAT)}),
    "hash": frozenset({FunctionType(None, Scalar.INT)}),
    "int": frozenset({FunctionType(None, Scalar.INT)}),
    "len": frozenset({FunctionType(None, Scalar.INT)}),
    "list": CONSTRUCTOR_FUNCTION["list"] | frozenset({FunctionType(None, ListOf(UnknownType))}),
    "ord": frozenset({FunctionType(None, Scalar.INT)}),
    "object": frozenset({FunctionType(None, UnsupportedType)}),
    "set": CONSTRUCTOR_FUNCTION["set"] | frozenset({FunctionType(None, SetOf(UnknownType))}),
    "str": frozenset({FunctionType(None, Scalar.STRING)}),
    "sum": _SUM_FUNCTION,
}

MATH_UNARY_FUNCTION = {
    "acos": _NUMERIC_TO_FLOAT,
    "acosh": _NUMERIC_TO_FLOAT,
    "asin": _NUMERIC_TO_FLOAT,
    "asinh": _NUMERIC_TO_FLOAT,
    "atan": _NUMERIC_TO_FLOAT,
    "atanh": _NUMERIC_TO_FLOAT,
    "cbrt": _NUMERIC_TO_FLOAT,
    "ceil": _NUMERIC_TO_INT,
    "cos": _NUMERIC_TO_FLOAT,
    "cosh": _NUMERIC_TO_FLOAT,
    "degrees": _NUMERIC_TO_FLOAT,
    "erf": _NUMERIC_TO_FLOAT,
    "erfc": _NUMERIC_TO_FLOAT,
    "exp": _NUMERIC_TO_FLOAT,
    "exp2": _NUMERIC_TO_FLOAT,
    "expm1": _NUMERIC_TO_FLOAT,
    "fabs": _NUMERIC_TO_FLOAT,
    "factorial": _INT_TO_INT,
    "floor": _NUMERIC_TO_INT,
    "gamma": _NUMERIC_TO_FLOAT,
    "isfinite": _NUMERIC_TO_BOOL,
    "isinf": _NUMERIC_TO_BOOL,
    "isnan": _NUMERIC_TO_BOOL,
    "lgamma": _NUMERIC_TO_FLOAT,
    "log1p": _NUMERIC_TO_FLOAT,
    "log2": _NUMERIC_TO_FLOAT,
    "log10": _NUMERIC_TO_FLOAT,
    "modf": frozenset(FunctionType((input_type,), TupleOf((Scalar.FLOAT, Scalar.FLOAT))) for input_type in _NUMERIC),
    "radians": _NUMERIC_TO_FLOAT,
    "sin": _NUMERIC_TO_FLOAT,
    "sinh": _NUMERIC_TO_FLOAT,
    "sqrt": _NUMERIC_TO_FLOAT,
    "tan": _NUMERIC_TO_FLOAT,
    "tanh": _NUMERIC_TO_FLOAT,
    "trunc": _NUMERIC_TO_INT,
    "ulp": _NUMERIC_TO_FLOAT,
}

MATH_VARIADIC_FUNCTION = {
    "dist": frozenset({FunctionType(None, Scalar.FLOAT)}),
    "fsum": frozenset({FunctionType(None, Scalar.FLOAT)}),
    "hypot": frozenset({FunctionType(None, Scalar.FLOAT)}),
    "isclose": _NUMERIC_NUMERIC_TO_BOOL | _NUMERIC_NUMERIC_NUMERIC_TO_BOOL | _NUMERIC_NUMERIC_NUMERIC_NUMERIC_TO_BOOL,
    "log": _NUMERIC_TO_FLOAT | _NUMERIC_NUMERIC_TO_FLOAT,
    "nextafter": _NUMERIC_NUMERIC_TO_FLOAT | _NUMERIC_NUMERIC_INT_TO_FLOAT,
    "prod": frozenset({FunctionType(None, Scalar.INT)}),
}

MATH_BINARY_FUNCTION = {
    "atan2": _NUMERIC_NUMERIC_TO_FLOAT,
    "copysign": _NUMERIC_NUMERIC_TO_FLOAT,
    "fmod": _NUMERIC_NUMERIC_TO_FLOAT,
    "ldexp": _NUMERIC_INT_TO_FLOAT,
    "pow": _NUMERIC_NUMERIC_TO_FLOAT,
    "remainder": _NUMERIC_NUMERIC_TO_FLOAT,
}

OPERATOR_FUNCTION = {
    "add": _NUMERIC_BINARY
    | frozenset({FunctionType((Scalar.STRING, Scalar.STRING), Scalar.STRING)})
    | frozenset(_LIST_ADD_BINARY),
    "sub": _NUMERIC_BINARY,
    "mul": _NUMERIC_BINARY,
    "mod": _NUMERIC_BINARY,
    "pow": _NUMERIC_BINARY,
    "truediv": _NUMERIC_NUMERIC_TO_FLOAT,
    "floordiv": _NUMERIC_BINARY,
    "lshift": _INT_INT_TO_INT,
    "rshift": _INT_INT_TO_INT,
    "and": _BITWISE_BINARY,
    "or": _BITWISE_BINARY,
    "xor": _BITWISE_BINARY,
    "not": frozenset((FunctionType(None, Scalar.BOOL),)),
    "pos": _INT_TO_INT | _FLOAT_TO_FLOAT,
    "neg": _INT_TO_INT | _FLOAT_TO_FLOAT,
    "invert": _INT_TO_INT | _BOOL_TO_INT,
}

_AST_OPERATOR_TO_FUNCTION_NAME = {
    ast.Add: "add",
    ast.Sub: "sub",
    ast.Mult: "mul",
    ast.Mod: "mod",
    ast.Pow: "pow",
    ast.Div: "truediv",
    ast.FloorDiv: "floordiv",
    ast.LShift: "lshift",
    ast.RShift: "rshift",
    ast.BitAnd: "and",
    ast.BitOr: "or",
    ast.BitXor: "xor",
    ast.Not: "not",
    ast.UAdd: "pos",
    ast.USub: "neg",
    ast.Invert: "invert",
}

STATIC_FUNCTION_BY_MODULE = {
    "builtins": BUILTIN_FUNCTION,
    "math": MATH_UNARY_FUNCTION | MATH_VARIADIC_FUNCTION | MATH_BINARY_FUNCTION,
    "operator": OPERATOR_FUNCTION,
}


def _get_static_overloads(
    static_module_name: object | None = "builtins",
    static_function_name: object | None = None,
) -> frozenset[FunctionType]:
    if not (isinstance(static_module_name, str) and isinstance(static_function_name, str)):
        return frozenset()
    return STATIC_FUNCTION_BY_MODULE.get(static_module_name, {}).get(static_function_name, frozenset())


def resolve_static_overloads(
    *,
    static_module_name: object | None = "builtins",
    static_function_name: object | None = None,
    operator: ast.operator | ast.unaryop | None = None,
) -> frozenset[FunctionType]:
    if operator is not None:
        return OPERATOR_FUNCTION.get(_AST_OPERATOR_TO_FUNCTION_NAME.get(type(operator), ""), frozenset())
    return _get_static_overloads(static_module_name, static_function_name)


def get_return_types(
    inferred_arg_types: tuple[frozenset[TypeInfo], ...],
    inferred_func_types: frozenset[FunctionType],
    static_overloads: frozenset[FunctionType],
) -> frozenset[TypeInfo]:
    overload_sources = tuple(overloads for overloads in (static_overloads, inferred_func_types) if overloads)

    out: set[TypeInfo] = set()
    for arg_types in itertools.product(*inferred_arg_types):
        matched_return_types: set[TypeInfo] = set()
        for overloads in overload_sources:
            exact_match_found = False
            wildcard_return_types: set[TypeInfo] = set()
            for overload in overloads:
                if overload.input_types == arg_types:
                    matched_return_types.add(overload.return_type)
                    exact_match_found = True
                elif overload.input_types is None:
                    wildcard_return_types.add(overload.return_type)
            if not exact_match_found:
                matched_return_types.update(wildcard_return_types)

        out.update(matched_return_types)

        if not matched_return_types:
            if UnknownType in inferred_func_types or UnknownType in arg_types:
                out.add(UnknownType)
            elif UnsupportedType in inferred_func_types or UnsupportedType in arg_types:
                out.add(UnsupportedType)

    return frozenset(out)
