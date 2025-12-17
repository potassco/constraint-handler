import clingo.script
from clintest.solver import Clingo

import constraint_handler.propagator as prop
import constraint_handler.utils.testing as chut

clingo.script.enable_python()

import pytest


def run_test_compile(name):
    name = "tests/example/" + name
    solver = Clingo(["0", "--heuristic=Domain"], "defaultEngine(compile).", files=[name + ".lp"])
    test = chut.build_expectations(name)
    solver.solve(test)
    test.assert_()


def run_test_ground(name):
    name = "tests/example/" + name
    solver = Clingo(["0", "--heuristic=Domain"], "defaultEngine(ground).", files=[name + ".lp"])
    test = chut.build_expectations(name)
    solver.solve(test)
    test.assert_()


def run_test_propagator(name: str, check_mode: bool):
    name = "tests/example/" + name
    solver = chut.SolverWithPropagators(
        ["0", "--heuristic=Domain"],
        "defaultEngine(propagator).",
        files=[name + ".lp"],
        propagators=[lambda: prop.ConstraintHandlerPropagator(check_mode)],
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
    # "lambdas",
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
    "variables",
]

compile_extra = ["preferences"]
ground_extra = []
propagator_extra = []


@pytest.mark.parametrize(
    "name",
    base_tests + compile_extra,
)
def test_engine_compile(name: str):
    unsupported = ["optimize_bools", "optimize_floats", "optimize_ints", "multimap_basics"]

    if name in unsupported:
        return

    run_test_compile(name)


@pytest.mark.parametrize(
    "name",
    base_tests + ground_extra,
)
def test_engine_ground(name: str):
    unsupported = [
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
    if name in unsupported:
        return

    run_test_ground(name)


@pytest.mark.parametrize(
    ["name", "check_mode"],
    list(zip(base_tests + propagator_extra, [True] * len(base_tests + propagator_extra)))
    + list(zip(base_tests + propagator_extra, [False] * len(base_tests + propagator_extra))),
)
def test_engine_propagator(name, check_mode):
    unsupported = [
        "lambda_recursive",
        "multimap_basics",
        "multimaps",
        "optimize_bools",
        "optimize_floats",
        "optimize_ints",
        "set_iterations",
        "set_selfref",
        "lambdas",
        "multimap_basics",
    ]
    if name in unsupported:
        return

    run_test_propagator(name, check_mode)
