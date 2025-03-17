"""
Test cases for main application functionality.
"""

from clingo import Control

from constraint_handler import get_encoding


def test():

    constraint_expr = """
    assign(assign_bike_frame_size, bike_frame_size, constant(int(26))).
    assign(assign_bike_frame_type, bike_frame_type, operation(ite, (operation(eq, (variable(bike_frame_size), (constant(int(26)), ()))), (constant(str("Mountain")), (constant(str("Road")), ()))))).
    """

    encoding = get_encoding()
    ctrl = Control("0")
    ctrl.add("base", [], encoding)
    ctrl.add("base", [], constraint_expr)
    ctrl.ground([("base", [])])
    solve_handle = ctrl.solve(yield_=True)
    for model in solve_handle:
        solution = set()
        for fact in model.symbols(shown=True):
            solution.add(fact.__str__())

        assert solution == {"val(bike_frame_size,int,26)", 'val(bike_frame_type,str,"Mountain")'}
