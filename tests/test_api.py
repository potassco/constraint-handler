"""
Test cases for main library functions.
"""

from typing import Iterator, Set

from clingo import Control, Symbol

import constraint_handler


def test_add_ctrl():
    ctrl = Control("0")
    constraint_handler.add_to_control(ctrl)
    ctrl.add("""
    variable_define(assign_x,x,val(int,20)).
    variable_define(assign_y,y,operation(add,(variable(x),(val(int,10),())))).
    #show value/2.
    """)
    ctrl.ground()
    solve_handle = ctrl.solve(yield_=True)
    for model in solve_handle:
        solution = {fact.__str__() for fact in model.symbols(shown=True, theory=True)}
        assert solution == {"value(x,val(int,20))", "value(y,val(int,30))"}


def get_solutions(program: str, use_prop=False) -> Iterator[Set[Symbol]]:
    """
    Helper function to get the solution from a given program.
    """
    ctrl = Control("0")

    if use_prop:
        ctrl.add("defaultEngine(propagator).")

    constraint_handler.add_to_control(ctrl)
    ctrl.add(program)

    ctrl.ground()
    with ctrl.solve(yield_=True) as solve_handle:
        for model in solve_handle:
            solution = set()
            for fact in model.symbols(shown=True, theory=True):
                solution.add(fact.__str__())

            yield solution


def test_prop():
    constraint_expr = """
    variable_define(assign_bike_frame_size, bike_frame_size, val(int,26)).
    variable_define(assign_bike_frame_type, bike_frame_type, operation(ite, (operation(eq, (variable(bike_frame_size), (val(int,26), ()))), (val(str,"Mountain"), (val(str,"Road"), ()))))).
    #show value/2.
    """

    for solution in get_solutions(constraint_expr, True):
        assert solution == {
            "value(bike_frame_size,val(int,26))",
            'value(bike_frame_type,val(str,"Mountain"))',
        }


def test_noprop():
    constraint_expr = """
    variable_define(assign_bike_frame_size, bike_frame_size, val(int,26)).
    variable_define(assign_bike_frame_type, bike_frame_type, operation(ite, (operation(eq, (variable(bike_frame_size), (val(int,26), ()))), (val(str,"Mountain"), (val(str,"Road"), ()))))).
    #show value/2.
    """

    for solution in get_solutions(constraint_expr):
        assert solution == {
            "value(bike_frame_size,val(int,26))",
            'value(bike_frame_type,val(str,"Mountain"))',
        }


def test_add():
    constraint_expr = """
    variable_define(assign_x, x, val(int,20)).
    variable_define(assign_y, y, operation(add, (variable(x), (val(int,10), ())))).
    #show value/2.
    """

    ctrl = Control("0")
    constraint_handler.add_to_control(ctrl)

    ctrl.add("base", [], constraint_expr)

    ctrl.ground([("base", [])])
    solve_handle = ctrl.solve(yield_=True)
    for model in solve_handle:
        solution = set()
        for fact in model.symbols(shown=True, theory=True):
            solution.add(fact.__str__())

        assert solution == {"value(x,val(int,20))", "value(y,val(int,30))"}
