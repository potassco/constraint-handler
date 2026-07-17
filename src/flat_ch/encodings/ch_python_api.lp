#script (python)
from clingo import Function, Number, String

from flat_ch.ch_flattener import CHFlattener, normalize_execution_declare
from flat_ch.ch_ssa import CHSSA
from flat_ch.evaluator import evaluate_operation
from flat_ch.operators.python import PythonRegistry

_global_python_registry = PythonRegistry()
_global_flattener = CHFlattener(_global_python_registry, constant_folding=False)
_global_ssa = CHSSA(_global_flattener)


def fch_flatten(clingo_term):
    return _global_flattener.flatten(clingo_term)


def fch_operation(operator_symbol, argument_tuple):
    return evaluate_operation(operator_symbol, argument_tuple)


def fch_py_operation(operation_symbol, argument_list):
    return _global_python_registry.execute(operation_symbol, argument_list)


def fch_integral_float_to_int(value):
    numeric = float(value.string)
    rounded = round(numeric)
    if abs(numeric - rounded) <= 1e-9:
        return Number(rounded)
    return Number(0)


def fch_float_is_integral(value):
    numeric = float(value.string)
    rounded = round(numeric)
    return Function("true" if abs(numeric - rounded) <= 1e-9 else "false", [])


def fch_scaled_float_to_int(value, precision):
    numeric = float(value.string)
    return Number(int(numeric * precision.number // 1))


def fch_scaled_int_to_float(value, precision):
    numeric = value.number / precision.number
    return String(repr(numeric))


def fch_unscale_int(value, precision):
    return Number(int(value.number / precision.number))


def fch_ssa(clingo_term):
    return _global_ssa.apply(clingo_term)


def fch_execution_inputs(clingo_term):
    normalized_execution = normalize_execution_declare(clingo_term)
    name_symbol, _, inputs_tuple, outputs_tuple = normalized_execution.arguments
    return [
        Function("execution_input_decl", [name_symbol, input_symbol])
        for input_symbol in inputs_tuple.arguments
    ] + [
        Function("execution_output_decl", [name_symbol, output_symbol])
        for output_symbol in outputs_tuple.arguments
    ]
#end.
