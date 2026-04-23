from typing import Literal

import pytest

import tests.utils.testing as chut

ctrl_options = ["0", "--heuristic=Domain"]


def run_test(name: str, engine: Literal["compile", "ground", "propagator"], check_mode: bool = False):
    name = "tests/correctness/" + name
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
    "core/basic_assignments",
    "core/conditional_assign",
    "core/custom_globals",
    "core/empty_variadics",
    "core/integrity",
    "core/reasoning_modes",
    "core/type_checking",
    "datatype/booleans",
    "datatype/bool_equivalence_bad",
    "datatype/bool_evaluate",
    "datatype/int_eq_compound",
    "datatype/ints",
    "datatype/floats",
    "datatype/strings",
    "engine/request",
    "engine/request_interaction",
    "engine/request_mult",
    "engine/request_set_ref",
    "error/recovery",
    "error/recovery_ensure",
    "execution/main",
    "execution/assert",
    "execution/conditional",
    "execution/loop",
    "execution/optional_run",
    "expression/bad_equality",
    "expression/python",
    "expression/lambdas",
    "expression/lambda_recursive",
    "expression/lambda_zero_args",
    "expression/python_multi_args",
    "multimap/basics",
    "multimap/equality",
    "multimap/executions",
    "multimap/main",
    "optimization/bools",
    "optimization/floats",
    "optimization/ints",
    "optimization/priority",
    "set/membership_decomposed",
    "set/membership_python",
    "set/nested",
    "set/comparisons",
    "set/executions",
    "set/fold_bools",
    "set/from_domain",
    "set/iterations",
    "set/manipulations",
    "set/selfref",
    "variable/parallel_declaration",
    "variable/flexible_domain",
    "variable/main",
    "warning/bad",
    "warning/fake_forbid",
    "warning/python",
    "warning/python_unsupported_type",
    "warning/statement_malformed",
    "warning/syntax",
    "warning/type",
    "warning/variables",
    "warning/variable_confusing_name",
    "warning/variable_undeclared",
    "warning/variable_undeclared_statement",
]

compile_extra = [
    "optimization/preferences",
]
ground_extra = []
propagator_extra = []


@pytest.mark.parametrize(
    "name",
    base_tests + compile_extra,
)
def test_engine_compile(name: str):
    unsupported: list[str] = [
        "engine/request",
        "engine/request_mult",
        "optimization/bools",
        "optimization/floats",
        "optimization/ints",
        "optimization/priority",
        "warning/syntax",
    ]
    if name not in unsupported:
        run_test(name, "compile")


@pytest.mark.parametrize(
    "name",
    base_tests + ground_extra,
)
def test_engine_ground(name: str):
    unsupported: list[str] = [
        "core/reasoning_modes",
        "core/type_checking",
        "engine/request",
        "engine/request_mult",
        "expression/lambdas",
        "expression/lambda_recursive",
        "expression/lambda_zero_args",
        "multimap/basics",
        "multimap/equality",
        "multimap/executions",
        "multimap/main",
        "optimization/bools",
        "optimization/floats",
        "optimization/ints",
        "optimization/priority",
        "set/fold_bools",
        "engine/request_set_ref",
        "set/iterations",
        "set/selfref",
        "warning/syntax",
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
        "core/type_checking",
        "datatype/bool_evaluate",
        "engine/request",
        "engine/request_mult",
        "expression/lambda_recursive",
        "multimap/main",
        "optimization/bools",
        "optimization/floats",
        "optimization/ints",
        "optimization/priority",
        "set/fold_bools",
        "set/iterations",
        "set/selfref",
        "warning/python_unsupported_type",
        "warning/variables",
        "warning/variable_undeclared",
    ]
    if name not in unsupported:
        run_test(name, "propagator", check_mode)
