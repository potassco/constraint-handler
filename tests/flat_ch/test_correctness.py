import subprocess
from pathlib import Path

import clingo
import pytest

import tests.utils.testing as chut
from flat_ch.main import add_to_control
from tests.test_encoding import (
    base_tests,
    ctrl_options,
    engine_tests,
    multimap_tests,
    type_tests,
    warning_tests,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session", autouse=True)
def generate_flat_ch_files() -> None:
    subprocess.run(["fch", "--generate"], check=True, cwd=REPO_ROOT)


flat_ch_removed_category_tests = set(type_tests + warning_tests + multimap_tests + engine_tests)

flat_ch_currently_not_working_tests = {
    "datatype/bool/conj_disj_bad",
    "datatype/bool/conj_disj_mixed",
    "datatype/bool/implication_bad",
    "datatype/float/equality_cross_type",
    "datatype/float/ordering_cross_type",
    "datatype/int/equality_cross_type",
    "datatype/int/ordering_cross_type",
    "core/conj_bad_none_recovery",
    "core/conditional_assign",
    "core/reasoning_modes",
    "expression/python_extract/basic",
    "error/recovery",
    "error/recovery_bool",
    "error/recovery_conditionals",
    "error/recovery_ensure",
    "execution/optional_run",
    "execution/python_augassign_types",
    "execution/python_integrity",
    "expression/bad_equality",
    "expression/lambda_recursive",
    "expression/lambda_zero_args",
    "expression/lambdas",
    "optimization/multimap_bool",
    "optimization/multimap_float",
    "optimization/multimap_float_precision",
    "optimization/multimap_int",
    "optimization/multimap_labeled_values",
    "optimization/priority",
    "set/fold_bools",
    "set/iterations",
    "set/manipulations",
    "set/membership_nested",
    "set/missing_declare_repair",
    "set/nested",
    "set/selfref",
    "unit/bad_add",
    "unit/bad_concat",
    "unit/bad_float_div",
    "unit/bad_geq",
    "unit/bad_gt",
    "unit/bad_int_div",
    "unit/bad_leq",
    "unit/bad_leqv",
    "unit/bad_lt",
    "unit/bad_lxor",
    "unit/bad_max",
    "unit/bad_min",
    "unit/bad_mult",
    "unit/bad_sub",
    "unit/boolean_conj",
    "unit/boolean_default",
    "unit/boolean_disj",
    "unit/boolean_disj_none_bug",
    "unit/boolean_ite",
    "unit/boolean_leqv",
    "unit/boolean_leqv_none_bug",
    "unit/boolean_limp",
    "unit/boolean_limp_none_bug",
    "unit/boolean_lxor",
    "unit/boolean_lxor_none_bug",
    "unit/equality_eq",
    "unit/equality_neq",
    "unit/float_add",
    "unit/float_float_div",
    "unit/float_geq",
    "unit/float_gt",
    "unit/float_int_div",
    "unit/float_leq",
    "unit/float_lt",
    "unit/float_max",
    "unit/float_min",
    "unit/float_mult",
    "unit/float_pow",
    "unit/float_sub",
    "unit/int_add",
    "unit/int_geq",
    "unit/int_gt",
    "unit/int_int_div",
    "unit/int_leq",
    "unit/int_lt",
    "unit/int_max",
    "unit/int_min",
    "unit/int_mult",
    "unit/int_pow",
    "unit/int_sub",
    "unit/nullary/python_pythonExtract",
    "unit/python_python",
    "unit/python_pythonExtract",
    "unit/set_eq",
    "unit/set_neq",
    "unit/set_set_isin",
    "unit/set_set_notin",
    "unit/set_subset",
    "unit/set_union",
    "unit/string_concat",
    "unit/string_geq",
    "unit/string_gt",
    "unit/string_leq",
    "unit/string_lt",
    "unit/symbol_geq",
    "unit/symbol_gt",
    "unit/symbol_leq",
    "unit/symbol_lt",
    "unit/tuple_eq",
    "unit/tuple_neq",
    "unit/unary/bad_abs",
    "unit/unary/bad_add",
    "unit/unary/bad_ceil",
    "unit/unary/bad_floor",
    "unit/unary/bad_hasValue",
    "unit/unary/bad_length",
    "unit/unary/bad_leqv",
    "unit/unary/bad_lxor",
    "unit/unary/bad_minus",
    "unit/unary/boolean_hasValue",
    "unit/unary/boolean_leqv",
    "unit/unary/boolean_lxor",
    "unit/unary/float_abs",
    "unit/unary/float_add",
    "unit/unary/float_ceil",
    "unit/unary/float_floor",
    "unit/unary/float_minus",
    "unit/unary/float_mult",
    "unit/unary/int_abs",
    "unit/unary/int_add",
    "unit/unary/int_ceil",
    "unit/unary/int_floor",
    "unit/unary/int_minus",
    "unit/unary/int_mult",
    "unit/unary/string_length",
    "variable/missing_domain_bad",
}.intersection(base_tests)

flat_ch_unsupported_tests = {
    "core/custom_globals",
    "core/python_set_bool_brave",
    "execution/python_integrity_should_be_ignored",
    "execution/python_set_empty_equality",
    "expression/python_extract/bad",
    "expression/python_extract/binding_leak",
    "expression/python_extract/dynamic",
    "expression/python_extract/set_input",
    "expression/python_extract/set_output",
    "expression/python_extract/set_projection",
    "expression/python_extract/static",
    "expression/python_extract/succeeds",
    "expression/tuple",
    "expression/tuple_arity_mismatch",
    "expression/tuple_nested",
    "optimization/preferences",
    "python/dynamic",
    "python/set_output",
}.intersection(base_tests)

flat_ch_supported_tests = [
    name
    for name in base_tests
    if name not in flat_ch_removed_category_tests
    and name not in flat_ch_currently_not_working_tests
    and name not in flat_ch_unsupported_tests
]

flat_ch_supported_core_tests = [name for name in flat_ch_supported_tests if name.startswith("core/")]
flat_ch_supported_non_core_tests = [name for name in flat_ch_supported_tests if not name.startswith("core/")]


def solve_with_flat_ch(name: str, test, extra_args: list[str]):
    ctl = clingo.Control([*ctrl_options, *extra_args])
    add_to_control(ctl, {}, api="ch")
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


@pytest.mark.parametrize(
    "name",
    flat_ch_supported_non_core_tests,
)
def test_flat_ch_correctness(name: str):
    run_test(name)


@pytest.mark.parametrize(
    "name",
    flat_ch_supported_core_tests,
)
def test_flat_ch_core_correctness(name: str):
    run_test(name)
