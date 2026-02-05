import pytest

import constraint_handler.utils.testing as chut

ctrl_options = ["0", "--heuristic=Domain"]


def run_test_compile(name):
    name = "tests/example/" + name
    solver = chut.Solver(ctrl_options, "defaultEngine(compile).", files=[name + ".lp"])
    test = chut.build_expectations(name)
    solver.solve(test)
    test.assert_()


def run_test_ground(name):
    name = "tests/example/" + name
    solver = chut.Solver(ctrl_options, "defaultEngine(ground).", files=[name + ".lp"])
    test = chut.build_expectations(name)
    solver.solve(test)
    test.assert_()


def run_test_propagator(name: str, check_mode: bool):
    name = "tests/example/" + name
    solver = chut.Solver(
        ctrl_options,
        "defaultEngine(propagator).",
        files=[name + ".lp"],
        propagator_check_only=check_mode,
    )
    test = chut.build_expectations(name)
    solver.solve(test)
    test.assert_()


base_tests = [
    "basic_assignments",
    "booleans",
    "conditional_assign",
    "custom_globals",
    "executions",
    "execution_assert",
    "execution_conditional",
    "execution_loop",
    "floats",
    "ints",
    "integrity",
    "lambdas",
    "lambda_recursive",
    "multimap_basics",
    "multimaps",
    "nested_set",
    "optimize_bools",
    "optimize_floats",
    "optimize_ints",
    "set_iterations",
    "set_manipulations",
    "set_selfref",
    "strings",
    # "type_checking",
    "variable_parallel_declaration",
    "variables",
    "warning_python",
    "warning_type",
    "warning_variables",
    "warning_variable_undeclared",
    "warning_variable_undeclared_statement",
]

compile_extra = ["preferences"]
ground_extra = []
propagator_extra = []


@pytest.mark.parametrize(
    "name",
    base_tests + compile_extra,
)
def test_engine_compile(name: str):
    unsupported: list[str] = ["optimize_bools", "optimize_floats", "optimize_ints"]
    if name not in unsupported:
        run_test_compile(name)


@pytest.mark.parametrize(
    "name",
    base_tests + ground_extra,
)
def test_engine_ground(name: str):
    unsupported: list[str] = [
        "lambdas",
        "lambda_recursive",
        "multimap_basics",
        "multimaps",
        "optimize_bools",
        "optimize_floats",
        "optimize_ints",
        "set_iterations",
        "set_selfref",
    ]
    if name not in unsupported:
        run_test_ground(name)


@pytest.mark.parametrize(
    ["name", "check_mode"],
    list(zip(base_tests + propagator_extra, [True] * len(base_tests + propagator_extra)))
    + list(zip(base_tests + propagator_extra, [False] * len(base_tests + propagator_extra))),
)
def test_engine_propagator(name, check_mode):
    unsupported: list[str] = [
        "lambda_recursive",
        "multimaps",
        "optimize_bools",
        "optimize_floats",
        "optimize_ints",
        "set_iterations",
        "set_selfref",
        "variable_parallel_declaration",
        "warning_python",
        "warning_type",
        "warning_variables",
        "warning_variable_undeclared",
        "warning_variable_undeclared_statement",
    ]
    if name not in unsupported:
        run_test_propagator(name, check_mode)
