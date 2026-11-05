import pytest
from clingo import Control, parse_term

import constraint_handler
import constraint_handler.engine as engine


@pytest.mark.parametrize("reasoning_mode", ["brave", "cautious"])
@pytest.mark.parametrize(
    "selected_engine",
    [
        pytest.param(
            engine.propagator,
            marks=pytest.mark.xfail(
                strict=True, raises=AssertionError, reason="Repeated reasoning-mode solves lose propagator set values"
            ),
            id="propagator",
        ),
        pytest.param(engine.propagator_check, id="propagator-check"),
    ],
)
def test_repeated_solve_set_values(selected_engine, reasoning_mode):
    control = Control(["0", "--heuristic=Domain", f"--enum-mode={reasoning_mode}"])
    constraint_handler.add_to_control(control, engine=selected_engine)
    control.add("""
    variable_declare(s,set).
    set_assign(s,val(int,1)).
    """)
    control.ground()
    expected = {
        parse_term("value(s,ref(set,variable(s)))"),
        parse_term("set_value(s,val(int,1))"),
    }

    for solve_number in range(1, 3):
        final_values = set()
        with control.solve(yield_=True) as handle:
            for model in handle:
                final_values = set(constraint_handler.find_values(model))
        assert expected <= final_values, f"Solve {solve_number} lost set values: {final_values}"
