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
    "datatype/booleans_xyftz",
    "datatype/bool_equivalence_bad",
    "datatype/bool_evaluate",
    "datatype/bool_negation",
    "datatype/int_eq_compound",
    "datatype/ints",
    "datatype/floats",
    "datatype/strings",
    "engine/request",
    "engine/request_interaction",
    "engine/request_mixed_trig",
    "engine/request_mult",
    "engine/request_set_ref",
    "error/recovery",
    "error/recovery_conditionals",
    "error/recovery_ensure",
    "execution/change",
    "execution/main_absolut",
    "execution/main_pyt",
    "execution/main_swap",
    "execution/assert",
    "execution/conditional",
    "execution/conditional_assert",
    "execution/optional_run",
    "execution/python_integrity",
    "expression/bad_equality",
    "expression/lambdas",
    "expression/lambda_recursive",
    "expression/lambda_zero_args",
    "expression/python",
    "expression/python_multi_args",
    "expression/python_extract",
    "expression/python_extract_binding_leak",
    "expression/tuple",
    "expression/tuple_arity_mismatch",
    "multimap/basics",
    "multimap/equality",
    "multimap/executions",
    "multimap/main",
    "optimization/bools",
    "optimization/floats",
    "optimization/floats_precision",
    "optimization/ints",
    "optimization/labeled_values",
    "optimization/none_as_zero",
    "optimization/preferences",
    "optimization/priority",
    "set/membership_decomposed",
    "set/membership_nested",
    "set/membership_python",
    "set/nested",
    "set/comparisons",
    "set/executions",
    "set/fold_bools",
    "set/from_domain",
    "set/iterations",
    "set/manipulations",
    "set/same_val_multi_expr",
    "set/selfref",
    "variable/parallel_declaration",
    "variable/flexible_domain",
    "variable/main",
    "variable/same_val_multi_expr",
    "warning/bad",
    "warning/fake_forbid",
    "warning/ignore",
    "warning/python",
    "warning/python_unsupported_type",
    "warning/statement_malformed",
    "warning/syntax",
    "warning/type",
    "warning/variables",
    "warning/variable_confusing_name",
    "warning/variable_reservedName",
    "warning/variable_undeclared",
    "warning/variable_undeclared_python_extract",
    "warning/variable_undeclared_statement",
]

compile_skip: list[str] = []
compile_xfail: list[str] = [
    "engine/request",
]
ground_skip: list[str] = [
    "set/selfref",
]
ground_xfail: list[str] = [
    "core/reasoning_modes",
    "engine/request",
    "engine/request_mixed_trig",
    "engine/request_set_ref",
    "expression/lambdas",
    "expression/lambda_recursive",
    "expression/lambda_zero_args",
    "multimap/basics",
    "multimap/equality",
    "multimap/executions",
    "multimap/main",
    "optimization/bools",
    "optimization/floats",
    "optimization/floats_precision",
    "optimization/ints",
    "optimization/labeled_values",
    "optimization/priority",
    "set/fold_bools",
    "set/iterations",
]

propagator_skip: list[str] = []
propagator_xfail: list[str] = [
    "engine/request",
    "engine/request_mixed_trig",
    "execution/python_integrity",
    "expression/lambda_recursive",
    "multimap/main",
    "optimization/floats_precision",
    "optimization/labeled_values",
    "optimization/preferences",
    "set/fold_bools",
    "set/iterations",
    "set/selfref",
    "warning/python_unsupported_type",
]


def mark_for_engine(name: str, skip: set[str], xfail: set[str], engine: str):
    if name in skip:
        return pytest.mark.skip(reason=f"skipped in {engine} engine")
    if name in xfail:
        return pytest.mark.xfail(reason=f"known failure in {engine} engine")
    return None


def mark_param_for_engine(name: str, skip: set[str], xfail: set[str], engine: str):
    mark = mark_for_engine(name, skip, xfail, engine)
    if mark is not None:
        return pytest.param(name, marks=mark)
    return name


@pytest.mark.parametrize(
    "name",
    [mark_param_for_engine(name, compile_skip, compile_xfail, "compile") for name in base_tests],
)
def test_engine_compile(name: str):
    run_test(name, "compile")


@pytest.mark.parametrize(
    "name",
    [mark_param_for_engine(name, ground_skip, ground_xfail, "ground") for name in base_tests],
)
def test_engine_ground(name: str):
    run_test(name, "ground")


@pytest.mark.parametrize(
    ["name", "check_mode"],
    [
        (
            pytest.param(n, c, marks=mark_for_engine(n, propagator_skip, propagator_xfail, "propagator"))
            if mark_for_engine(n, propagator_skip, propagator_xfail, "propagator") is not None
            else (n, c)
        )
        for c in [True, False]
        for n in base_tests
    ],
)
def test_engine_propagator(name: str, check_mode):
    run_test(name, "propagator", check_mode)


choice_statistics_skip: list[str] = []
choice_statistics_xfail: list[str] = [
    "core/conditional_assign",
    "core/integrity",
    "core/reasoning_modes",
    "core/type_checking",
    "datatype/booleans_xyftz",
    "datatype/bool_equivalence_bad",
    "datatype/bool_evaluate",
    "datatype/bool_negation",
    "datatype/strings",
    "error/recovery_ensure",
    "execution/change",
    "execution/main_absolut",
    "execution/main_swap",
    "execution/assert",
    "execution/conditional",
    "execution/optional_run",
    "execution/python_integrity",
    "expression/bad_equality",
    "optimization/bools",
    "optimization/floats",
    "optimization/floats_precision",
    "optimization/ints",
    "optimization/labeled_values",
    "optimization/none_as_zero",
    "optimization/preferences",
    "optimization/priority",
    "set/membership_decomposed",
    "set/membership_python",
    "set/from_domain",
    "set/same_val_multi_expr",
    "set/selfref",
    "variable/parallel_declaration",
    "variable/flexible_domain",
    "variable/main",
    "variable/same_val_multi_expr",
    "warning/bad",
    "warning/fake_forbid",
    "warning/python",
    "warning/type",
    "warning/variables",
    "warning/variable_reservedName",
    "warning/variable_undeclared",
]


@pytest.mark.parametrize(
    "name",
    [
        mark_param_for_engine(
            name,
            choice_statistics_skip,
            choice_statistics_xfail,
            "compile statistics choices",
        )
        for name in base_tests
    ],
)
def test_compile_statistics_have_zero_choices(name: str):
    statistics = solve_with_clingo_statistics(name)
    assert statistics["solving"]["solvers"]["choices"] == 0.0


tightness_statistics_skip: set[str] = []
tightness_statistics_xfail: set[str] = [
    "optimization/floats_precision",
    "optimization/labeled_values",
    "optimization/none_as_zero",
    "optimization/bools",
    "optimization/floats",
    "optimization/ints",
    "optimization/priority",
]


@pytest.mark.parametrize(
    "name",
    [
        mark_param_for_engine(
            name,
            tightness_statistics_skip,
            tightness_statistics_xfail,
            "compile statistics tightness",
        )
        for name in base_tests
    ],
)
def test_compile_statistics_are_tight(name: str):
    statistics = solve_with_clingo_statistics(name)
    assert statistics["problem"]["lp"]["sccs"] == 0.0
