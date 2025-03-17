"""
The constraint-handler project.
"""

from importlib.resources import files

from clingo import Control
from clingo.script import enable_python

conditionals_lp = files("constraint_handler.data").joinpath("conditionals.lp")
direct_lp = files("constraint_handler.data").joinpath("direct.lp")
display_lp = files("constraint_handler.data").joinpath("display.lp")
floats_lp = files("constraint_handler.data").joinpath("floats.lp")
gringoEval_lp = files("constraint_handler.data").joinpath("gringoEval.lp")
main_lp = files("constraint_handler.data").joinpath("main.lp")


def add_constraints(ctrl: Control):
    ctrl.add("base", [], conditionals_lp.read_text())
    ctrl.add("base", [], direct_lp.read_text())
    ctrl.add("base", [], display_lp.read_text())
    ctrl.add("base", [], floats_lp.read_text())
    ctrl.add("base", [], gringoEval_lp.read_text())
    ctrl.add("base", [], main_lp.read_text())


def get_encoding() -> str:
    content = ""
    content = content.__add__(conditionals_lp.read_text())
    content = content.__add__(direct_lp.read_text())
    content = content.__add__(display_lp.read_text())
    content = content.__add__(floats_lp.read_text())
    content = content.__add__(gringoEval_lp.read_text())
    content = content.__add__(main_lp.read_text())
    return content


enable_python()
