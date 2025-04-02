"""
The constraint-handler project.
"""

from importlib.resources import files

from clingo.ast import ProgramBuilder, parse_files
from clingo.script import enable_python

CONDITIONALS_LP = files("constraint_handler.data").joinpath("conditionals.lp")
DIRECT_LP = files("constraint_handler.data").joinpath("direct.lp")
DISPLAY_LP = files("constraint_handler.data").joinpath("display.lp")
FLOATS_LP = files("constraint_handler.data").joinpath("floats.lp")
GRINGO_EVAL_LP = files("constraint_handler.data").joinpath("gringoEval.lp")
MAIN_LP = files("constraint_handler.data").joinpath("main.lp")

enable_python()


def add_encoding_to_program_builder(b: ProgramBuilder):
    """Adds encoding logic to the provided ProgramBuilder instance."""
    with b:
        parse_files(
            [
                str(CONDITIONALS_LP),
                str(DIRECT_LP),
                str(DISPLAY_LP),
                str(FLOATS_LP),
                str(GRINGO_EVAL_LP),
                str(MAIN_LP),
            ],
            lambda stm: b.add(stm),
        )
