import clingo.script
from clintest.solver import Clingo

import constraint_handler.utils.testing as chut
import constraint_handler.propagator as prop

clingo.script.enable_python()


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
        ["0", "--heuristic=Domain"], "defaultEngine(propagator).", files=[name + ".lp"], propagators=[prop.ConstraintHandlerPropagator]
    )
    test = chut.build_expectations(name)
    solver.solve(test)
    test.assert_()


base_tests = [
    "basic_assignments",
    "booleans",
    "conditional_assign",
    "floats",
    "ints",
    "lambdas",
    "multimaps",
    "nested_set",
    "set_iterations",
    "set_manipulations",
    "set_selfref",
    "strings",
]


def test_engine_compile():
    extra = ["executions", "preferences"]
    unsupported = []
    for test in base_tests + extra:
        if test not in unsupported:
            run_test_compile(test)


def test_engine_ground():
    extra = []
    unsupported = ["lambdas", "multimaps", "nested_set", "set_iterations", "set_manipulations", "set_selfref"]
    for test in base_tests + extra:
        if test not in unsupported:
            run_test_ground(test)


def test_engine_propagator():
    extra = []
    # supported = ["basic_assignments"]
    unsupported = [
        #"basic_assignments",
        #"booleans",
        #"conditional_assign",
        #"floats",
        #"ints",
        "lambdas",
        "multimaps",
        "nested_set",
        "set_iterations",
        "set_manipulations",
        "set_selfref",
        #"strings",
    ]
    for test in base_tests + extra:
        if test not in unsupported:
            run_test_propagator(test)


if __name__ == "__main__":
    test_engine_compile()
    test_engine_ground()
    test_engine_propagator()
