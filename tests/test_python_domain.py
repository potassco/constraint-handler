from __future__ import annotations

import math
from dataclasses import replace
from itertools import product

import clingo
import pytest

import constraint_handler.evaluator as evaluator
import constraint_handler.solver_environment as solver_environment
from constraint_handler.schemas import expression, operators
from constraint_handler.utils.python_domain import Domain, PythonEvaluationSession
from constraint_handler.utils.python_domain_computation import DomainComputation


@pytest.fixture(autouse=True)
def reset_domain_global_state() -> None:
    Domain.GLOBAL_SET_UIDS.clear()
    Domain.NEXT_SET_UID = 0
    Domain.sets.fget.cache_clear()
    Domain.set_uids.fget.cache_clear()


def build_domain(*values, is_bad: bool = False) -> Domain:
    parts: list[Domain] = []
    for value in values:
        parts.append(Domain.from_runtime(value))
    return Domain.merge(*parts, Domain.bad() if is_bad else Domain.empty())


class IgnorePythonEvaluation(PythonEvaluationSession):
    pass


def compute_domain(
    operation: clingo.Symbol,
    *domains: Domain,
    solver_identifiers: tuple[clingo.Symbol, ...] = (),
) -> Domain:
    return Domain.compute_domain(
        operation,
        *domains,
        solver_identifiers=solver_identifiers,
        evaluation_session=IgnorePythonEvaluation(),
    )


def semantic_runtime_options(domain: Domain) -> tuple[object, ...]:
    options = [Domain.value_to_runtime(value) for value in domain.values()]
    if domain.is_bad:
        options.append(expression.Bad.bad)
    return tuple(options)


def expected_domain_from_evaluator(operation: object, *domains: Domain) -> Domain:
    arg_options = [semantic_runtime_options(domain) for domain in domains]
    if any(not options for options in arg_options):
        return Domain.empty()

    result = Domain.empty()
    is_bad = False
    for args in product(*arg_options):
        try:
            applied = evaluator.operator(operation, args, (), {})
        except Exception:
            is_bad = True
            continue
        if applied.value is expression.Bad.bad:
            is_bad = True
            continue
        result = Domain.merge(result, Domain.from_runtime(applied.value))
    return Domain.merge(result, Domain.bad() if is_bad else Domain.empty())


def assert_same_semantics(operation: object, *domains: Domain) -> None:
    assert Domain.apply(operation, *domains) == expected_domain_from_evaluator(operation, *domains)


def symbol_sequence(*items: clingo.Symbol) -> clingo.Symbol:
    result = clingo.Tuple_([])
    for item in reversed(items):
        result = clingo.Tuple_([item, result])
    return result


def test_value_helpers_preserve_set_style_numeric_deduplication() -> None:
    domain = Domain(
        is_bad=True,
        bools=frozenset({True}),
        ints=frozenset({1, 2}),
        floats=frozenset({1.0, 2.5}),
        is_none=True,
        strings=frozenset({"x"}),
        symbols=frozenset({clingo.Function("sym")}),
        tuples=frozenset({("tuple",)}),
    )
    domain = Domain.merge(domain, Domain.set_values(frozenset({"member"})))

    assert domain.value_count() == 10
    assert set(domain.numeric_values()) == {1, 2, 2.5}
    assert set(domain.scalar_values()) == {True, 2, 2.5, None, "x", clingo.Function("sym")}
    assert set(domain.values()) == {
        True,
        2,
        2.5,
        None,
        "x",
        clingo.Function("sym"),
        ("tuple",),
        frozenset({"member"}),
    }
    assert set(domain.values(include_bad=True)) == {
        True,
        2,
        2.5,
        None,
        "x",
        clingo.Function("sym"),
        ("tuple",),
        frozenset({"member"}),
        Domain.BAD_SYMBOL,
    }


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (True, Domain.booleans(True)),
        (7, Domain.integers(7)),
        (2.5, Domain.floats_only(2.5)),
        (None, Domain.none()),
        ("txt", Domain.strings_only("txt")),
        (clingo.Function("sym"), Domain.symbols_only(clingo.Function("sym"))),
        ((1, "x"), Domain.tuple_values((1, "x"))),
        (frozenset({1, "x"}), Domain.set_values(frozenset({1, "x"}))),
    ],
)
def test_from_value_covers_supported_runtime_types(value: object, expected: Domain) -> None:
    assert Domain.from_value(value) == expected


def test_from_symbol_decodes_compile2_values_and_preserves_plain_symbols() -> None:
    plain_symbol = clingo.Function("plain", [clingo.Number(1)])

    assert Domain.from_symbol(
        clingo.Function("val", [clingo.Function("bool"), clingo.Function("true")])
    ) == Domain.booleans(True)
    assert Domain.from_symbol(clingo.Function("val", [clingo.Function("int"), clingo.Number(7)])) == Domain.integers(7)
    assert Domain.from_symbol(
        clingo.Function("val", [clingo.Function("float"), clingo.Function("float", [clingo.String("2.5")])])
    ) == Domain.floats_only(2.5)
    assert (
        Domain.from_symbol(clingo.Function("val", [clingo.Function("none"), clingo.Function("none")])) == Domain.none()
    )
    assert Domain.from_symbol(
        clingo.Function("val", [clingo.Function("string"), clingo.String("txt")])
    ) == Domain.strings_only("txt")
    assert Domain.from_symbol(clingo.Function("val", [clingo.Function("symbol"), plain_symbol])) == Domain.symbols_only(
        plain_symbol
    )
    assert Domain.from_symbol(plain_symbol) == Domain.symbols_only(plain_symbol)
    assert Domain.from_symbol(clingo.Function("val", [clingo.Function("tuple"), plain_symbol])) == Domain.bad()


def test_runtime_and_symbol_roundtrips_cover_nested_structures_and_bad_marker() -> None:
    nested_value = (1, frozenset({False, "x"}), None)
    runtime_value = Domain.value_to_runtime(nested_value)

    assert runtime_value == (1, frozenset({False, "x"}), None)
    assert Domain.runtime_to_value(runtime_value) == nested_value
    assert Domain.runtime_to_value(Domain.value_to_runtime(Domain.BAD_SYMBOL)) == Domain.BAD_SYMBOL

    encoded_set = Domain.value_to_symbol(frozenset({1, "x"}))
    assert encoded_set.name == "set"
    assert Domain.value_to_symbol((1, "x")) == clingo.Tuple_(
        [
            Domain.value_to_symbol(1),
            Domain.value_to_symbol("x"),
        ]
    )


def test_options_without_none_and_has_values_cover_empty_optional_and_bad_cases() -> None:
    domain = Domain.merge(Domain.booleans(True), Domain.none(), Domain.bad())

    assert domain.has_values() is True
    assert replace(domain, is_none=False) == Domain(is_bad=True, bools=frozenset({True}))
    assert domain.options() == tuple(sorted((Domain.BAD_SYMBOL, None, True), key=str))
    assert Domain.bad().has_values() is False
    assert Domain.empty().options() == ()


def test_set_domains_can_represent_all_subsets_without_materializing_them_up_front() -> None:
    domain = Domain.all_subsets(1, 2)

    assert domain.domain_atoms == {1, 2}
    assert domain.possible_subsets is None
    assert domain.sets == {
        frozenset(),
        frozenset({1}),
        frozenset({2}),
        frozenset({1, 2}),
    }


def test_set_uids_are_cached_and_allocated_globally_from_possible_subsets() -> None:
    left = Domain.all_subsets(1)
    right = Domain.set_values(frozenset(), frozenset({1}))

    assert left.set_uids == {0, 1}
    assert left.set_uids == {0, 1}
    assert right.set_uids == {0, 1}
    assert Domain.GLOBAL_SET_UIDS == {
        frozenset(): 0,
        frozenset({1}): 1,
    }


def test_domain_symbol_export_helpers_include_bad_and_candidate_members() -> None:
    expr_symbol = clingo.Function("expr")
    domain = Domain.merge(Domain(is_bad=True, ints=frozenset({1})), Domain.set_values(frozenset({1, 2})))
    uid = next(iter(domain.set_uids))
    global_set_uids = Domain.GLOBAL_SET_UIDS

    assert list(domain.expression_domain_symbols(expr_symbol, include_set_values=False)) == [
        clingo.Tuple_([expr_symbol, Domain.value_to_symbol(1)]),
        clingo.Tuple_([expr_symbol, clingo.Function("bad")]),
    ]
    assert list(domain.expression_set_domain_symbols(expr_symbol, global_set_uids)) == [
        clingo.Tuple_([expr_symbol, clingo.Number(uid)])
    ]
    assert sorted(domain.set_domain_value_symbols(global_set_uids, candidate_values=(3,)), key=str) == sorted(
        [
            clingo.Tuple_([clingo.Number(uid), clingo.Function("pos"), Domain.value_to_symbol(1)]),
            clingo.Tuple_([clingo.Number(uid), clingo.Function("pos"), Domain.value_to_symbol(2)]),
            clingo.Tuple_([clingo.Number(uid), clingo.Function("neg"), Domain.value_to_symbol(3)]),
        ],
        key=str,
    )


def test_set_value_domain_symbols_export_one_concrete_set() -> None:
    set_value = frozenset({1, 2})
    uid = Domain.register_set_uid(set_value)

    assert sorted(
        Domain.set_value_domain_symbols(
            set_value,
            global_set_uids=Domain.GLOBAL_SET_UIDS,
            candidate_values=(2, 3),
        ),
        key=str,
    ) == sorted(
        [
            clingo.Tuple_([clingo.Number(uid), clingo.Function("pos"), Domain.value_to_symbol(1)]),
            clingo.Tuple_([clingo.Number(uid), clingo.Function("pos"), Domain.value_to_symbol(2)]),
            clingo.Tuple_([clingo.Number(uid), clingo.Function("neg"), Domain.value_to_symbol(3)]),
        ],
        key=str,
    )


@pytest.mark.parametrize(
    ("operation", "expected"),
    [
        ("add", Domain.integers(0)),
        ("mult", Domain.integers(1)),
        ("conj", Domain.booleans(True)),
        ("disj", Domain.booleans(False)),
        ("leqv", Domain.booleans(True)),
        ("lxor", Domain.booleans(False)),
        ("union", Domain.empty()),
        ("inter", Domain.empty()),
        ("diff", Domain.empty()),
        ("max", Domain.empty()),
        ("min", Domain.empty()),
        ("set_make", Domain.set_values(frozenset())),
    ],
)
def test_compute_domain_variadic_empty_cases(operation: str, expected: Domain) -> None:
    assert compute_domain(clingo.Function(operation)) == expected


def test_compute_domain_variadic_fold_cases() -> None:
    assert compute_domain(
        clingo.Function("add"),
        Domain.integers(1),
        Domain.integers(2),
        Domain.integers(3),
    ) == Domain.integers(6)
    assert compute_domain(
        clingo.Function("leqv"),
        Domain.booleans(True),
        Domain.booleans(False),
    ) == Domain.booleans(False)
    assert compute_domain(
        clingo.Function("union"),
        Domain.set_values(frozenset({1}), frozenset({2})),
        Domain.set_values(frozenset({3})),
    ) == Domain.set_values(frozenset({1, 3}), frozenset({2, 3}))


@pytest.mark.parametrize(
    ("operation", "domains"),
    [
        (operators.ArithmeticOperator.abs, (build_domain(-3, 1.5),)),
        (operators.ArithmeticOperator.sqrt, (build_domain(0, 4.0),)),
        (operators.ArithmeticOperator.cos, (build_domain(0.0, math.pi),)),
        (operators.ArithmeticOperator.sin, (build_domain(0.0, math.pi / 2),)),
        (operators.ArithmeticOperator.tan, (build_domain(0.0, 1.0),)),
        (operators.ArithmeticOperator.acos, (build_domain(-1.0, 1.0),)),
        (operators.ArithmeticOperator.asin, (build_domain(-1.0, 1.0),)),
        (operators.ArithmeticOperator.atan, (build_domain(-1.0, 1.0),)),
        (operators.ArithmeticOperator.minus, (build_domain(-3, 1.5),)),
        (operators.ArithmeticOperator.floor, (build_domain(1.2, 3.0),)),
        (operators.ArithmeticOperator.ceil, (build_domain(1.2, 3.0),)),
        (operators.ArithmeticOperator.add, (build_domain(1, 2.5), build_domain(3, 4.5))),
        (operators.ArithmeticOperator.sub, (build_domain(5, 5.5), build_domain(2, 0.5))),
        (operators.ArithmeticOperator.mult, (build_domain(2, 2.5), build_domain(3, 4.0))),
        (operators.ArithmeticOperator.int_div, (build_domain(7, 8.0), build_domain(2, 3))),
        (operators.ArithmeticOperator.float_div, (build_domain(6, 7.5), build_domain(2, 3.0))),
        (operators.ArithmeticOperator.pow, (build_domain(2, 4.0), build_domain(0, 2))),
    ],
)
def test_apply_matches_evaluator_for_numeric_operators(operation: object, domains: tuple[Domain, ...]) -> None:
    assert_same_semantics(operation, *domains)


@pytest.mark.parametrize(
    ("operation", "domains"),
    [
        (operators.ArithmeticOperator.leq, (build_domain(1, 2), build_domain(2, 3))),
        (operators.ArithmeticOperator.lt, (build_domain(1, 2), build_domain(2, 3))),
        (operators.ArithmeticOperator.geq, (build_domain(2, 3), build_domain(1, 2))),
        (operators.ArithmeticOperator.gt, (build_domain(2, 3), build_domain(1, 2))),
        (expression.EqOperator.eq, (build_domain(1, 2), build_domain(2, 3))),
        (expression.EqOperator.eq, (build_domain(None), build_domain(None, 1))),
        (expression.EqOperator.neq, (build_domain("x", "y"), build_domain("y", "z"))),
        (operators.LogicOperator.conj, (build_domain(True, False, None), build_domain(True, None))),
        (operators.LogicOperator.disj, (build_domain(True, False, None), build_domain(False, None))),
        (operators.LogicOperator.ite, (build_domain(True, False, None), build_domain(1, 2), build_domain(3, 4))),
        (
            operators.LogicOperator.leqv,
            (build_domain(True, False, None), build_domain(True, False, expression.Bad.bad)),
        ),
        (operators.LogicOperator.limp, (build_domain(True, False, None), build_domain(True, False, None))),
        (operators.LogicOperator.lnot, (build_domain(True, False, None),)),
        (
            operators.LogicOperator.lxor,
            (build_domain(True, False, None), build_domain(True, False, expression.Bad.bad)),
        ),
        (operators.LogicOperator.snot, (build_domain(True, False, None),)),
        (operators.LogicOperator.wnot, (build_domain(True, False, None),)),
    ],
)
def test_apply_matches_evaluator_for_comparison_and_logic_operators(
    operation: object,
    domains: tuple[Domain, ...],
) -> None:
    assert_same_semantics(operation, *domains)


@pytest.mark.parametrize(
    ("operation", "domains"),
    [
        (expression.StringOperator.concat, (build_domain("a", "b"), build_domain("", "z"))),
        (expression.StringOperator.length, (build_domain("abc", (), frozenset({1, 2})),)),
        (expression.ConditionalOperator.default, (build_domain(None, 1), build_domain(2, 3))),
        (expression.ConditionalOperator.hasValue, (build_domain(None, 1, frozenset({2})),)),
    ],
)
def test_apply_matches_evaluator_for_string_and_conditional_operators(
    operation: object,
    domains: tuple[Domain, ...],
) -> None:
    assert_same_semantics(operation, *domains)


@pytest.mark.parametrize(
    ("operation", "domains"),
    [
        (operators.SetOperator.set_make, (build_domain(1, 2), build_domain("x"))),
        (operators.SetOperator.set_isin, (build_domain(1, 2), build_domain(frozenset({1}), frozenset({2, 3})))),
        (operators.SetOperator.set_notin, (build_domain(1, 2), build_domain(frozenset({1}), frozenset({2, 3})))),
        (operators.SetOperator.union, (build_domain(frozenset({1}), frozenset({2})), build_domain(frozenset({2, 3})))),
        (
            operators.SetOperator.inter,
            (build_domain(frozenset({1, 2}), frozenset({2, 3})), build_domain(frozenset({2}), frozenset({3}))),
        ),
        (
            operators.SetOperator.diff,
            (build_domain(frozenset({1, 2}), frozenset({2, 3})), build_domain(frozenset({2}))),
        ),
        (
            operators.SetOperator.subset,
            (build_domain(frozenset(), frozenset({1})), build_domain(frozenset({1}), frozenset({1, 2}))),
        ),
    ],
)
def test_apply_matches_evaluator_for_set_operators(operation: object, domains: tuple[Domain, ...]) -> None:
    assert_same_semantics(operation, *domains)


def test_apply_tracks_numeric_corner_cases_and_type_mismatches() -> None:
    assert Domain.apply(operators.ArithmeticOperator.sqrt, build_domain(-1)).is_bad is True
    assert compute_domain(clingo.Function("add"), build_domain("x"), build_domain(1)) == Domain.bad()
    assert compute_domain(clingo.Function("float_div"), build_domain(1.0), build_domain(0.0)) == Domain.bad()
    assert compute_domain(clingo.Function("pow"), Domain.bad(), build_domain(0)) == Domain.integers(1)
    assert compute_domain(clingo.Function("pow"), build_domain(None), build_domain(0)) == Domain.integers(1)


def test_apply_length_marks_invalid_scalar_inputs_bad_but_keeps_valid_lengths() -> None:
    domain = build_domain("abcd", frozenset({1, 2}), (1, 2, 3), 9, None)

    assert Domain.apply(expression.StringOperator.length, domain) == Domain(is_bad=True, ints=frozenset({2, 3, 4}))


def test_apply_set_operations_use_complete_sets_and_nonset_values_mark_bad() -> None:
    assert Domain.apply(
        operators.SetOperator.set_isin,
        build_domain(1),
        build_domain(frozenset({1, 2})),
    ) == Domain.booleans(True)
    assert Domain.apply(
        operators.SetOperator.union,
        build_domain(frozenset({1}), 9),
        build_domain(frozenset({2})),
    ) == Domain.merge(Domain.set_values(frozenset({1, 2})), Domain.bad())


def test_apply_if_default_and_hasvalue_cover_none_bad_and_false_cases() -> None:
    assert Domain.apply(expression.ConditionalOperator.IF, build_domain(True, False, None), build_domain(7)) == Domain(
        ints=frozenset({7}),
        is_none=True,
    )
    assert Domain.apply(
        expression.ConditionalOperator.default, build_domain(None, 1), build_domain(2, 3)
    ) == build_domain(1, 2, 3)
    assert Domain.apply(expression.ConditionalOperator.hasValue, build_domain(None, 1, frozenset())) == Domain.booleans(
        True, False
    )
    assert Domain.apply(expression.ConditionalOperator.hasValue, Domain.bad()) == Domain(is_bad=True)


def test_apply_max_and_min_follow_evaluator_cross_product_semantics() -> None:
    left = build_domain(1, 5)
    right = build_domain(2, 3)

    assert Domain.apply(expression.OtherOperator.max, left, right) == expected_domain_from_evaluator(
        expression.OtherOperator.max, left, right
    )
    assert Domain.apply(expression.OtherOperator.min, left, right) == expected_domain_from_evaluator(
        expression.OtherOperator.min, left, right
    )


def test_apply_max_and_min_reject_non_numeric_domains() -> None:
    assert Domain.apply(expression.OtherOperator.max, build_domain("x"), build_domain(2)) == Domain.bad()
    assert Domain.apply(expression.OtherOperator.min, build_domain(True), build_domain(2)) == Domain.bad()


def test_apply_ordered_comparisons_use_extrema_shortcuts_without_changing_results() -> None:
    assert Domain.apply(operators.ArithmeticOperator.leq, build_domain(1, 2), build_domain(5, 6)) == Domain.booleans(
        True
    )
    assert Domain.apply(operators.ArithmeticOperator.gt, build_domain(1, 2), build_domain(5, 6)) == Domain.booleans(
        False
    )
    assert Domain.apply(operators.ArithmeticOperator.lt, build_domain(1, 10), build_domain(5, 6)) == Domain.booleans(
        True, False
    )


def test_apply_length_coarsens_large_symbolic_set_domains_by_cardinality_range() -> None:
    domain = Domain.all_subsets(*range(8))

    assert Domain.apply(expression.StringOperator.length, domain) == Domain(ints=frozenset(range(9)))


def test_apply_set_operations_use_threshold_fallbacks_for_large_symbolic_domains() -> None:
    left = Domain.all_subsets(*range(8))
    right = Domain.all_subsets(*range(4, 12))

    assert Domain.apply(operators.SetOperator.union, left, right) == Domain.all_subsets(*range(12))
    assert Domain.apply(operators.SetOperator.inter, left, right) == Domain.all_subsets(4, 5, 6, 7)
    assert Domain.apply(operators.SetOperator.diff, left, right) == Domain.all_subsets(*range(8))
    assert Domain.apply(operators.SetOperator.subset, left, right) == Domain.booleans(True, False)


def test_compute_domain_uses_shared_threshold_for_large_boolean_cross_products() -> None:
    operation = clingo.Function("leq")
    left = Domain.all_subsets(1, 2, 3)
    right = Domain.all_subsets(2, 3, 4)

    assert compute_domain(operation, left, right) == Domain(is_bad=True, bools=frozenset({True, False}))


def test_compute_domain_symbolic_dispatch_matches_apply_for_small_cases() -> None:
    assert compute_domain(clingo.Function("sub"), build_domain(7), build_domain(2)) == Domain.integers(5)
    assert compute_domain(clingo.Function("conj"), build_domain(True, None), build_domain(False)) == Domain.booleans(
        False
    )
    assert compute_domain(clingo.Function("concat"), build_domain("a"), build_domain("b", "c")) == Domain.strings_only(
        "ab", "ac"
    )
    assert compute_domain(clingo.Function("set_make"), build_domain(1, 2), build_domain("x")) == Domain.set_values(
        frozenset({1, "x"}),
        frozenset({2, "x"}),
    )


def test_compute_domain_if_requires_exactly_two_arguments() -> None:
    assert compute_domain(clingo.Function("if"), Domain.booleans(True)) == Domain.bad()


def test_compute_domain_returns_empty_when_any_child_domain_is_empty() -> None:
    assert compute_domain(clingo.Function("add"), Domain.empty(), build_domain(1)) == Domain.empty()


def test_compute_domain_rejects_non_function_operators() -> None:
    assert compute_domain(clingo.Number(7), build_domain(1)) == Domain.bad()


def test_compute_domain_python_callable_matches_evaluator_success_cases() -> None:
    operation = clingo.Function("python", [clingo.String("lambda x, y: x + y")])

    assert compute_domain(operation, build_domain(1, 2), build_domain(10)) == build_domain(11, 12)


def test_compute_domain_python_callable_exception_marks_bad_like_evaluator() -> None:
    operation = clingo.Function("python", [clingo.String("lambda x: 10 / x")])

    assert compute_domain(operation, build_domain(2, 0)) == Domain(floats=frozenset({5.0}), is_bad=True)


def test_compute_domain_python_callable_bad_code_is_bad() -> None:
    operation = clingo.Function("python", [clingo.String("not valid python")])

    assert compute_domain(operation, build_domain(1)) == Domain.bad()


def test_compute_domain_python_extract_matches_success_and_failure_semantics() -> None:
    operation = clingo.Function(
        "pythonExtract",
        [
            clingo.String("total = left + right"),
            clingo.String("total"),
        ],
    )
    succeeds_operation = clingo.Function(
        "pythonExtract",
        [
            clingo.String("raise solver_environment.FailIntegrityExn()"),
            clingo.String("__succeeds"),
        ],
    )
    solver_id = (clingo.Number(99),)
    evaluator._solver_environment[99] = {"solver_environment": solver_environment}

    try:
        assert compute_domain(
            operation, build_domain(("left", 1)), build_domain(("right", 2)), solver_identifiers=solver_id
        ) == Domain.integers(3)
        assert compute_domain(succeeds_operation, build_domain()) == Domain.empty()
        assert compute_domain(
            succeeds_operation, build_domain(("left", 1)), solver_identifiers=solver_id
        ) == Domain.booleans(False)
    finally:
        evaluator._solver_environment.pop(99, None)


def test_compute_domain_python_extract_marks_bad_on_invalid_bindings_and_eval_errors() -> None:
    binding_operation = clingo.Function(
        "pythonExtract",
        [
            clingo.String("x = 1"),
            clingo.String("x"),
        ],
    )
    eval_operation = clingo.Function(
        "pythonExtract",
        [
            clingo.String("x = 1"),
            clingo.String("missing_name"),
        ],
    )

    assert compute_domain(binding_operation, build_domain(1)) == Domain.bad()
    assert compute_domain(eval_operation, build_domain(("left", 1))) == Domain.bad()


def test_domain_computation_preserves_bad_tuple_inputs_for_python_extract() -> None:
    variable_name = clingo.String("missing_input")
    variable_expr = clingo.Function("variable", [variable_name])
    binding_expr = clingo.Tuple_(
        [
            clingo.Function("val", [clingo.Function("string"), clingo.String("lhs")]),
            variable_expr,
        ]
    )
    operation_expr = clingo.Function(
        "operation",
        [
            clingo.Function(
                "pythonExtract",
                [
                    clingo.String("pass"),
                    clingo.String("lhs"),
                ],
            ),
            symbol_sequence(binding_expr),
        ],
    )

    computed = DomainComputation.compute(
        (
            operation_expr,
            variable_expr,
            clingo.Function("variable_define", [variable_name, clingo.Function("bad")]),
        ),
        (),
    )

    assert computed.expression_domains[binding_expr] == Domain.tuple_values(("lhs", Domain.BAD_SYMBOL))
    assert computed.expression_domains[operation_expr] == Domain.bad()


def test_domain_computation_combines_all_required_set_source_options() -> None:
    left_name = clingo.String("left")
    right_name = clingo.String("right")
    target_name = clingo.String("target")
    left_var = clingo.Function("variable", [left_name])
    right_var = clingo.Function("variable", [right_name])
    target_var = clingo.Function("variable", [target_name])

    computed = DomainComputation.compute(
        (
            target_var,
            left_var,
            right_var,
            clingo.Function(
                "set_baseDomain", [left_name, clingo.Function("val", [clingo.Function("int"), clingo.Number(1)])]
            ),
            clingo.Function(
                "set_baseDomain", [left_name, clingo.Function("val", [clingo.Function("int"), clingo.Number(2)])]
            ),
            clingo.Function(
                "set_assign", [left_name, clingo.Function("val", [clingo.Function("int"), clingo.Number(1)])]
            ),
            clingo.Function(
                "set_baseDomain", [right_name, clingo.Function("val", [clingo.Function("int"), clingo.Number(3)])]
            ),
            clingo.Function(
                "set_baseDomain", [right_name, clingo.Function("val", [clingo.Function("int"), clingo.Number(4)])]
            ),
            clingo.Function(
                "set_assign", [right_name, clingo.Function("val", [clingo.Function("int"), clingo.Number(3)])]
            ),
            clingo.Function("set_assign", [target_name, left_var]),
            clingo.Function("set_assign", [target_name, right_var]),
        ),
        (),
    )

    assert computed.expression_domains[target_var] == Domain.set_values(
        frozenset({1, 3}),
        frozenset({1, 3, 4}),
        frozenset({1, 2, 3}),
        frozenset({1, 2, 3, 4}),
    )


def test_domain_computation_exports_python_callable_trace_symbols() -> None:
    variable_name = clingo.String("x")
    variable_expr = clingo.Function("variable", [variable_name])
    operation_expr = clingo.Function(
        "operation",
        [
            clingo.Function("python", [clingo.String("lambda x: 10 / x")]),
            symbol_sequence(variable_expr),
        ],
    )

    computed = DomainComputation.compute(
        (
            operation_expr,
            variable_expr,
            clingo.Function(
                "variable_define", [variable_name, clingo.Function("val", [clingo.Function("int"), clingo.Number(2)])]
            ),
            clingo.Function(
                "variable_domain", [variable_name, clingo.Function("val", [clingo.Function("int"), clingo.Number(0)])]
            ),
        ),
        (),
    )

    assert set(computed.python_evaluation_symbols()) == {
        clingo.Tuple_([operation_expr, clingo.Number(0)]),
        clingo.Tuple_([operation_expr, clingo.Number(1)]),
    }
    assert set(computed.python_evaluation_input_symbols()) == {
        clingo.Tuple_(
            [
                operation_expr,
                clingo.Number(0),
                variable_expr,
                clingo.Function("val", [clingo.Function("int"), clingo.Number(0)]),
            ]
        ),
        clingo.Tuple_(
            [
                operation_expr,
                clingo.Number(1),
                variable_expr,
                clingo.Function("val", [clingo.Function("int"), clingo.Number(2)]),
            ]
        ),
    }
    assert set(computed.python_evaluation_output_symbols()) == {
        clingo.Tuple_(
            [
                operation_expr,
                clingo.Number(0),
                clingo.Function("bad"),
            ]
        ),
        clingo.Tuple_(
            [
                operation_expr,
                clingo.Number(0),
                clingo.Function(
                    "error",
                    [
                        clingo.Function("expression", [clingo.Function("pythonError")]),
                        clingo.String("ZeroDivisionError('division by zero')"),
                    ],
                ),
            ]
        ),
        clingo.Tuple_(
            [
                operation_expr,
                clingo.Number(1),
                clingo.Function("val", [clingo.Function("float"), clingo.Function("float", [clingo.String("5.0")])]),
            ]
        ),
    }


def test_domain_computation_exports_set_memberships_only_for_python_and_tuple_consumers() -> None:
    python_input_name = clingo.String("python_input")
    python_input_var = clingo.Function("variable", [python_input_name])
    python_output_name = clingo.String("python_output")
    python_output_var = clingo.Function("variable", [python_output_name])
    tuple_child_name = clingo.String("tuple_child")
    tuple_child_var = clingo.Function("variable", [tuple_child_name])
    unused_name = clingo.String("unused")
    unused_var = clingo.Function("variable", [unused_name])

    python_input_expr = clingo.Function(
        "operation",
        [
            clingo.Function("python", [clingo.String("lambda pool: 4 in pool")]),
            symbol_sequence(python_input_var),
        ],
    )
    python_output_expr = clingo.Function(
        "operation",
        [
            clingo.Function("python", [clingo.String("lambda: {1, 3}")]),
            symbol_sequence(),
        ],
    )
    tuple_expr = clingo.Tuple_([tuple_child_var])

    computed = DomainComputation.compute(
        (
            python_input_expr,
            python_input_var,
            python_output_expr,
            python_output_var,
            tuple_expr,
            tuple_child_var,
            unused_var,
            clingo.Function(
                "set_baseDomain",
                [python_input_name, clingo.Function("val", [clingo.Function("int"), clingo.Number(1)])],
            ),
            clingo.Function(
                "set_baseDomain",
                [python_input_name, clingo.Function("val", [clingo.Function("int"), clingo.Number(2)])],
            ),
            clingo.Function(
                "set_baseDomain",
                [python_input_name, clingo.Function("val", [clingo.Function("int"), clingo.Number(4)])],
            ),
            clingo.Function(
                "set_assign", [python_input_name, clingo.Function("val", [clingo.Function("int"), clingo.Number(1)])]
            ),
            clingo.Function(
                "set_assign", [python_input_name, clingo.Function("val", [clingo.Function("int"), clingo.Number(2)])]
            ),
            clingo.Function("set_assign", [python_output_name, python_output_expr]),
            clingo.Function(
                "set_baseDomain", [tuple_child_name, clingo.Function("val", [clingo.Function("int"), clingo.Number(5)])]
            ),
            clingo.Function(
                "set_baseDomain", [tuple_child_name, clingo.Function("val", [clingo.Function("int"), clingo.Number(6)])]
            ),
            clingo.Function(
                "set_assign", [tuple_child_name, clingo.Function("val", [clingo.Function("int"), clingo.Number(5)])]
            ),
            clingo.Function(
                "set_baseDomain", [unused_name, clingo.Function("val", [clingo.Function("int"), clingo.Number(7)])]
            ),
            clingo.Function(
                "set_assign", [unused_name, clingo.Function("val", [clingo.Function("int"), clingo.Number(7)])]
            ),
        ),
        (),
    )

    membership_symbols = set(computed.expression_set_domain_value_symbols())
    python_input_uid = computed.global_set_uids[frozenset({1, 2})]
    python_output_uid = computed.global_set_uids[frozenset({1, 3})]
    tuple_child_uid = computed.global_set_uids[frozenset({5})]
    unused_uid = computed.global_set_uids[frozenset({7})]

    assert (
        clingo.Tuple_([clingo.Number(python_input_uid), clingo.Function("pos"), Domain.value_to_symbol(1)])
        in membership_symbols
    )
    assert (
        clingo.Tuple_([clingo.Number(python_input_uid), clingo.Function("pos"), Domain.value_to_symbol(2)])
        in membership_symbols
    )
    assert (
        clingo.Tuple_([clingo.Number(python_input_uid), clingo.Function("neg"), Domain.value_to_symbol(4)])
        in membership_symbols
    )

    assert (
        clingo.Tuple_([clingo.Number(python_output_uid), clingo.Function("pos"), Domain.value_to_symbol(1)])
        in membership_symbols
    )
    assert (
        clingo.Tuple_([clingo.Number(python_output_uid), clingo.Function("pos"), Domain.value_to_symbol(3)])
        in membership_symbols
    )

    assert (
        clingo.Tuple_([clingo.Number(tuple_child_uid), clingo.Function("pos"), Domain.value_to_symbol(5)])
        in membership_symbols
    )
    assert (
        clingo.Tuple_([clingo.Number(tuple_child_uid), clingo.Function("neg"), Domain.value_to_symbol(6)])
        in membership_symbols
    )

    assert (
        clingo.Tuple_([clingo.Number(unused_uid), clingo.Function("pos"), Domain.value_to_symbol(7)])
        not in membership_symbols
    )


def test_domain_computation_exports_python_extract_inputs_against_value_expressions() -> None:
    left_name = clingo.String("left")
    right_name = clingo.String("right")
    left_var = clingo.Function("variable", [left_name])
    right_var = clingo.Function("variable", [right_name])
    left_binding = clingo.Tuple_(
        [
            clingo.Function("val", [clingo.Function("string"), left_name]),
            left_var,
        ]
    )
    right_binding = clingo.Tuple_(
        [
            clingo.Function("val", [clingo.Function("string"), right_name]),
            right_var,
        ]
    )
    operation_expr = clingo.Function(
        "operation",
        [
            clingo.Function(
                "pythonExtract",
                [
                    clingo.String("total = left + right"),
                    clingo.String("total"),
                ],
            ),
            symbol_sequence(left_binding, right_binding),
        ],
    )

    computed = DomainComputation.compute(
        (
            operation_expr,
            left_var,
            right_var,
            clingo.Function(
                "variable_define", [left_name, clingo.Function("val", [clingo.Function("int"), clingo.Number(1)])]
            ),
            clingo.Function(
                "variable_domain", [left_name, clingo.Function("val", [clingo.Function("int"), clingo.Number(2)])]
            ),
            clingo.Function(
                "variable_define", [right_name, clingo.Function("val", [clingo.Function("int"), clingo.Number(2)])]
            ),
        ),
        (),
    )

    assert set(computed.python_evaluation_symbols()) == {
        clingo.Tuple_([operation_expr, clingo.Number(0)]),
        clingo.Tuple_([operation_expr, clingo.Number(1)]),
    }
    assert set(computed.python_evaluation_input_symbols()) == {
        clingo.Tuple_(
            [
                operation_expr,
                clingo.Number(0),
                left_var,
                clingo.Function("val", [clingo.Function("int"), clingo.Number(1)]),
            ]
        ),
        clingo.Tuple_(
            [
                operation_expr,
                clingo.Number(1),
                left_var,
                clingo.Function("val", [clingo.Function("int"), clingo.Number(2)]),
            ]
        ),
    }
    assert set(computed.python_evaluation_output_symbols()) == {
        clingo.Tuple_(
            [
                operation_expr,
                clingo.Number(0),
                clingo.Function("val", [clingo.Function("int"), clingo.Number(3)]),
            ]
        ),
        clingo.Tuple_(
            [
                operation_expr,
                clingo.Number(1),
                clingo.Function("val", [clingo.Function("int"), clingo.Number(4)]),
            ]
        ),
    }


def test_domain_computation_exports_python_extract_statement_error_output() -> None:
    input_name = clingo.String("a")
    input_var = clingo.Function("variable", [input_name])
    binding = clingo.Tuple_(
        [
            clingo.Function("val", [clingo.Function("string"), input_name]),
            input_var,
        ]
    )
    operation_expr = clingo.Function(
        "operation",
        [
            clingo.Function(
                "pythonExtract",
                [
                    clingo.String("assert(False)"),
                    clingo.String("__succeeds"),
                ],
            ),
            symbol_sequence(binding),
        ],
    )

    computed = DomainComputation.compute(
        (
            operation_expr,
            input_var,
            clingo.Function(
                "variable_define", [input_name, clingo.Function("val", [clingo.Function("int"), clingo.Number(4)])]
            ),
        ),
        (),
    )

    assert set(computed.python_evaluation_output_symbols()) == {
        clingo.Tuple_(
            [
                operation_expr,
                clingo.Number(0),
                clingo.Function("bad"),
            ]
        ),
        clingo.Tuple_(
            [
                operation_expr,
                clingo.Number(0),
                clingo.Function(
                    "error",
                    [
                        clingo.Function("expression", [clingo.Function("pythonError")]),
                        clingo.String("AssertionError()"),
                    ],
                ),
            ]
        ),
    }


def test_domain_computation_groups_python_extract_outputs_with_shared_inputs() -> None:
    solver_identifier = clingo.Number(101)
    seen: list[int] = []
    evaluator._solver_environment[101] = {"seen": seen}

    variable_name = clingo.String("x")
    variable_expr = clingo.Function("variable", [variable_name])
    binding = clingo.Tuple_(
        [
            clingo.Function("val", [clingo.Function("string"), variable_name]),
            variable_expr,
        ]
    )
    first_expr = clingo.Function(
        "operation",
        [
            clingo.Function(
                "pythonExtract",
                [
                    clingo.String("seen.append(x)\ny = x * 10\nz = y + 1"),
                    clingo.String("y"),
                ],
            ),
            symbol_sequence(binding),
        ],
    )
    second_expr = clingo.Function(
        "operation",
        [
            clingo.Function(
                "pythonExtract",
                [
                    clingo.String("seen.append(x)\ny = x * 10\nz = y + 1"),
                    clingo.String("z"),
                ],
            ),
            symbol_sequence(binding),
        ],
    )

    try:
        computed = DomainComputation.compute(
            (
                first_expr,
                second_expr,
                variable_expr,
                clingo.Function(
                    "variable_define",
                    [variable_name, clingo.Function("val", [clingo.Function("int"), clingo.Number(1)])],
                ),
                clingo.Function(
                    "variable_domain",
                    [variable_name, clingo.Function("val", [clingo.Function("int"), clingo.Number(2)])],
                ),
            ),
            solver_identifiers=(solver_identifier,),
        )
    finally:
        evaluator._solver_environment.pop(101, None)

    assert computed.expression_domains[first_expr] == Domain.integers(10, 20)
    assert computed.expression_domains[second_expr] == Domain.integers(11, 21)
    assert seen == [1, 2]
    assert set(computed.python_evaluation_output_symbols()) == {
        clingo.Tuple_(
            [
                first_expr,
                clingo.Number(0),
                clingo.Function("val", [clingo.Function("int"), clingo.Number(10)]),
            ]
        ),
        clingo.Tuple_(
            [
                first_expr,
                clingo.Number(1),
                clingo.Function("val", [clingo.Function("int"), clingo.Number(20)]),
            ]
        ),
        clingo.Tuple_(
            [
                second_expr,
                clingo.Number(0),
                clingo.Function("val", [clingo.Function("int"), clingo.Number(11)]),
            ]
        ),
        clingo.Tuple_(
            [
                second_expr,
                clingo.Number(1),
                clingo.Function("val", [clingo.Function("int"), clingo.Number(21)]),
            ]
        ),
    }
