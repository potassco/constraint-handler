from typing import Literal

import clingo
import pytest

import constraint_handler
import tests.utils.testing as chut

ctrl_options = ["0", "--heuristic=Domain"]


def solve_with_clingo_statistics(name: str, engine: Literal["compile", "ground", "propagator"] = "compile") -> dict:
    ctl = clingo.Control(["--stats=2"])
    constraint_handler.add_to_control(ctl)
    ctl.add(f"defaultEngine({engine}).")
    ctl.load(f"tests/correctness/{name}.lp")
    ctl.ground()

    result = ctl.solve()
    assert result.satisfiable

    return ctl.statistics


def run_test(name: str, engine: Literal["compile", "ground", "propagator"], check_mode: bool = False):
    name = "tests/correctness/" + name
    engine_prg = f"defaultEngine({engine})."
    solver = chut.Solver(ctrl_options, engine_prg, files=[name + ".lp"], propagator_check_only=check_mode)
    test = chut.build_expectations(name)
    solver.solve(test)
    test.assert_()

    for test, extra_args in chut.build_expectations_with_args(name):
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
    "execution/python_integrity",
    "expression/bad_equality",
    "expression/lambdas",
    "expression/lambda_recursive",
    "expression/lambda_zero_args",
    "expression/python",
    "expression/python_multi_args",
    "expression/tuple",
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
    "variable/variables_same_val_multi_expr",
    "warning/bad",
    "warning/fake_forbid",
    "warning/python",
    "warning/python_unsupported_type",
    #    pytest.param(
    #        "warning/statement_python_declared_output",
    #        marks=pytest.mark.xfail(reason="known failing regression for statement_python declared outputs"),
    #    ),
    "warning/statement_malformed",
    "warning/syntax",
    "warning/type",
    "warning/variables",
    "warning/variable_confusing_name",
    "warning/variable_undeclared",
    "warning/variable_undeclared_statement",
]

compile_extra = [
    "optimization/labeled_values",
    "optimization/none_as_zero",
    "optimization/preferences",
    "optimization/floats_precision",
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
    [(n, c) for c in [True, False] for n in base_tests + propagator_extra],
    #    list(zip(base_tests + propagator_extra, [True] * len(base_tests + propagator_extra)))
    #    + list(zip(base_tests + propagator_extra, [False] * len(base_tests + propagator_extra))),
)
def test_engine_propagator(name: str, check_mode):
    unsupported: list[str] = [
        "core/type_checking",
        "datatype/bool_evaluate",
        "engine/request",
        "engine/request_mult",
        "execution/python_integrity",
        "expression/lambda_recursive",
        "multimap/main",
        "set/fold_bools",
        "set/iterations",
        "set/selfref",
        "warning/python_unsupported_type",
        "warning/variables",
        "warning/variable_undeclared",
    ]
    print(name, check_mode)
    if name not in unsupported:
        run_test(name, "propagator", check_mode)


choice_statistics_tests = [
    "core/basic_assignments",
    "core/custom_globals",
    "core/empty_variadics",
    "engine/request",
    "engine/request_interaction",
    "engine/request_mult",
    "engine/request_set_ref",
    "datatype/int_eq_compound",
    "error/recovery",
    "example2",
    "example3",
    "expression/python",
    "datatype/floats",
    "datatype/ints",
    "expression/lambda_recursive",
    "expression/lambdas",
    "expression/lambda_zero_args",
    "multimap/basics",
    "multimap/equality",
    "multimap/executions",
    "multimap/main",
    "set/nested",
    "expression/python_multi_args",
    "set/comparisons",
    "set/executions",
    "set/fold_bools",
    "set/iterations",
    "set/manipulations",
    "testAddition",
    "warning/statement_malformed",
    "warning/syntax",
    "warning/variable_confusing_name",
    "warning/variable_undeclared_statement",
]


@pytest.mark.parametrize("name", choice_statistics_tests)
def test_compile_statistics_have_zero_choices(name: str):
    statistics = solve_with_clingo_statistics(name)
    assert statistics["solving"]["solvers"]["choices"] == 0.0


tightness_statistics_tests = [
    "core/basic_assignments",
    pytest.param("datatype/booleans", marks=pytest.mark.xfail(reason="tightness: sccs != 0.0")),
    "datatype/bool_equivalence_bad",
    "datatype/bool_evaluate",
    pytest.param("core/conditional_assign", marks=pytest.mark.xfail(reason="tightness: sccs != 0.0")),
    "core/custom_globals",
    "core/empty_variadics",
    "engine/request",
    "engine/request_interaction",
    "engine/request_mult",
    "engine/request_set_ref",
    "datatype/int_eq_compound",
    "error/recovery",
    "error/recovery_ensure",
    "expression/bad_equality",
    "expression/python",
    "execution/main",
    "execution/assert",
    pytest.param("execution/conditional", marks=pytest.mark.xfail(reason="tightness: sccs != 0.0")),
    "execution/loop",
    pytest.param("execution/optional_run", marks=pytest.mark.xfail(reason="tightness: sccs != 0.0")),
    "datatype/floats",
    "datatype/ints",
    pytest.param("core/integrity", marks=pytest.mark.xfail(reason="tightness: sccs != 0.0")),
    "expression/lambdas",
    "expression/lambda_recursive",
    "expression/lambda_zero_args",
    "multimap/basics",
    "multimap/equality",
    "multimap/executions",
    "multimap/main",
    "set/nested",
    pytest.param("optimization/bools", marks=pytest.mark.xfail(reason="tightness: sccs != 0.0")),
    pytest.param("optimization/floats", marks=pytest.mark.xfail(reason="tightness: sccs != 0.0")),
    pytest.param("optimization/ints", marks=pytest.mark.xfail(reason="tightness: sccs != 0.0")),
    pytest.param("optimization/priority", marks=pytest.mark.xfail(reason="tightness: sccs != 0.0")),
    "set/membership_decomposed",
    "set/membership_python",
    "expression/python_multi_args",
    "core/reasoning_modes",
    "set/comparisons",
    "set/executions",
    "set/fold_bools",
    pytest.param("set/from_domain", marks=pytest.mark.xfail(reason="tightness: sccs != 0.0")),
    "set/iterations",
    "set/manipulations",
    pytest.param("set/selfref", marks=pytest.mark.xfail(reason="tightness: sccs != 0.0")),
    pytest.param("datatype/strings", marks=pytest.mark.xfail(reason="tightness: sccs != 0.0")),
    pytest.param("core/type_checking", marks=pytest.mark.xfail(reason="tightness: sccs != 0.0")),
    "variable/parallel_declaration",
    pytest.param("variable/flexible_domain", marks=pytest.mark.xfail(reason="tightness: sccs != 0.0")),
    "variable/main",
    "warning/bad",
    "warning/fake_forbid",
    pytest.param("warning/python", marks=pytest.mark.xfail(reason="tightness: sccs != 0.0")),
    "warning/python_unsupported_type",
    "warning/statement_malformed",
    "warning/syntax",
    "warning/type",
    "warning/variables",
    "warning/variable_confusing_name",
    "warning/variable_undeclared",
    "warning/variable_undeclared_statement",
]


@pytest.mark.parametrize("name", tightness_statistics_tests)
def test_compile_statistics_are_tight(name: str):
    statistics = solve_with_clingo_statistics(name)
    assert statistics["problem"]["lp"]["sccs"] == 0.0
