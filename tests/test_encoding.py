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


def run_test_propagator(name):
    name = "tests/example/" + name
    solver = chut.SolverWithPropagators(
        ["0", "--heuristic=Domain"],
        "defaultEngine(propagator).",
        files=[name + ".lp"],
        propagators=[prop.ConstraintHandlerPropagator],
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


def test_engine_compile():
    extra = ["preferences"]
    unsupported = ["optimize_bools", "optimize_floats", "optimize_ints"]
    for test in base_tests + extra:
        if test not in unsupported:
            run_test_compile(test)


def test_engine_ground():
    extra = []
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
    for test in base_tests + extra:
        if test not in unsupported:
            run_test_ground(test)

# def test_engine_propagator():
#     extra = []
#     unsupported = [
#         "lambda_recursive",
#         "multimaps",
#         "optimize_bools",
#         "optimize_floats",
#         "optimize_ints",
#         "set_iterations",
#         "set_selfref",
#         "lambdas",
#         "multimap_basics",
#     ]
#     for test in base_tests + extra:
#         if test not in unsupported:
#             run_test_propagator(test)

@pytest.mark.parametrize(["name", "check_mode"], list(zip(base_tests, [True]*len(base_tests))) + list(zip(base_tests, [False]*len(base_tests))))
def test_propagator(name, check_mode):
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
    
    name = "tests/example/" + name
    solver = chut.SolverWithPropagators(
        ["0", "--heuristic=Domain"],
        "defaultEngine(propagator).",
        files=[name + ".lp"],
        propagators=[lambda : prop.ConstraintHandlerPropagator(check_mode)],
    )
    test = chut.build_expectations(name)
    solver.solve(test)
    test.assert_()


if __name__ == "__main__":
    test_engine_compile()
    test_engine_ground()
    test_engine_propagator()
