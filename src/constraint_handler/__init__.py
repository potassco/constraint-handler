"""
The constraint-handler project.
"""

from importlib.resources import files

from clingo.ast import ProgramBuilder, parse_files
from clingo.script import enable_python

BOOL_LP = files("constraint_handler.data").joinpath("bool.lp")
CONDITIONALS_LP = files("constraint_handler.data").joinpath("conditionals.lp")
DIRECT_LP = files("constraint_handler.data").joinpath("direct.lp")
EXECUTION_LP = files("constraint_handler.data").joinpath("execution.lp")
FLOAT_LP = files("constraint_handler.data").joinpath("float.lp")
GRINGO_EVAL_LP = files("constraint_handler.data").joinpath("gringoEval.lp")
GROUND_EXEC_LP = files("constraint_handler.data").joinpath("groundExec.lp")
INT_LP = files("constraint_handler.data").joinpath("int.lp")
MAIN_LP = files("constraint_handler.data").joinpath("main.lp")
MULTIMAP_LP = files("constraint_handler.data").joinpath("multimap.lp")
OPTIMIZE_LP = files("constraint_handler.data").joinpath("optimize.lp")
PREFERENCE_LP = files("constraint_handler.data").joinpath("preference.lp")
PROPAGATOR_LP = files("constraint_handler.data").joinpath("propagator.lp")
PYTHON_HELPER_LP = files("constraint_handler.data").joinpath("pythonHelper.lp")
SET_LP = files("constraint_handler.data").joinpath("set.lp")
STRING_LP = files("constraint_handler.data").joinpath("string.lp")
SYMBOL_LP = files("constraint_handler.data").joinpath("symbol.lp")

enable_python()


def add_encoding_to_program_builder(b: ProgramBuilder):
    """Adds encoding logic to the provided ProgramBuilder instance."""
    with b:
        parse_files(
            [
                str(BOOL_LP),
                str(CONDITIONALS_LP),
                str(DIRECT_LP),
                str(EXECUTION_LP),
                str(FLOAT_LP),
                str(GRINGO_EVAL_LP),
                str(GROUND_EXEC_LP),
                str(INT_LP),
                str(MAIN_LP),
                str(MULTIMAP_LP),
                str(OPTIMIZE_LP),
                str(PREFERENCE_LP),
                str(PYTHON_HELPER_LP),
                str(PROPAGATOR_LP),
                str(SET_LP),
                str(STRING_LP),
                str(SYMBOL_LP),
            ],
            lambda stm: b.add(stm),
        )
