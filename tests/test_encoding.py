from typing import Literal

import clingo
import pytest

import constraint_handler
import tests.utils.testing as chut

ctrl_options = ["0", "--heuristic=Domain"]


def solve_with_clingo_statistics(
    name: str, engine: Literal["compile", "compile2", "ground", "propagator"] = "compile"
) -> dict:
    ctl = clingo.Control(["--stats=2"])
    constraint_handler.add_to_control(ctl)
    ctl.add(f"defaultEngine({engine}).")
    ctl.load(f"tests/correctness/{name}.lp")
    ctl.ground()

    result = ctl.solve()
    assert result.satisfiable

    return ctl.statistics


def run_test(name: str, engine: Literal["compile", "compile2", "ground", "propagator"], check_mode: bool = False):
    name = "tests/correctness/" + name
    engine_prg = f"defaultEngine({engine})."
    for test, extra_args in chut.build_expectations(name):
        options = ctrl_options + extra_args
        solver = chut.Solver(options, engine_prg, files=[name + ".lp"], propagator_check_only=check_mode)
        solver.solve(test)
        test.assert_()


base_tests = [
    "core/basic_assignments",
    "core/empty_set_execution",
    "core/conditional_assign",
    "core/custom_globals",
    "core/empty_variadics",
    "core/integrity",
    "core/optional_absent_comparison_evaluation",
    "core/optional_absent_string_comparison_evaluation",
    "core/conj_bad_none_recovery",
    "core/python_set_bool_brave",
    "core/python_extract_set_projection",
    "core/python_extract_statement_error_warning",
    "core/reasoning_modes",
    "core/python_extract_tuple_projection",
    "core/shared_optional_output_domains",
    "core/set_interface_value_marker",
    "core/set_execution_input_alias",
    "core/unprojected_optional_equality",
    "datatype/bool/conj_disj",
    "datatype/bool/conj_disj_bad",
    "datatype/bool/conj_disj_mixed",
    "datatype/bool/conj_disj_none",
    "datatype/bool/conj_disj_variadic",
    "datatype/bool/derived_relations",
    "datatype/bool/equivalence_bad",
    "datatype/bool/evaluate",
    "datatype/bool/implication_bad",
    "datatype/bool/negation_logical_bad",
    "datatype/bool/negation_logical_basic",
    "datatype/bool/negation_logical_none",
    "datatype/bool/negation_strong_bad",
    "datatype/bool/negation_strong_basic",
    "datatype/bool/negation_strong_none",
    "datatype/bool/negation_weak_bad",
    "datatype/bool/negation_weak_basic",
    "datatype/bool/negation_weak_none",
    "datatype/float/division",
    "datatype/float/division_with_int",
    "datatype/float/equality_basic",
    "datatype/float/equality_cross_type",
    "datatype/float/extrema",
    "datatype/float/ordering_cross_type",
    "datatype/float/ordering_with_int",
    "datatype/float/rounding",
    "datatype/int/abs",
    "datatype/int/arithmetic_add_mul_basic",
    "datatype/int/arithmetic_sub_basic",
    "datatype/int/comparison",
    "datatype/int/division",
    "datatype/int/equality_compound_basic",
    "datatype/int/equality_cross_type",
    "datatype/int/extrema",
    "datatype/int/minus",
    "datatype/int/ordering_cross_type",
    "datatype/int/power",
    "datatype/strings",
    "engine/request",
    "engine/request_interaction",
    "engine/request_mixed_trig",
    "engine/request_mult",
    "engine/request_set_ref",
    "error/recovery_bool",
    "error/recovery_conditionals",
    "error/recovery_ensure",
    "error/recovery",
    "execution/change",
    "execution/implicit_variable",
    "execution/main_absolut",
    "execution/main_pyt",
    "execution/main_swap",
    "execution/assert",
    "execution/conditional",
    "execution/conditional_string_equality_single_model",
    "execution/conditional_assert",
    "execution/python_integrity_should_be_ignored",
    "execution/optional_run",
    "execution/python_integrity",
    "execution/python_list",
    "execution/python_set_empty_equality",
    "expression/bad_equality",
    "expression/lambdas",
    "expression/lambda_recursive",
    "expression/lambda_zero_args",
    "expression/python",
    "expression/python_multi_args",
    "expression/python_extract",
    "expression/python_extract_binding_leak",
    "expression/tuple_arity_mismatch",
    "expression/tuple_nested",
    "expression/tuple",
    "python/static",
    "python/dynamic",
    "python/bad",
    "python/set_input",
    "python/set_output",
    "python/extract_static",
    "python/extract_dynamic",
    "python/extract_bad",
    "python/extract_succeeds",
    "python/extract_set_input",
    "python/extract_set_output",
    "multimap/basics",
    "multimap/equality",
    "multimap/executions",
    "multimap/main",
    "optimization/multimap_bool",
    "optimization/multimap_float",
    "optimization/multimap_float_precision",
    "optimization/multimap_int",
    "core/boolean_shortcut_optional_presence",
    "optimization/multimap_labeled_values",
    "optimization/no_multimap_bool",
    "optimization/no_multimap_float",
    "optimization/no_multimap_float_precision",
    "optimization/no_multimap_int",
    "optimization/no_multimap_labeled_values",
    "optimization/optional_absent_linked_value",
    "optimization/preferences",
    "optimization/priority",
    "set/comparisons",
    "set/membership_decomposed",
    "set/membership_nested",
    "set/membership_python",
    "set/nested",
    "set/executions",
    "set/fold_bools",
    "set/from_domain",
    "set/missing_declare_repair",
    "set/iterations",
    "set/length_flat",
    "set/diff_flat",
    "set/eq_neq_flat",
    "set/inter_flat",
    "set/manipulation_flat",
    "set/manipulations",
    "set/nondet_simple",
    "set/overapprox_boundaries",
    "set/set_in_set_notin",
    "set/set_make_flat",
    "set/same_val_multi_expr",
    "set/subset_flat",
    "set/selfref",
    "set/union_flat",
    "type/checking/invalid",
    "type/checking/multimap",
    "type/checking/none_bool",
    "type/checking/numeric",
    "type/checking/set",
    "type/checking/string_symbol",
    "type/python_extract/non_deterministic_python_type_inference",
    "type/python_extract/python_extract_type_inference",
    "type/python_extract/python_inference_type_warnings",
    "type/python_extract/type_inference_unknown_vs_no_type",
    "type/statement_python/inference_warnings",
    "type/statement_python/nondeterministic_inference",
    "type/statement_python/typing",
    "type/statement_python/unknown_vs_untyped",
    "type/statement_python/unknown_vs_untyped_nondeterministic",
    "type/warning/python",
    "type/warning/python_unsupported_type",
    "type/warning/type",
    "variable/dynamic_type",
    "variable/flexible_domain",
    "variable/main",
    "variable/missing_domain_bad",
    "variable/parallel_declaration",
    "variable/same_val_multi_expr",
    "warning/bad",
    "warning/bad_interface",
    "warning/fake_forbid",
    "warning/ignore",
    "warning/statement/control",
    "warning/statement/decl_lists",
    "warning/statement/python",
    "warning/statement/structure",
    "warning/syntax",
    "warning/variables",
    "warning/variable_confusing_name",
    "warning/variable_reservedName",
    "warning/variable_undeclared",
    "warning/variable_undeclared_python_extract",
    "warning/variable_undeclared_statement",
]

other_tests = [
    "core/conditional_empty_set_linked_output",
    "core/empty_set_linked_output_execution",
    "core/optional_absent_conditional_set_output",
    "core/optional_set_empty_execution",
]

compile_skip: set[str] = set()
compile_xfail: set[str] = {
    "datatype/bool/conj_disj_none",
    "datatype/bool/conj_disj_mixed",
    "engine/request",
}
compile2_skip: set[str] = {
    "engine/request_mult",  # mixed engines
    "execution/python_integrity",  # non static input
    "variable/dynamic_type",  # non static input
}
compile2_xfail: set[str] = {
    "datatype/bool/conj_disj_mixed",
    "engine/request",
    "expression/python_extract",
    "optimization/multimap_bool",
    "optimization/multimap_float",
    "optimization/multimap_float_precision",
    "optimization/multimap_int",
    "optimization/multimap_labeled_values",
    "optimization/priority",
    "set/manipulations",
    "set/selfref",
    "multimap/basics",
    "multimap/equality",
    "multimap/executions",
    "multimap/main",
    "expression/lambdas",
    "expression/lambda_recursive",
    "expression/lambda_zero_args",
    "set/fold_bools",
    "set/iterations",
    "set/nested",
    "set/membership_nested",
    "type/checking/multimap",
    "type/checking/numeric",
    "engine/request_set_ref",  # mixed engines?
    "core/reasoning_modes",  # multimap
    "python/extract_set_input",
    "python/extract_static",
}
ground_skip: set[str] = {
    "set/selfref",
    "core/python_set_bool_brave",
    "core/python_extract_statement_error_warning",
    "set/overapprox_boundaries",  ## too slow as it enumerates a lot of sets
}
ground_xfail: set[str] = {
    "datatype/bool/conj_disj_mixed",
    "core/reasoning_modes",
    "core/set_execution_input_alias",
    "engine/request",
    "engine/request_set_ref",
    "expression/lambdas",
    "expression/lambda_recursive",
    "expression/lambda_zero_args",
    "multimap/basics",
    "multimap/equality",
    "multimap/executions",
    "multimap/main",
    "optimization/multimap_bool",
    "optimization/multimap_float",
    "optimization/multimap_float_precision",
    "optimization/multimap_int",
    "optimization/multimap_labeled_values",
    "optimization/priority",
    "set/fold_bools",
    "set/iterations",
}

propagator_skip: set[str] = {
    "core/python_extract_statement_error_warning",
    "set/overapprox_boundaries",  ## too slow as it enumerates a lot of sets
}
propagator_xfail: set[str] = {
    "datatype/bool/conj_disj_mixed",
    "engine/request",
    "engine/request_mixed_trig",
    "expression/lambda_recursive",
    "multimap/main",
    "optimization/preferences",
    "python/set_output",
    "python/extract_set_output",
    "set/fold_bools",
    "set/iterations",
    "set/selfref",
    "type/warning/python_unsupported_type",
    "warning/variables",
}

propagator_true_skip: set[str] = propagator_skip | set()
propagator_true_xfail: set[str] = propagator_xfail | set()

engine_test_configs: list[tuple[str, set[str], set[str], tuple[bool, ...]]] = [
    ("compile", compile_skip, compile_xfail, (False,)),
    ("compile2", compile2_skip, compile2_xfail, (False,)),
    ("ground", ground_skip, ground_xfail, (False,)),
    ("propagator", propagator_skip, propagator_xfail, (False,)),
    ("propagator", propagator_true_skip, propagator_true_xfail, (True,)),
]


def param_marks(
    name: str,
    skip: set[str],
    xfail: set[str],
    engine: str,
):
    """Return pytest marks for a test name under a specific engine context."""
    if name in skip:
        return [pytest.mark.skip(reason=f"skipped in {engine} engine")]
    if name in xfail:
        return [pytest.mark.xfail(reason=f"known failure in {engine} engine")]
    return []


@pytest.mark.parametrize(
    ["name", "engine", "check_mode"],
    [
        pytest.param(
            name,
            engine,
            check_mode,
            marks=param_marks(name, skip, xfail, engine),
        )
        for engine, skip, xfail, check_modes in engine_test_configs
        for check_mode in check_modes
        for name in base_tests
    ],
)
def test_engine(name: str, engine: Literal["compile", "compile2", "ground", "propagator"], check_mode: bool):
    run_test(name, engine, check_mode)


choice_statistics_skip: set[str] = {
    "core/empty_set_execution",
    "core/optional_set_empty_execution",
    "core/python_set_bool_brave",
    "python/dynamic",
    "python/extract_dynamic",
    "python/extract_succeeds",
    "optimization/optional_absent_linked_value",
    "core/boolean_shortcut_optional_presence",
    "core/unprojected_optional_equality",
    "core/set_interface_value_marker",
    "core/shared_optional_output_domains",
    "core/python_extract_statement_error_warning",
    "execution/conditional_string_equality_single_model",
}
choice_statistics_xfail: set[str] = {
    "core/conditional_assign",
    "core/integrity",
    "core/reasoning_modes",
    "type/checking/invalid",
    "type/checking/none_bool",
    "type/python_extract/non_deterministic_python_type_inference",
    "type/statement_python/nondeterministic_inference",
    "type/statement_python/unknown_vs_untyped_nondeterministic",
    "datatype/bool/derived_relations",
    "datatype/bool/equivalence_bad",
    "datatype/bool/evaluate",
    "datatype/bool/implication_bad",
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
    "optimization/multimap_bool",
    "optimization/multimap_float",
    "optimization/multimap_float_precision",
    "optimization/multimap_int",
    "optimization/multimap_labeled_values",
    "optimization/no_multimap_bool",
    "optimization/no_multimap_float",
    "optimization/no_multimap_float_precision",
    "optimization/no_multimap_int",
    "optimization/no_multimap_labeled_values",
    "optimization/preferences",
    "optimization/priority",
    "set/membership_decomposed",
    "set/membership_python",
    "set/diff_flat",
    "set/from_domain",
    "set/eq_neq_flat",
    "set/inter_flat",
    "set/nondet_simple",
    "set/same_val_multi_expr",
    "set/set_in_set_notin",
    "set/set_make_flat",
    "set/length_flat",
    "set/overapprox_boundaries",
    "set/selfref",
    "set/subset_flat",
    "set/union_flat",
    "variable/parallel_declaration",
    "variable/flexible_domain",
    "variable/main",
    "variable/same_val_multi_expr",
    "variable/dynamic_type",
    "warning/bad",
    "warning/fake_forbid",
    "type/warning/python",
    "type/warning/type",
    "warning/variables",
    "warning/variable_reservedName",
    "warning/variable_undeclared",
}


@pytest.mark.parametrize(
    "name",
    [
        pytest.param(
            name,
            marks=param_marks(name, choice_statistics_skip, choice_statistics_xfail, "compile statistics choices"),
        )
        for name in base_tests
    ],
)
def test_compile_statistics_have_zero_choices(name: str):
    statistics = solve_with_clingo_statistics(name)
    assert statistics["solving"]["solvers"]["choices"] == 0.0


tightness_statistics_skip: set[str] = {"core/python_set_bool_brave"}
tightness_statistics_xfail: set[str] = {
    "optimization/multimap_bool",
    "optimization/multimap_float",
    "optimization/multimap_float_precision",
    "optimization/multimap_labeled_values",
    "optimization/multimap_int",
    "optimization/priority",
    "variable/dynamic_type",
}


@pytest.mark.parametrize(
    "name",
    [
        pytest.param(
            name,
            marks=param_marks(
                name, tightness_statistics_skip, tightness_statistics_xfail, "compile statistics tightness"
            ),
        )
        for name in base_tests
    ],
)
def test_compile_statistics_are_tight(name: str):
    statistics = solve_with_clingo_statistics(name)
    assert statistics["problem"]["lp"]["sccs"] == 0.0
