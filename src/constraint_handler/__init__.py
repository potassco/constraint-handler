"""
The constraint-handler project.
"""

from importlib.resources import files

import clingo
import clingo.ast
import clingo.script

modules = [
    "bool",
    "conditionals",
    "direct",
    "execution",
    "float",
    "gringoEval",
    "groundExec",
    "int",
    "main",
    "multimap",
    "optimize",
    "preference",
    "propagator",
    "pythonHelper",
    "set",
    "string",
    "symbol",
    "variable",
]


def add_to_control(ctrl: clingo.Control, environment=None, _environment_ids=dict()):
    """Adds encoding logic to the provided Control instance. The environment argumennt specifies the locals used in the python statements and expressions."""
    clingo.script.enable_python()
    for mod in modules:
        file = files("constraint_handler.data").joinpath(f"{mod}.lp")
        ctrl.load(str(file))
    if environment is not None:
        eid = id(environment)
        if eid in _environment_ids:
            idx = _environment_ids[eid]
        else:
            idx = len(_environment_ids)
            evaluator._solver_environment[idx] = environment
            _environment_ids[eid] = idx
        ctrl.add(f"main_solverIdentifier({idx}).")


def set_globals(environment=None):
    """The environment argumennt specifies the globals used in the python statements and expressions.
    By default, the globals import the math module.
    Calling set_globals with no arguments clears the globals."""
    if environment is not None:
        evaluator._shared_environment = environment
    else:
        evaluator._shared_environment = dict()


def add_to_globals(environment):
    evaluator._shared_environment.update(environment)


def add_encoding_to_program_builder(b: clingo.ast.ProgramBuilder):
    """Adds encoding logic to the provided ProgramBuilder instance."""
    clingo.script.enable_python()
    all_files = [str(files("constraint_handler.data").joinpath(f"{mod}.lp")) for mod in modules]
    with b:
        clingo.ast.parse_files(all_files, lambda stm: b.add(stm))
