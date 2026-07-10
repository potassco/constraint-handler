from functools import cache
import typing

from clingo import Function

from flat_ch.core.types import Type
from flat_ch.core.operators import Operator
from flat_ch.core.serialization import clingo_to_python, python_to_clingo
from flat_ch.operators.registry import OPERATOR_HANDLERS

@cache
def evaluate_operation(operator_symbol, arguments_tuple) -> Function:
    """
    Evaluates a built-in operation given its operator symbol and argument tuple.
    """
    try:
        operator = Operator(operator_symbol.number)
        arguments = [clingo_to_python(arg) for arg in arguments_tuple.arguments]
        
        pure_type, pure_value = evaluate_operation_pure(operator, arguments)
        clingo_result = python_to_clingo(pure_type, pure_value)
        return clingo_result
    except Exception as e:
        raise TypeError(f"Error evaluating operation {operator_symbol} with arguments {arguments_tuple}: {e}")

def evaluate_operation_pure(operator: Operator, arguments: list[tuple[Type, typing.Any]]) -> tuple[Type, typing.Any]:
    """
    Evaluates a built-in operation given its operator ID and argument list in pure Python types.
    """

    handler = OPERATOR_HANDLERS.get(operator)

    if not handler:
        raise NotImplementedError(
            f"Operator {operator} is not supported. No handler found."
        )
        
    return handler(arguments)