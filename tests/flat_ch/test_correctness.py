import clingo
import pytest

import flat_ch.api as flat_ch_api
import tests.utils.testing as chut
from tests.test_encoding import base_tests, ctrl_options

flat_ch_unsupported_tests = {
    "core/conditional_assign",  # missing operator: default
    "core/custom_globals",  # missing custom Python globals injection
    "core/python_set_bool_brave",  # brave-mode Python/set reasoning mismatch
    "core/python_extract_set_projection",  # missing Python set projection
    "engine/request_mixed_trig",  # missing mixed trigger/request handling
    "execution/optional_run",  # missing operator: default
    "execution/python_integrity_should_be_ignored",  # requires CH-specific Python environment wiring
    "expression/python_extract_binding_leak",  # missing operator: pythonExtract
    "expression/tuple_arity_mismatch",  # unsupported tuple literal expressions
    "expression/tuple_nested",  # unsupported tuple literal expressions
    "expression/tuple",  # unsupported tuple literal expressions
    "python/dynamic",  # Python dynamic runtime mismatch
    "python/extract_dynamic",  # missing dynamic Python extract
    "python/extract_succeeds",  # Python extract output mismatch
    "python/extract_set_output",  # missing set-valued Python extract output
    "optimization/preferences",  # missing CH preference_* support
}

flat_ch_bad_warning_unsupported_tests = {
    "core/python_extract_statement_error_warning",  # missing statement-level Python warning recovery
    "datatype/bool_equivalence_bad",  # bad/equivalence handling mismatch
    "error/recovery_bool",  # recovery warning output mismatch
    "error/recovery_conditionals",  # missing conditional recovery
    "error/recovery_ensure",  # recovery error handling mismatch
    "error/recovery",  # recovery flow mismatch
    "expression/bad_equality",  # bad-value propagation mismatch
    "python/extract_bad",  # missing bad-result Python extract handling
    "warning/bad",  # bad warning output mismatch
    "warning/bad_interface",  # bad-interface warning/value mismatch
    "warning/fake_forbid",  # missing forbid-style warnings
    "warning/python_unsupported_type",  # missing Python unsupported-type warnings
    "warning/statement_malformed",  # missing malformed-statement warnings
    "warning/syntax",  # syntax diagnostics mismatch
    "warning/type",  # type diagnostics mismatch
    "warning/variables",  # variable warning aggregation mismatch
    "warning/variable_reservedName",  # missing reserved-name warnings
    "warning/variable_undeclared",  # missing undeclared-variable warnings
    "warning/variable_undeclared_python_extract",  # missing undeclared Python-extract warnings
    "warning/variable_undeclared_statement",  # missing undeclared statement-variable warnings
    "set/missing_declare_repair",  # missing implicit set-declare repair
    "variable/missing_domain_bad",  # missing CH empty-domain bad-value repair
}

all_flat_ch_unsupported_tests = flat_ch_unsupported_tests | flat_ch_bad_warning_unsupported_tests

supported_tests = [name for name in base_tests if name not in all_flat_ch_unsupported_tests]
currently_unsupported_tests = [name for name in base_tests if name in all_flat_ch_unsupported_tests]

supported_core_tests = [name for name in supported_tests if name.startswith("core/")]
supported_non_core_tests = [name for name in supported_tests if not name.startswith("core/")]
currently_unsupported_core_tests = [
    name for name in base_tests if name.startswith("core/") and name in all_flat_ch_unsupported_tests
]


def solve_with_flat_ch(name: str, test, extra_args: list[str]):
    ctl = clingo.Control([*ctrl_options, *extra_args])
    flat_ch_api.add_to_control(ctl, {}, api="ch")
    if name.startswith("tests/correctness/optimization/"):
        ctl.add("base", [], "_fch_enable_optimize_value_output.")

    ctl.load(name + ".lp")
    ctl.ground()

    if not test.outcome().is_certain():
        ctl.solve(
            on_core=test.on_core,
            on_finish=test.on_finish,
            on_model=test.on_model,
            on_unsat=test.on_unsat,
            on_statistics=test.on_statistics,
        )


def run_test(name: str):
    file_name = "tests/correctness/" + name
    for test, extra_args in chut.build_expectations(file_name):
        solve_with_flat_ch(file_name, test, extra_args)
        test.assert_()


flat_ch_skip: set[str] = {
    "engine/request_mult",
    "execution/python_integrity",
}
flat_ch_xfail: set[str] = {
    "core/reasoning_modes",
    "core/type_checking",
    "engine/request",
    "engine/request_set_ref",
    "expression/lambdas",
    "expression/lambda_recursive",
    "expression/lambda_zero_args",
    "expression/python_extract",
    "python/extract_static",
    "python/extract_set_input",
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
    "set/membership_nested",
    "set/nested",
    "set/fold_bools",
    "set/iterations",
    "set/manipulations",
    "set/selfref",
    "warning/python",
    "warning/variable_confusing_name",
}


def param_marks(name: str):
    if name in flat_ch_skip:
        return [pytest.mark.skip(reason="skipped in flat_ch CH API mode")]
    if name in flat_ch_xfail:
        return [pytest.mark.xfail(reason="requires CH-specific Python environment wiring")]
    return []


@pytest.mark.parametrize(
    "name",
    [
        pytest.param(
            name,
            marks=param_marks(name),
        )
        for name in supported_non_core_tests
    ],
)
def test_flat_ch_correctness(name: str):
    run_test(name)


@pytest.mark.parametrize(
    "name",
    [
        pytest.param(
            name,
            marks=param_marks(name),
        )
        for name in supported_core_tests
    ],
)
def test_flat_ch_core_correctness(name: str):
    run_test(name)
