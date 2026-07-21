import typing
from collections import Counter
from functools import cache
from threading import Lock

from clingo import Function

from flat_ch.core.evaluation.operators import Operator
from flat_ch.core.evaluation.registry import OPERATOR_HANDLERS
from flat_ch.core.serialization import SerializerProtocol
from flat_ch.core.types import Type

_OPERATION_USAGE_COUNTER: Counter[tuple[str, ...]] = Counter()
_OPERATION_USAGE_LOCK = Lock()


def reset_operation_usage_counts() -> None:
    with _OPERATION_USAGE_LOCK:
        _OPERATION_USAGE_COUNTER.clear()


def get_operation_usage_counts() -> dict[tuple[str, ...], int]:
    with _OPERATION_USAGE_LOCK:
        return dict(_OPERATION_USAGE_COUNTER)


def _record_operation_usage(operator: Operator, argument_types: list[Type]) -> None:
    key = (operator.asp_name, *(arg_type.name.lower() for arg_type in argument_types))
    with _OPERATION_USAGE_LOCK:
        _OPERATION_USAGE_COUNTER[key] += 1


@cache
def evaluate_operation(operator_symbol, arguments_tuple, serializer: SerializerProtocol) -> Function:
    """
    Evaluates a built-in operation given its operator symbol and argument tuple.
    """
    try:
        operator = Operator(operator_symbol.number)
        arguments = [serializer.clingo_to_python(arg) for arg in arguments_tuple.arguments]
        _record_operation_usage(operator, [arg_type for arg_type, _ in arguments])

        pure_type, pure_value = evaluate_operation_pure(operator, arguments)
        clingo_result = serializer.python_to_clingo(pure_type, pure_value)
        return clingo_result
    except Exception as e:
        raise TypeError(f"Error evaluating operation {operator_symbol} with arguments {arguments_tuple}: {e}")


def evaluate_operation_pure(operator: Operator, arguments: list[tuple[Type, typing.Any]]) -> tuple[Type, typing.Any]:
    """
    Evaluates a built-in operation given its operator ID and argument list in pure Python types.
    """

    handler = OPERATOR_HANDLERS.get(operator)

    if not handler:
        raise NotImplementedError(f"Operator {operator} is not supported. No handler found.")

    return handler(arguments)
