"""
Test cases for library functionality.
"""

from clingo import Control
from clingo.ast import ProgramBuilder

import constraint_handler


def test():
    constraint_expr = """
    assign(assign_bike_frame_size, bike_frame_size, constant(int(26))).
    assign(assign_bike_frame_type, bike_frame_type, operation(ite, (operation(eq, (variable(bike_frame_size), (constant(int(26)), ()))), (constant(str("Mountain")), (constant(str("Road")), ()))))).
    """

    ctrl = Control("0")
    pbuilder = ProgramBuilder(ctrl)
    constraint_handler.add_encoding_to_program_builder(pbuilder)

    ctrl.add("base", [], constraint_expr)

    ctrl.ground([("base", [])])
    solve_handle = ctrl.solve(yield_=True)
    for model in solve_handle:
        solution = set()
        for fact in model.symbols(shown=True):
            solution.add(fact.__str__())

        assert solution == {
            "val(bike_frame_size,int,26)",
            'val(bike_frame_type,str,"Mountain")',
        }


def test_add():
    constraint_expr = """
    assign(assign_x, x, constant(int(20))).
    assign(assign_y, y, operation(add, (variable(x), (constant(int(10)), ())))).
    """

    ctrl = Control("0")
    pbuilder = ProgramBuilder(ctrl)
    constraint_handler.add_encoding_to_program_builder(pbuilder)

    ctrl.add("base", [], constraint_expr)

    ctrl.ground([("base", [])])
    solve_handle = ctrl.solve(yield_=True)
    for model in solve_handle:
        solution = set()
        for fact in model.symbols(shown=True):
            solution.add(fact.__str__())

        assert solution == {"val(x,int,20)", "val(y,int,30)"}
