%
% This module contains the internal Python API.
%
% All python functions used in the internal encodings should be defined here.
% The functions are not intended for user facing use, which is why the prefix
% 'fch_' is used.

#script (python)
import os

from clingo import Function, Number

from flat_ch.api.flat.serialization import FCHSerializer
from flat_ch.core.flattener import Flattener
from flat_ch.core.evaluation.evaluator import evaluate_operation
from flat_ch.api.flat.registration import Registration
from flat_ch.core.registry import ProgramRegistry, native_static_result
from flat_ch.core.ssa import SSA
from flat_ch.core.evaluation.python import PythonRegistry
_global_serializer = FCHSerializer()
_global_python_registry = PythonRegistry()
_global_flattener = Flattener(_global_python_registry, _global_serializer, constant_folding=False)
_global_registered_program = ProgramRegistry(Registration, _global_serializer)
_DEBUG = os.environ.get("FCH_DEBUG", "").lower() in {"1", "true", "yes", "on"}
"""
The global Flattener instance used for turning nested expressions into a flat representation.

This is loaded here in order to give each clingo control a separate flattener.
"""


_global_ssa = SSA()
def fch_register(clingo_term):
    return _global_registered_program.register(clingo_term)

def fch_flatten(clingo_term=None):
    if clingo_term is not None:
        return _global_flattener.flatten(clingo_term)

    if _DEBUG:
        _global_registered_program.debug_print("flat")
    return native_static_result()

def fch_operation(operator_symbol, argument_tuple):
    return evaluate_operation(operator_symbol, argument_tuple, _global_serializer)

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

def fch_ssa(clingo_term):
    ssa_done = _global_ssa.apply(clingo_term)

    flatten_done = [
        fact
        for term in ssa_done
        for fact in _global_flattener.flatten(term)
    ]
    return flatten_done
#end.
