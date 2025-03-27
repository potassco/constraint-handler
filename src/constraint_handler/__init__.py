"""
The constraint-handler project.
"""

import uuid
from importlib.resources import files

from clingo.ast import ASTType, ProgramBuilder, Transformer, parse_files
from clingo.script import enable_python

CONDITIONALS_LP = files("constraint_handler.data").joinpath("conditionals.lp")
DIRECT_LP = files("constraint_handler.data").joinpath("direct.lp")
DISPLAY_LP = files("constraint_handler.data").joinpath("display.lp")
FLOATS_LP = files("constraint_handler.data").joinpath("floats.lp")
GRINGO_EVAL_LP = files("constraint_handler.data").joinpath("gringoEval.lp")
MAIN_LP = files("constraint_handler.data").joinpath("main.lp")
INTENSIONAL_SET_LP = files("constraint_handler.data").joinpath("intensionalSet.lp")
UNIQUE_PREFIX = str(uuid.uuid4())

enable_python()


class ProgramTransformer(Transformer):
    def visit_SymbolicAtom(self, atom):
        if atom.symbol.ast_type == ASTType.Function:
            if atom.symbol.name == "assign" and len(atom.symbol.arguments) == 3:
                pass
            else:
                new_name = UNIQUE_PREFIX + atom.symbol.name
                atom.symbol.name = new_name
        return atom


def add_encoding_to_program_builder(b: ProgramBuilder):
    """Adds encoding logic to the provided ProgramBuilder instance."""
    with b:
        t = ProgramTransformer()
        parse_files(
            [
                str(CONDITIONALS_LP),
                str(DIRECT_LP),
                str(DISPLAY_LP),
                str(FLOATS_LP),
                str(GRINGO_EVAL_LP),
                str(MAIN_LP),
                str(INTENSIONAL_SET_LP),
            ],
            lambda stm: b.add(t.visit(stm)),
        )
