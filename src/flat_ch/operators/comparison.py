import math
import typing

from flat_ch.core.types import Type


def handle_eq(arguments: list[tuple[Type, typing.Any]]) -> tuple[Type, bool]:
    (t1, v1), (t2, v2) = arguments

    if t1 == Type.NONE or t2 == Type.NONE:
        return Type.BOOL, t1 == t2

    numeric_types = {Type.INT, Type.FLOAT}

    if t1 in numeric_types and t2 in numeric_types:
        return Type.BOOL, math.isclose(float(v1), float(v2))

    if t1 != t2:
        return Type.BOOL, False

    return Type.BOOL, v1 == v2


def handle_neq(arguments: list[tuple[Type, typing.Any]]) -> tuple[Type, bool]:
    eq_type, eq_value = handle_eq(arguments)
    return eq_type, not eq_value


def handle_leq(arguments: list[tuple[Type, typing.Any]]) -> tuple[Type, bool]:
    (_, v1), (_, v2) = arguments
    f1, f2 = float(v1), float(v2)
    return Type.BOOL, f1 < f2 or math.isclose(f1, f2)


def handle_lt(arguments: list[tuple[Type, typing.Any]]) -> tuple[Type, bool]:
    (_, v1), (_, v2) = arguments
    f1, f2 = float(v1), float(v2)
    return Type.BOOL, f1 < f2 and not math.isclose(f1, f2)


def handle_gt(arguments: list[tuple[Type, typing.Any]]) -> tuple[Type, bool]:
    (_, v1), (_, v2) = arguments
    f1, f2 = float(v1), float(v2)
    return Type.BOOL, f1 > f2 and not math.isclose(f1, f2)


def handle_geq(arguments: list[tuple[Type, typing.Any]]) -> tuple[Type, bool]:
    (_, v1), (_, v2) = arguments
    f1, f2 = float(v1), float(v2)
    return Type.BOOL, f1 > f2 or math.isclose(f1, f2)
