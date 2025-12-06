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


def add_to_control(ctrl: clingo.Control):
    """Adds encoding logic to the provided Control instance."""
    clingo.script.enable_python()
    for mod in modules:
        file = files("constraint_handler.data").joinpath(f"{mod}.lp")
        ctrl.load(str(file))


def add_encoding_to_program_builder(b: clingo.ast.ProgramBuilder):
    """Adds encoding logic to the provided ProgramBuilder instance."""
    clingo.script.enable_python()
    all_files = [str(files("constraint_handler.data").joinpath(f"{mod}.lp")) for mod in modules]
    with b:
        clingo.ast.parse_files(all_files, lambda stm: b.add(stm))
