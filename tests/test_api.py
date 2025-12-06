"""
Test cases for main library functions.
"""

from typing import Iterator, Set

from clingo import Control, Symbol
from clingo.ast import ProgramBuilder

import constraint_handler
import constraint_handler.propagator as prop


def test_add_ctrl():
    ctrl = Control("0")
    constraint_handler.add_to_control(ctrl)
    ctrl.add(
        """
    assign(assign_x,x,val(int,20)).
    assign(assign_y,y,operation(add,(variable(x),(val(int,10),())))).
    #show value/3.
    """
    )
    ctrl.ground()
    solve_handle = ctrl.solve(yield_=True)
    for model in solve_handle:
        solution = {fact.__str__() for fact in model.symbols(shown=True, theory=True)}
        assert solution == {"value(x,int,20)", "value(y,int,30)"}


def get_solutions(program: str, use_prop=False) -> Iterator[Set[Symbol]]:
    """
    Helper function to get the solution from a given program.
    """
    ctrl = Control("0")

    if use_prop:
        propagator = prop.ConstraintHandlerPropagator()
        ctrl.register_propagator(propagator)
        ctrl.add("defaultEngine(propagator).")

    pbuilder = ProgramBuilder(ctrl)
    constraint_handler.add_encoding_to_program_builder(pbuilder)
    ctrl.add("base", [], program)

    ctrl.ground([("base", [])])
    with ctrl.solve(yield_=True) as solve_handle:
        for model in solve_handle:
            if use_prop:
                propagator.on_model(model)
            solution = set()
            for fact in model.symbols(shown=True, theory=True):
                solution.add(fact.__str__())

            yield solution


def test_prop():
    constraint_expr = """
    assign(assign_bike_frame_size, bike_frame_size, val(int,26)).
    assign(assign_bike_frame_type, bike_frame_type, operation(ite, (operation(eq, (variable(bike_frame_size), (val(int,26), ()))), (val(str,"Mountain"), (val(str,"Road"), ()))))).
    #show value/3.
    """

    for solution in get_solutions(constraint_expr, True):
        assert solution == {
            "value(bike_frame_size,int,26)",
            'value(bike_frame_type,str,"Mountain")',
        }


def test_noprop():
    constraint_expr = """
    assign(assign_bike_frame_size, bike_frame_size, val(int,26)).
    assign(assign_bike_frame_type, bike_frame_type, operation(ite, (operation(eq, (variable(bike_frame_size), (val(int,26), ()))), (val(str,"Mountain"), (val(str,"Road"), ()))))).
    #show value/3.
    """

    for solution in get_solutions(constraint_expr):
        assert solution == {
            "value(bike_frame_size,int,26)",
            'value(bike_frame_type,str,"Mountain")',
        }


def test_add():
    constraint_expr = """
    assign(assign_x, x, val(int,20)).
    assign(assign_y, y, operation(add, (variable(x), (val(int,10), ())))).
    #show value/3.
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

        assert solution == {"value(x,int,20)", "value(y,int,30)"}
