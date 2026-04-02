from typing import Literal

import pytest

import tests.utils.testing as chut

ctrl_options = ["0", "--heuristic=Domain"]


def run_test(name: str, engine: Literal["compile", "ground", "propagator"], check_mode: bool = False):
    name = "tests/example/" + name
    engine_prg = f"defaultEngine({engine})."
    solver = chut.Solver(ctrl_options, engine_prg, files=[name + ".lp"], propagator_check_only=check_mode)
    test = chut.build_expectations(name)
    solver.solve(test)
    test.assert_()

    for test, extra_args in chut.build_reasoning_mode_expectations(name):
        solver = chut.Solver(ctrl_options + extra_args, engine_prg, files=[name + ".lp"])
        solver.solve(test)
        test.assert_()


base_tests = [
    "basic_assignments",
    "booleans",
    "conditional_assign",
    "custom_globals",
    "empty_variadics",
    "engine_request",
    "engine_request_interaction",
    "engine_request_mult",
    "engine_request_set_ref",
    "eq_compound_int",
    "error_recovery",
    "error_recovery_ensure",
    "executions",
    "execution_assert",
    "execution_conditional",
    "execution_loop",
    "floats",
    "ints",
    "integrity",
    "lambdas",
    "lambda_recursive",
    "lambda_zero_args",
    "multimap_basics",
    "multimap_equality",
    "multimap_executions",
    "multimaps",
    "nested_set",
    "optimize_bools",
    "optimize_floats",
    "optimize_ints",
    "optimize_priority",
    "python_multi_args",
    "reasoning_modes",
    "set_comparisons",
    "set_executions",
    "set_fold_bools",
    "set_from_domain",
    "set_iterations",
    "set_manipulations",
    "set_selfref",
    "strings",
    "type_checking",
    "variable_parallel_declaration",
    "variables",
    "warning_fake_forbid",
    "warning_python",
    "warning_type",
    "warning_variables",
    "warning_variable_confusingName",
    "warning_variable_undeclared",
    "warning_variable_undeclared_statement",
]

compile_extra = [
    "preferences",
    "sum_aggregates",
]
ground_extra = []
propagator_extra = []


@pytest.mark.parametrize(
    "name",
    base_tests + compile_extra,
)
def test_engine_compile(name: str):
    unsupported: list[str] = [
        "engine_request",
        "engine_request_mult",
        "optimize_bools",
        "optimize_floats",
        "optimize_ints",
        "optimize_priority",
        "sum_aggregates",
    ]
    if name not in unsupported:
        run_test(name, "compile")


@pytest.mark.parametrize(
    "name",
    base_tests + ground_extra,
)
def test_engine_ground(name: str):
    unsupported: list[str] = [
        "engine_request",
        "engine_request_mult",
        "lambdas",
        "lambda_recursive",
        "lambda_zero_args",
        "multimap_basics",
        "multimap_equality",
        "multimap_executions",
        "multimaps",
        "optimize_bools",
        "optimize_floats",
        "optimize_ints",
        "optimize_priority",
        "reasoning_modes",
        "set_fold_bools",
        "engine_request_set_ref",
        "set_iterations",
        "set_selfref",
        "type_checking",
    ]
    if name not in unsupported:
        run_test(name, "ground")


@pytest.mark.parametrize(
    ["name", "check_mode"],
    list(zip(base_tests + propagator_extra, [True] * len(base_tests + propagator_extra)))
    + list(zip(base_tests + propagator_extra, [False] * len(base_tests + propagator_extra))),
)
def test_engine_propagator(name, check_mode):
    unsupported: list[str] = [
        "engine_request",
        "engine_request_mult",
        "lambda_recursive",
        "multimaps",
        "optimize_bools",
        "optimize_floats",
        "optimize_ints",
        "optimize_priority",
        "set_fold_bools",
        "set_from_domain",
        "set_iterations",
        "set_selfref",
        "warning_variables",
        "warning_variable_undeclared",
        "type_checking",
    ]
    if name not in unsupported:
        run_test(name, "propagator", check_mode)
