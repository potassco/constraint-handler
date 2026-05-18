"""Declarative function signatures for Python statement analysis."""

from __future__ import annotations

import ast

from constraint_handler.utils.python_type_model import (
    _BOOL_SCALAR,
    _FLOAT_SCALAR,
    _INT_SCALAR,
    _STR_SCALAR,
    FunctionType,
    TupleOf,
)

_BOOL_TYPES = frozenset({_BOOL_SCALAR})
_INT_TYPES = frozenset({_INT_SCALAR})
_FLOAT_TYPES = frozenset({_FLOAT_SCALAR})
_STR_TYPES = frozenset({_STR_SCALAR})
_NUMERIC_SCALAR_TYPES = frozenset({_INT_SCALAR, _FLOAT_SCALAR})
_ONE_NUMERIC_INPUT = (_NUMERIC_SCALAR_TYPES,)
_TWO_NUMERIC_INPUTS = (_NUMERIC_SCALAR_TYPES, _NUMERIC_SCALAR_TYPES)
_NUMERIC_AND_INT_INPUTS = (_NUMERIC_SCALAR_TYPES, _INT_TYPES)
_NUMERIC_BINARY_OVERLOADS = (
    FunctionType((_INT_TYPES, _INT_TYPES), _INT_TYPES),
    FunctionType((_INT_TYPES, _FLOAT_TYPES), _FLOAT_TYPES),
    FunctionType((_FLOAT_TYPES, _INT_TYPES), _FLOAT_TYPES),
    FunctionType((_FLOAT_TYPES, _FLOAT_TYPES), _FLOAT_TYPES),
)
_DIV_BINARY_OVERLOADS = (FunctionType((_NUMERIC_SCALAR_TYPES, _NUMERIC_SCALAR_TYPES), _FLOAT_TYPES),)
_FLOORDIV_BINARY_OVERLOADS = _NUMERIC_BINARY_OVERLOADS
_INT_BINARY_OVERLOADS = (FunctionType((_INT_TYPES, _INT_TYPES), _INT_TYPES),)

MATH_FUNCTION_TYPES = {
    "acos": FunctionType(_ONE_NUMERIC_INPUT, _FLOAT_TYPES),
    "acosh": FunctionType(_ONE_NUMERIC_INPUT, _FLOAT_TYPES),
    "asin": FunctionType(_ONE_NUMERIC_INPUT, _FLOAT_TYPES),
    "asinh": FunctionType(_ONE_NUMERIC_INPUT, _FLOAT_TYPES),
    "atan": FunctionType(_ONE_NUMERIC_INPUT, _FLOAT_TYPES),
    "atan2": FunctionType(_TWO_NUMERIC_INPUTS, _FLOAT_TYPES),
    "atanh": FunctionType(_ONE_NUMERIC_INPUT, _FLOAT_TYPES),
    "cbrt": FunctionType(_ONE_NUMERIC_INPUT, _FLOAT_TYPES),
    "ceil": FunctionType(_ONE_NUMERIC_INPUT, _INT_TYPES),
    "copysign": FunctionType(_TWO_NUMERIC_INPUTS, _FLOAT_TYPES),
    "cos": FunctionType(_ONE_NUMERIC_INPUT, _FLOAT_TYPES),
    "cosh": FunctionType(_ONE_NUMERIC_INPUT, _FLOAT_TYPES),
    "degrees": FunctionType(_ONE_NUMERIC_INPUT, _FLOAT_TYPES),
    "dist": FunctionType(None, _FLOAT_TYPES),
    "erf": FunctionType(_ONE_NUMERIC_INPUT, _FLOAT_TYPES),
    "erfc": FunctionType(_ONE_NUMERIC_INPUT, _FLOAT_TYPES),
    "exp": FunctionType(_ONE_NUMERIC_INPUT, _FLOAT_TYPES),
    "exp2": FunctionType(_ONE_NUMERIC_INPUT, _FLOAT_TYPES),
    "expm1": FunctionType(_ONE_NUMERIC_INPUT, _FLOAT_TYPES),
    "fabs": FunctionType(_ONE_NUMERIC_INPUT, _FLOAT_TYPES),
    "factorial": FunctionType((_INT_TYPES,), _INT_TYPES),
    "floor": FunctionType(_ONE_NUMERIC_INPUT, _INT_TYPES),
    "fmod": FunctionType(_TWO_NUMERIC_INPUTS, _FLOAT_TYPES),
    "fsum": FunctionType(None, _FLOAT_TYPES),
    "gamma": FunctionType(_ONE_NUMERIC_INPUT, _FLOAT_TYPES),
    "hypot": FunctionType(None, _FLOAT_TYPES),
    "isclose": FunctionType(None, _BOOL_TYPES),
    "isfinite": FunctionType(_ONE_NUMERIC_INPUT, _BOOL_TYPES),
    "isinf": FunctionType(_ONE_NUMERIC_INPUT, _BOOL_TYPES),
    "isnan": FunctionType(_ONE_NUMERIC_INPUT, _BOOL_TYPES),
    "ldexp": FunctionType(_NUMERIC_AND_INT_INPUTS, _FLOAT_TYPES),
    "lgamma": FunctionType(_ONE_NUMERIC_INPUT, _FLOAT_TYPES),
    "log": FunctionType(None, _FLOAT_TYPES),
    "log1p": FunctionType(_ONE_NUMERIC_INPUT, _FLOAT_TYPES),
    "log2": FunctionType(_ONE_NUMERIC_INPUT, _FLOAT_TYPES),
    "log10": FunctionType(_ONE_NUMERIC_INPUT, _FLOAT_TYPES),
    "modf": FunctionType(_ONE_NUMERIC_INPUT, frozenset({TupleOf((_FLOAT_TYPES, _FLOAT_TYPES))})),
    "nextafter": FunctionType(None, _FLOAT_TYPES),
    "pow": FunctionType(_TWO_NUMERIC_INPUTS, _FLOAT_TYPES),
    "prod": FunctionType(None, _INT_TYPES),
    "radians": FunctionType(_ONE_NUMERIC_INPUT, _FLOAT_TYPES),
    "remainder": FunctionType(_TWO_NUMERIC_INPUTS, _FLOAT_TYPES),
    "sin": FunctionType(_ONE_NUMERIC_INPUT, _FLOAT_TYPES),
    "sinh": FunctionType(_ONE_NUMERIC_INPUT, _FLOAT_TYPES),
    "sqrt": FunctionType(_ONE_NUMERIC_INPUT, _FLOAT_TYPES),
    "tan": FunctionType(_ONE_NUMERIC_INPUT, _FLOAT_TYPES),
    "tanh": FunctionType(_ONE_NUMERIC_INPUT, _FLOAT_TYPES),
    "trunc": FunctionType(_ONE_NUMERIC_INPUT, _INT_TYPES),
    "ulp": FunctionType(_ONE_NUMERIC_INPUT, _FLOAT_TYPES),
}

BINARY_OPERATOR_OVERLOADS = {
    ast.Add: _NUMERIC_BINARY_OVERLOADS + (FunctionType((_STR_TYPES, _STR_TYPES), _STR_TYPES),),
    ast.Sub: _NUMERIC_BINARY_OVERLOADS,
    ast.Mult: _NUMERIC_BINARY_OVERLOADS,
    ast.Mod: _NUMERIC_BINARY_OVERLOADS,
    ast.Pow: _NUMERIC_BINARY_OVERLOADS,
    ast.Div: _DIV_BINARY_OVERLOADS,
    ast.FloorDiv: _FLOORDIV_BINARY_OVERLOADS,
    ast.LShift: _INT_BINARY_OVERLOADS,
    ast.RShift: _INT_BINARY_OVERLOADS,
    ast.BitAnd: _INT_BINARY_OVERLOADS,
    ast.BitOr: _INT_BINARY_OVERLOADS,
    ast.BitXor: _INT_BINARY_OVERLOADS,
}

UNARY_OPERATOR_OVERLOADS = {
    ast.Not: (FunctionType(None, _BOOL_TYPES),),
    ast.UAdd: (
        FunctionType((_INT_TYPES,), _INT_TYPES),
        FunctionType((_FLOAT_TYPES,), _FLOAT_TYPES),
    ),
    ast.USub: (
        FunctionType((_INT_TYPES,), _INT_TYPES),
        FunctionType((_FLOAT_TYPES,), _FLOAT_TYPES),
    ),
    ast.Invert: (
        FunctionType((_INT_TYPES,), _INT_TYPES),
        FunctionType((_BOOL_TYPES,), _INT_TYPES),
    ),
}
