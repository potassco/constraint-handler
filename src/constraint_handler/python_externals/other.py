import math
from functools import cache

import clingo

import constraint_handler.myClorm as myClorm
import constraint_handler.schemas.expression as expression


@cache
def pythonScaleInteger(value, scale):
    """
    Scales the given float/bool/integer value by the provided scale factor.
    Returns floor of scaled value
    """
    return myClorm.pytocl(
        math.floor(myClorm.cltopy(value, expression.constant) * myClorm.cltopy(scale, expression.constant))
    )


@cache
def _to_val(type_, v):
    return clingo.Function("val", [clingo.Function(type_, []), myClorm.pytocl(v)])


@cache
def pythonFloatUnary(operator, val):
    value = float(val.arguments[0].string)
    match operator.name:
        case "abs":
            return _to_val("float", abs(value))
        case "ceil":
            return _to_val("int", math.ceil(value))
        case "floor":
            return _to_val("int", math.floor(value))
        case "minus":
            return _to_val("float", -value)
        case _:
            return clingo.Function("bad", [])


@cache
def pythonFloatBinary(operator, val1, val2):
    """given an operator and two values, evaluates the result of applying the operator to the values as floating string ("42.0")"""
    if val1.type == clingo.SymbolType.Number:
        value1 = val1.number
    elif (
        val1.type == clingo.SymbolType.Function
        and val1.name == "float"
        and len(val1.arguments) == 1
        and val1.arguments[0].type == clingo.SymbolType.String
    ):
        value1 = float(val1.arguments[0].string)

    if val2.type == clingo.SymbolType.Number:
        value2 = val2.number
    elif (
        val2.type == clingo.SymbolType.Function
        and val2.name == "float"
        and len(val2.arguments) == 1
        and val2.arguments[0].type == clingo.SymbolType.String
    ):
        value2 = float(val2.arguments[0].string)

    match operator.name:
        case "add":
            return _to_val("float", value1 + value2)
        case "mult":
            return _to_val("float", value1 * value2)
        case "int_div":
            if value2 == 0.0:
                return clingo.Function("bad", [])
            return _to_val("int", math.floor(value1 / value2))
        case "float_div":
            if value2 == 0.0:
                return clingo.Function("bad", [])
            return _to_val("float", value1 / value2)
        case "sub":
            return _to_val("float", value1 - value2)
        case "pow":
            return _to_val("float", value1**value2)
        case "eq":
            return _to_val("bool", value1 == value2)
        case "neq":
            return _to_val("bool", value1 != value2)
        case "leq":
            return _to_val("bool", value1 <= value2)
        case "lt":
            return _to_val("bool", value1 < value2)
        case "geq":
            return _to_val("bool", value1 >= value2)
        case "gt":
            return _to_val("bool", value1 > value2)
        case "max":
            return _to_val("float", max(value1, value2))
        case "min":
            return _to_val("float", min(value1, value2))
        case _:
            return clingo.Function("bad", [])
