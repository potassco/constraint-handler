"""
The constraint-handler project.
"""

from importlib.resources import files

from clingo.ast import ProgramBuilder, parse_files
from clingo.script import enable_python

BOOL_LP = files("constraint_handler.data").joinpath("bool.lp")
CONDITIONALS_LP = files("constraint_handler.data").joinpath("conditionals.lp")
DIRECT_LP = files("constraint_handler.data").joinpath("direct.lp")
DISPLAY_LP = files("constraint_handler.data").joinpath("display.lp")
FLOAT_LP = files("constraint_handler.data").joinpath("float.lp")
GRINGO_EVAL_LP = files("constraint_handler.data").joinpath("gringoEval.lp")
INT_LP = files("constraint_handler.data").joinpath("int.lp")
MAIN_LP = files("constraint_handler.data").joinpath("main.lp")
MULTIMAP_LP = files("constraint_handler.data").joinpath("multimap.lp")
SET_LP = files("constraint_handler.data").joinpath("set.lp")
STRING_LP = files("constraint_handler.data").joinpath("string.lp")

enable_python()


def add_encoding_to_program_builder(b: ProgramBuilder):
    """Adds encoding logic to the provided ProgramBuilder instance."""
    with b:
        parse_files(
            [
                str(BOOL_LP),
                str(CONDITIONALS_LP),
                str(DIRECT_LP),
                str(DISPLAY_LP),
                str(FLOAT_LP),
                str(GRINGO_EVAL_LP),
                str(INT_LP),
                str(MAIN_LP),
                str(MULTIMAP_LP),
                str(SET_LP),
                str(STRING_LP),
            ],
            lambda stm: b.add(stm),
        )
