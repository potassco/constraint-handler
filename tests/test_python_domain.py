from __future__ import annotations

from itertools import product
import math

import clingo
import pytest

import constraint_handler.evaluator as evaluator
import constraint_handler.solver_environment as solver_environment
from constraint_handler.schemas import expression, operators
from constraint_handler.utils.python_domain import Domain


def build_domain(*values, is_bad: bool = False) -> Domain:
    domain = Domain.empty()
    for value in values:
        domain.absorb(Domain.from_runtime(value))
    domain.is_bad = domain.is_bad or is_bad
    return domain


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
    for args in product(*arg_options):
        try:
            applied = evaluator.operator(operation, args, (), {})
        except Exception:
            result.is_bad = True
            continue
        if applied.value is expression.Bad.bad:
            result.is_bad = True
            continue
        result.absorb(Domain.from_runtime(applied.value))
    return result


def assert_same_semantics(operation: object, *domains: Domain) -> None:
    assert Domain.apply(operation, *domains) == expected_domain_from_evaluator(operation, *domains)


def test_value_helpers_preserve_set_style_numeric_deduplication() -> None:
    domain = Domain(
        is_bad=True,
        bools={True},
        ints={1, 2},
        floats={1.0, 2.5},
        is_none=True,
        strings={"x"},
        symbols={clingo.Function("sym")},
        tuples={("tuple",)},
    )
    domain.absorb(Domain.set_values(frozenset({"member"})))

    assert domain.value_count() == 8
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

    assert Domain.from_symbol(clingo.Function("val", [clingo.Function("bool"), clingo.Function("true")])) == Domain.booleans(True)
    assert Domain.from_symbol(clingo.Function("val", [clingo.Function("int"), clingo.Number(7)])) == Domain.integers(7)
    assert Domain.from_symbol(
        clingo.Function("val", [clingo.Function("float"), clingo.Function("float", [clingo.String("2.5")])])
    ) == Domain.floats_only(2.5)
    assert Domain.from_symbol(clingo.Function("val", [clingo.Function("none"), clingo.Function("none")])) == Domain.none()
    assert Domain.from_symbol(clingo.Function("val", [clingo.Function("string"), clingo.String("txt")])) == Domain.strings_only("txt")
    assert Domain.from_symbol(clingo.Function("val", [clingo.Function("symbol"), plain_symbol])) == Domain.symbols_only(plain_symbol)
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
    assert Domain.value_to_symbol((1, "x")) == clingo.Tuple_([
        Domain.value_to_symbol(1),
        Domain.value_to_symbol("x"),
    ])


def test_options_without_none_and_has_values_cover_empty_optional_and_bad_cases() -> None:
    domain = Domain.merge(Domain.booleans(True), Domain.none(), Domain.bad())

    assert domain.has_values() is True
    assert domain.without_none() == Domain(is_bad=True, bools={True})
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
    Domain.GLOBAL_SET_UIDS.clear()
    Domain.NEXT_SET_UID = 0
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
    domain = Domain(is_bad=True, ints={1})
    domain.absorb(Domain.set_values(frozenset({1, 2})))
    Domain.GLOBAL_SET_UIDS.clear()
    Domain.NEXT_SET_UID = 0
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
    assert Domain.compute_domain(clingo.Function(operation)) == expected


def test_compute_domain_variadic_fold_cases() -> None:
    assert Domain.compute_domain(
        clingo.Function("add"),
        Domain.integers(1),
        Domain.integers(2),
        Domain.integers(3),
    ) == Domain.integers(6)
    assert Domain.compute_domain(
        clingo.Function("leqv"),
        Domain.booleans(True),
        Domain.booleans(False),
    ) == Domain.booleans(False)
    assert Domain.compute_domain(
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
        (operators.LogicOperator.leqv, (build_domain(True, False, None), build_domain(True, False))),
        (operators.LogicOperator.limp, (build_domain(True, False, None), build_domain(True, False, None))),
        (operators.LogicOperator.lnot, (build_domain(True, False, None),)),
        (operators.LogicOperator.lxor, (build_domain(True, False, None), build_domain(True, False))),
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
        (operators.SetOperator.inter, (build_domain(frozenset({1, 2}), frozenset({2, 3})), build_domain(frozenset({2}), frozenset({3})))),
        (operators.SetOperator.diff, (build_domain(frozenset({1, 2}), frozenset({2, 3})), build_domain(frozenset({2})))),
        (operators.SetOperator.subset, (build_domain(frozenset(), frozenset({1})), build_domain(frozenset({1}), frozenset({1, 2})))),
    ],
)
def test_apply_matches_evaluator_for_set_operators(operation: object, domains: tuple[Domain, ...]) -> None:
    assert_same_semantics(operation, *domains)


def test_apply_tracks_numeric_corner_cases_and_type_mismatches() -> None:
    assert Domain.apply(operators.ArithmeticOperator.sqrt, build_domain(-1)).is_bad is True
    assert Domain.compute_domain(clingo.Function("add"), build_domain("x"), build_domain(1)) == Domain.bad()
    assert Domain.compute_domain(clingo.Function("float_div"), build_domain(1.0), build_domain(0.0)) == Domain.bad()


def test_apply_length_marks_invalid_scalar_inputs_bad_but_keeps_valid_lengths() -> None:
    domain = build_domain("abcd", frozenset({1, 2}), (1, 2, 3), 9, None)

    assert Domain.apply(expression.StringOperator.length, domain) == Domain(is_bad=True, ints={2, 3, 4})


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
    ) == Domain.set_values(frozenset({1, 2})).absorb(Domain.bad())


def test_apply_if_default_and_hasvalue_cover_none_bad_and_false_cases() -> None:
    assert Domain.apply(expression.ConditionalOperator.IF, build_domain(True, False, None), build_domain(7)) == Domain(
        ints={7},
        is_none=True,
    )
    assert Domain.apply(expression.ConditionalOperator.default, build_domain(None, 1), build_domain(2, 3)) == build_domain(1, 2, 3)
    assert Domain.apply(expression.ConditionalOperator.hasValue, build_domain(None, 1, frozenset())) == Domain.booleans(True, False)
    assert Domain.apply(expression.ConditionalOperator.hasValue, Domain.bad()) == Domain(is_bad=True)


def test_apply_max_and_min_follow_evaluator_cross_product_semantics() -> None:
    left = build_domain(1, 5)
    right = build_domain(2, 3)

    assert Domain.apply(expression.OtherOperator.max, left, right) == expected_domain_from_evaluator(expression.OtherOperator.max, left, right)
    assert Domain.apply(expression.OtherOperator.min, left, right) == expected_domain_from_evaluator(expression.OtherOperator.min, left, right)


def test_compute_domain_symbolic_dispatch_matches_apply_for_small_cases() -> None:
    assert Domain.compute_domain(clingo.Function("sub"), build_domain(7), build_domain(2)) == Domain.integers(5)
    assert Domain.compute_domain(clingo.Function("conj"), build_domain(True, None), build_domain(False)) == Domain.booleans(False)
    assert Domain.compute_domain(clingo.Function("concat"), build_domain("a"), build_domain("b", "c")) == Domain.strings_only("ab", "ac")
    assert Domain.compute_domain(clingo.Function("set_make"), build_domain(1, 2), build_domain("x")) == Domain.set_values(
        frozenset({1, "x"}),
        frozenset({2, "x"}),
    )


def test_compute_domain_if_requires_exactly_two_arguments() -> None:
    assert Domain.compute_domain(clingo.Function("if"), Domain.booleans(True)) == Domain.bad()


def test_compute_domain_returns_empty_when_any_child_domain_is_empty() -> None:
    assert Domain.compute_domain(clingo.Function("add"), Domain.empty(), build_domain(1)) == Domain.empty()


def test_compute_domain_rejects_non_function_operators() -> None:
    assert Domain.compute_domain(clingo.Number(7), build_domain(1)) == Domain.bad()


def test_compute_domain_python_callable_matches_evaluator_success_cases() -> None:
    operation = clingo.Function("python", [clingo.String("lambda x, y: x + y")])

    assert Domain.compute_domain(operation, build_domain(1, 2), build_domain(10)) == build_domain(11, 12)


def test_compute_domain_python_callable_exception_keeps_none_semantics_from_evaluator() -> None:
    operation = clingo.Function("python", [clingo.String("lambda x: 10 / x")])

    assert Domain.compute_domain(operation, build_domain(2, 0)) == build_domain(5.0, None)


def test_compute_domain_python_callable_bad_code_is_bad() -> None:
    operation = clingo.Function("python", [clingo.String("not valid python")])

    assert Domain.compute_domain(operation, build_domain(1)) == Domain.bad()


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
        assert Domain.compute_domain(operation, build_domain(("left", 1)), build_domain(("right", 2)), solver_identifiers=solver_id) == Domain.integers(3)
        assert Domain.compute_domain(succeeds_operation, build_domain()) == Domain.empty()
        assert Domain.compute_domain(succeeds_operation, build_domain(("left", 1)), solver_identifiers=solver_id) == Domain.booleans(False)
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

    assert Domain.compute_domain(binding_operation, build_domain(1)) == Domain.bad()
    assert Domain.compute_domain(eval_operation, build_domain(("left", 1))) == Domain.bad()
