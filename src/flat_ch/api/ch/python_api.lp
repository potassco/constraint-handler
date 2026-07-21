#script (python)
import os

from clingo import Function, Number, String
from clingo.symbol import SymbolType

from flat_ch.api.ch.registration import Registration
from flat_ch.api.ch.serialization import CHSerializer
from flat_ch.core.serialization import BaseSerializer
from flat_ch.core.evaluation.evaluator import evaluate_operation
from flat_ch.core.evaluation.python import PythonRegistry
from flat_ch.core.flattener import Flattener
from flat_ch.core.registry import ProgramRegistry

_input_serializer = CHSerializer()
_internal_serializer = BaseSerializer()
_global_python_registry = PythonRegistry(_internal_serializer)
_global_flattener = Flattener(_global_python_registry, _internal_serializer)
_global_registry = ProgramRegistry(Registration, _input_serializer)
_DEBUG = os.environ.get("FCH_DEBUG", "").lower() in {"1", "true", "yes", "on"}


def _float_symbol_to_python(value):
    if value.type == SymbolType.Function and value.name == "float" and len(value.arguments) == 1:
        inner = value.arguments[0]
        if inner.type == SymbolType.Number:
            return float(inner.number)
        if inner.type == SymbolType.String:
            return float(inner.string)
        return float(str(inner))
    if value.type == SymbolType.Number:
        return float(value.number)
    return float(value.string)

def fch_register(clingo_term):
    return _global_registry.register(clingo_term)

def fch_flatten():
    program_ir = _global_registry.get_program_ir()
    flat_facts = _global_flattener.flatten(program_ir)
    if _DEBUG:
        _global_flattener.debug_print_dag()
    return flat_facts


def fch_operation(operator_symbol, argument_tuple):
    return evaluate_operation(operator_symbol, argument_tuple, _internal_serializer)


def fch_py_operation(operation_symbol, argument_list):
    return _global_python_registry.execute(operation_symbol, argument_list)


def fch_integral_float_to_int(value):
    numeric = _float_symbol_to_python(value)
    rounded = round(numeric)
    if abs(numeric - rounded) <= 1e-9:
        return Number(rounded)
    return Number(0)


def fch_float_is_integral(value):
    numeric = _float_symbol_to_python(value)
    rounded = round(numeric)
    return Function("true" if abs(numeric - rounded) <= 1e-9 else "false", [])


def fch_scaled_float_to_int(value, precision):
    numeric = _float_symbol_to_python(value)
    return Number(int(numeric * precision.number // 1))


def fch_scaled_int_to_float(value, precision):
    numeric = value.number / precision.number
    return String(repr(numeric))


def fch_unscale_int(value, precision):
    return Number(int(value.number / precision.number))
#end.
