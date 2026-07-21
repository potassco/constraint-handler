import typing

from flat_ch.core.types import Type


def handle_hasvalue(arguments: list[tuple[Type, typing.Any]]) -> tuple[Type, typing.Any]:
    arg_type, _ = arguments[0]
    return Type.BOOL, arg_type != Type.NONE


def handle_if(arguments: list[tuple[Type, typing.Any]]) -> tuple[Type, typing.Any]:
    (condition_type, condition_value), (then_type, then_value) = arguments

    if condition_type == Type.NONE:
        return Type.NONE, None
    if condition_type == Type.BOOL and condition_value is True:
        return then_type, then_value
    if condition_type == Type.BOOL and condition_value is False:
        return Type.NONE, None
    raise TypeError(f"if expects a bool/none condition, got {condition_type}.")


def handle_ite(arguments: list[tuple[Type, typing.Any]]) -> tuple[Type, typing.Any]:
    (condition_type, condition_value), (then_type, then_value), (else_type, else_value) = arguments

    if condition_type == Type.NONE:
        return Type.NONE, None
    if condition_type == Type.BOOL and condition_value is True:
        return then_type, then_value
    if condition_type == Type.BOOL and condition_value is False:
        return else_type, else_value
    raise TypeError(f"ite expects a bool/none condition, got {condition_type}.")


def handle_limp(arguments: list[tuple[Type, typing.Any]]) -> tuple[Type, typing.Any]:
    (left_type, left_value), (right_type, right_value) = arguments

    if left_type == Type.BOOL and left_value is False:
        return Type.BOOL, True
    if right_type == Type.BOOL and right_value is True:
        return Type.BOOL, True
    if left_type == Type.BOOL and left_value is True and right_type == Type.BOOL and right_value is False:
        return Type.BOOL, False
    if left_type == Type.NONE or right_type == Type.NONE:
        return Type.NONE, None
    raise TypeError(f"limp expects bool/none arguments, got {left_type} and {right_type}.")


def handle_leqv(arguments: list[tuple[Type, typing.Any]]) -> tuple[Type, typing.Any]:
    if not arguments:
        return Type.BOOL, True

    if any(arg_type == Type.NONE for arg_type, _ in arguments):
        return Type.NONE, None

    if any(arg_type != Type.BOOL for arg_type, _ in arguments):
        raise TypeError(f"leqv expects bool/none arguments, got {arguments}.")

    result = bool(arguments[0][1])
    for _, value in arguments[1:]:
        result = result == bool(value)
    return Type.BOOL, result


def handle_lnot(arguments: list[tuple[Type, typing.Any]]) -> tuple[Type, typing.Any]:
    arg_type, arg_value = arguments[0]

    if arg_type == Type.NONE:
        return Type.NONE, None
    if arg_type == Type.BOOL:
        return Type.BOOL, not arg_value
    raise TypeError(f"lnot expects a bool/none argument, got {arg_type}.")


def handle_snot(arguments: list[tuple[Type, typing.Any]]) -> tuple[Type, typing.Any]:
    arg_type, arg_value = arguments[0]

    if arg_type == Type.BOOL:
        return Type.BOOL, not arg_value
    if arg_type == Type.NONE:
        return Type.BOOL, False
    raise TypeError(f"snot expects a bool/none argument, got {arg_type}.")


def handle_wnot(arguments: list[tuple[Type, typing.Any]]) -> tuple[Type, typing.Any]:
    arg_type, arg_value = arguments[0]

    if arg_type == Type.NONE:
        return Type.BOOL, True
    if arg_type == Type.BOOL:
        return Type.BOOL, not arg_value
    raise TypeError(f"wnot expects a bool/none argument, got {arg_type}.")


def handle_lxor(arguments: list[tuple[Type, typing.Any]]) -> tuple[Type, typing.Any]:
    (left_type, left_value), (right_type, right_value) = arguments

    if left_type == Type.NONE or right_type == Type.NONE:
        return Type.NONE, None
    if left_type == Type.BOOL and right_type == Type.BOOL:
        return Type.BOOL, bool(left_value) != bool(right_value)
    raise TypeError(f"lxor expects bool/none arguments, got {left_type} and {right_type}.")
