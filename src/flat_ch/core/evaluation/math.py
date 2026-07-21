import math
import typing

from flat_ch.core.types import Type


def handle_add(arguments: list[tuple[Type, typing.Any]]) -> tuple[Type, typing.Any]:
    t1, v1 = arguments[0]
    t2, v2 = arguments[1]

    if t1 == Type.FLOAT or t2 == Type.FLOAT:
        return Type.FLOAT, float(v1) + float(v2)
    return Type.INT, int(v1) + int(v2)


def handle_sub(arguments: list[tuple[Type, typing.Any]]) -> tuple[Type, typing.Any]:
    t1, v1 = arguments[0]
    t2, v2 = arguments[1]

    if t1 == Type.FLOAT or t2 == Type.FLOAT:
        return Type.FLOAT, float(v1) - float(v2)
    return Type.INT, int(v1) - int(v2)


def handle_mult(arguments: list[tuple[Type, typing.Any]]) -> tuple[Type, typing.Any]:
    has_float = any(arg_type == Type.FLOAT for arg_type, _ in arguments)
    if has_float:
        result = 1.0
        for _, value in arguments:
            result *= float(value)
        return Type.FLOAT, result

    result = 1
    for _, value in arguments:
        result *= int(value)
    return Type.INT, result


def handle_float_div(arguments: list[tuple[Type, typing.Any]]) -> tuple[Type, typing.Any]:
    _, v1 = arguments[0]
    _, v2 = arguments[1]
    return Type.FLOAT, float(v1) / float(v2)


def handle_int_div(arguments: list[tuple[Type, typing.Any]]) -> tuple[Type, typing.Any]:
    _, v1 = arguments[0]
    _, v2 = arguments[1]
    return Type.INT, int(float(v1) // float(v2))


def handle_abs(arguments: list[tuple[Type, typing.Any]]) -> tuple[Type, typing.Any]:
    arg_type, value = arguments[0]
    if arg_type == Type.FLOAT:
        return Type.FLOAT, abs(float(value))
    return Type.INT, abs(int(value))


def handle_pow(arguments: list[tuple[Type, typing.Any]]) -> tuple[Type, typing.Any]:
    t1, v1 = arguments[0]
    t2, v2 = arguments[1]

    if t1 == Type.FLOAT or t2 == Type.FLOAT:
        return Type.FLOAT, float(v1) ** float(v2)
    return Type.INT, int(v1) ** int(v2)


def handle_length(arguments: list[tuple[Type, typing.Any]]) -> tuple[Type, typing.Any]:
    arg_type, value = arguments[0]
    if arg_type == Type.STRING:
        return Type.INT, len(str(value))
    raise TypeError(f"length expects a string argument here, got {arg_type}.")


def handle_concat(arguments: list[tuple[Type, typing.Any]]) -> tuple[Type, typing.Any]:
    (_, left_value), (_, right_value) = arguments
    return Type.STRING, str(left_value) + str(right_value)


def handle_ceil(arguments: list[tuple[Type, typing.Any]]) -> tuple[Type, typing.Any]:
    t, v = arguments[0]
    if t == Type.FLOAT:
        return Type.INT, math.ceil(float(v))
    return Type.INT, int(v)


def handle_floor(arguments: list[tuple[Type, typing.Any]]) -> tuple[Type, typing.Any]:
    t, v = arguments[0]
    if t == Type.FLOAT:
        return Type.INT, math.floor(float(v))
    return Type.INT, int(v)


def handle_minus(arguments: list[tuple[Type, typing.Any]]) -> tuple[Type, typing.Any]:
    t, v = arguments[0]

    if t == Type.FLOAT:
        return Type.FLOAT, -float(v)
    return Type.INT, -int(v)


def handle_sqrt(arguments: list[tuple[Type, typing.Any]]) -> tuple[Type, typing.Any]:
    _, v = arguments[0]
    return Type.FLOAT, math.sqrt(float(v))


def handle_max(arguments: list[tuple[Type, typing.Any]]) -> tuple[Type, typing.Any]:
    t1, v1 = arguments[0]
    t2, v2 = arguments[1]

    if float(v1) >= float(v2):
        return t1, v1
    return t2, v2


def handle_min(arguments: list[tuple[Type, typing.Any]]) -> tuple[Type, typing.Any]:
    t1, v1 = arguments[0]
    t2, v2 = arguments[1]

    if float(v1) <= float(v2):
        return t1, v1
    return t2, v2
