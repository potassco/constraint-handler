"""
Test cases for main library functions.
"""

from typing import Iterator, Set

import pytest
from clingo import Control, Function, Symbol, parse_term

import constraint_handler
import constraint_handler.engine as engine
from constraint_handler.schemas.expression import Val
from constraint_handler.schemas.result import Value


def test_add_ctrl():
    ctrl = Control("0")
    constraint_handler.add_to_control(ctrl)
    ctrl.add("""
    variable_define(x,val(int,20)).
    variable_define(y,operation(add,(variable(x),(val(int,10),()))),val(bool,true),assign_y).
    #show value/2.
    """)
    ctrl.ground()
    solve_handle = ctrl.solve(yield_=True)
    for model in solve_handle:
        solution = {fact.__str__() for fact in model.symbols(shown=True, theory=True)}
        assert solution == {"value(x,val(int,20))", "value(y,val(int,30))"}


@pytest.mark.parametrize(
    "value, expected",
    [
        ("val(int,0)", 0),
        ("val(int,-3)", -3),
        ('val(float,float("3.25"))', 3.25),
        ('val(string,"hello")', "hello"),
        ('val(string,"")', ""),
        ("val(bool,true)", True),
        ("val(bool,false)", False),
        ("val(none,none)", None),
        ("val(symbol,example(1))", parse_term("example(1)")),
        ("val(symbol,3)", parse_term("3")),
        ('val(symbol,"hello")', parse_term('"hello"')),
        ("val(symbol,true)", Function("true")),
    ],
)
def test_find_python_values_scalars(value, expected):
    control = Control()
    control.add(f'value("x",{value}).')
    control.ground()

    with control.solve(yield_=True) as handle:
        model = handle.model()
        values = constraint_handler.find_python_values(model)
        raw = constraint_handler.find_values(model)

    assert values == {"x": expected}
    assert type(values["x"]) is type(expected)
    assert len(raw) == 1
    record = raw[parse_term(f'value("x",{value})')]
    assert isinstance(record, Value)
    assert isinstance(record.val, Val)


@pytest.mark.parametrize(
    "program, expected",
    [
        pytest.param(
            'value("x",ref(set,s)). set_value(s,val(int,1)). set_value(s,val(int,2)).',
            frozenset({1, 2}),
            marks=pytest.mark.xfail(
                strict=True, raises=NotImplementedError, reason="Native set conversion is not implemented"
            ),
            id="set",
        ),
        pytest.param(
            'value("x",ref(multimap,m)). multimap_value(m,val(string,"key"),val(int,1)).',
            {"key": 1},
            marks=pytest.mark.xfail(
                strict=True, raises=NotImplementedError, reason="Native multimap conversion is not implemented"
            ),
            id="multimap",
        ),
    ],
)
def test_find_python_values_collections(program, expected):
    control = Control()
    control.add(program)
    control.ground()

    with control.solve(yield_=True) as handle:
        values = constraint_handler.find_python_values(handle.model())

    assert values == {"x": expected}


def test_find_python_values_ignores_non_assignments():
    control = Control()
    control.add("""
    value(x,val(int,3)).
    evaluated(val(int,3),val(int,3)).
    optimize_value("price",0,val(int,7)).
    """)
    control.ground()

    with control.solve(yield_=True) as handle:
        assert constraint_handler.find_python_values(handle.model()) == {Function("x"): 3}


def get_solutions(program: str, use_prop=False) -> Iterator[Set[Symbol]]:
    """
    Helper function to get the solution from a given program.
    """
    ctrl = Control("0")
    constraint_handler.add_to_control(ctrl, engine=engine.propagator if use_prop else engine.compile)
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
    variable_define(bike_frame_size,val(int,26),val(bool,true),assign_bike_frame_size).
    variable_define(bike_frame_type,operation(ite,(operation(eq,(variable(bike_frame_size),(val(int,26),()))),(val(string,"Mountain"),(val(string,"Road"), ())))),val(bool,true),assign_bike_frame_type).
    #show value/2.
    """

    for solution in get_solutions(constraint_expr, True):
        assert solution == {
            "value(bike_frame_size,val(int,26))",
            'value(bike_frame_type,val(string,"Mountain"))',
        }


def test_noprop():
    constraint_expr = """
    variable_define(bike_frame_size,val(int,26),val(bool,true),assign_bike_frame_size).
    variable_define(bike_frame_type,operation(ite,(operation(eq,(variable(bike_frame_size),(val(int,26),()))),(val(string,"Mountain"),(val(string,"Road"),())))),val(bool,true),assign_bike_frame_type).
    #show value/2.
    """

    for solution in get_solutions(constraint_expr):
        assert solution == {
            "value(bike_frame_size,val(int,26))",
            'value(bike_frame_type,val(string,"Mountain"))',
        }


def test_add():
    constraint_expr = """
    variable_define(x,val(int,20),val(bool,true),assign_x).
    variable_define(y,operation(add,(variable(x),(val(int,10),()))),val(bool,true),assign_y).
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
