"""Tests for the old-to-new constraint-handler fact converter and SSA."""

# pyright: reportPrivateUsage=false

import json
from pathlib import Path

import pytest

from constraint_handler import (
    LABEL_ANONYMOUS,
    FailIntegrityExn,
    Operator,
    PreprocessOptions,
    Preprocessor,
    Python,
    SolveOptions,
    VariableRef,
    internal_input,
)
from constraint_handler.domains import Domain
from constraint_handler.internal_input import ValueDef, ValueType

from .audit_complex import audit_case, current_value, legacy_value
from .converter import (
    ConversionError,
    UnsupportedFeatureError,
    convert_file,
    convert_string,
    main,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
CORRECTNESS_DIR = REPO_ROOT / "tests" / "correctness"


def test_convert_variable_domains_and_defaults() -> None:
    """Verify conversion of boolDomain, fromFacts, open, definition, and defaults."""
    source = """
    variable_declare(b, boolDomain, "bool_lbl").
    variable_declare(x, fromFacts, "x_lbl").
    variable_domain(x, val(int, 1..3)).
    variable_declare(y, open).
    variable_choice(y, val(int, (10; 20)), "choice_lbl").
    variable_assign(y, val(int, 10), "assign_lbl").
    variable_default(y, val(int, 0)).
    variable_default(y, val(int, 20), operation(eq, (variable(x), (val(int, 2), ()))), 5, "def_lbl").
    variable_declare(z, definition).
    variable_define(z, operation(mod, (variable(x), (val(int, 2), ())))).
    variable_declare(empty_from_facts, fromFacts).
    variable_declare(empty_def, definition).
    """
    store = convert_string(source)

    b_var = store.variables[VariableRef("b")]
    assert [store._expressions[c.value] for c in b_var.choices] == [
        ValueDef(ValueType.boolean, False),
        ValueDef(ValueType.boolean, True),
    ]
    assert [c.label for c in b_var.choices] == ["bool_lbl", "bool_lbl"]

    x_var = store.variables[VariableRef("x")]
    assert [store._expressions[c.value] for c in x_var.choices] == [
        ValueDef(ValueType.integer, 1),
        ValueDef(ValueType.integer, 2),
        ValueDef(ValueType.integer, 3),
    ]
    assert all(c.label == "x_lbl" for c in x_var.choices)

    y_var = store.variables[VariableRef("y")]
    assert [store._expressions[c.value] for c in y_var.choices] == [
        ValueDef(ValueType.integer, 10),
        ValueDef(ValueType.integer, 20),
    ]
    assert len(y_var.definitions) == 1
    assert y_var.definitions[0].label == "assign_lbl"
    assert len(y_var.defaults) == 2
    assert (y_var.defaults[0].priority, y_var.defaults[0].label) == (
        0,
        LABEL_ANONYMOUS,
    )
    assert (y_var.defaults[1].priority, y_var.defaults[1].label) == (5, "def_lbl")

    z_var = store.variables[VariableRef("z")]
    assert store._expressions[z_var.definitions[0].value] == internal_input.Operation(
        Operator.mod, (VariableRef("x"), ValueDef(ValueType.integer, 2))
    )

    assert store.variables[VariableRef("empty_from_facts")].choices == []
    assert store.variables[VariableRef("empty_def")].definitions == []


def test_convert_float_string_and_none_values() -> None:
    """Verify conversion of val(float, ...), val(string, ...), and val(none, ...)."""
    source = """
    variable_define(f1, val(float, float("1.5"))).
    variable_define(f2, val(float, 2)).
    variable_define(st, val(string, "hello")).
    variable_define(n, val(none, none)).
    """
    store = convert_string(source)
    assert store._expressions[store.variables[VariableRef("f1")].definitions[0].value] == ValueDef(
        ValueType.real, 1.5
    )
    assert store._expressions[store.variables[VariableRef("f2")].definitions[0].value] == ValueDef(
        ValueType.real, 2.0
    )
    assert store._expressions[store.variables[VariableRef("st")].definitions[0].value] == ValueDef(
        ValueType.string, "hello"
    )
    assert store._expressions[store.variables[VariableRef("n")].definitions[0].value] == ValueDef(ValueType.none, None)


def test_convert_sets() -> None:
    """Verify conversion of variable_declare(s, set), set_baseDomain, and set_assign."""
    store = convert_file(CORRECTNESS_DIR / "set" / "conditional_assign.lp")
    assert VariableRef("s") in store.set_variables
    assert VariableRef("candidates") in store.set_variables

    s_set = store.set_variables[VariableRef("s")]
    assert len(s_set.assigns) == 5
    assert s_set.assigns[3].label == "named"

    cand_set = store.set_variables[VariableRef("candidates")]
    assert len(cand_set.bases) == 1
    assert store._expressions[cand_set.bases[0].value] == ValueDef(ValueType.integer, 6)
    assert len(cand_set.assigns) == 1
    assert store._expressions[cand_set.assigns[0].condition] == VariableRef("include")

    empty_set_store = convert_string("variable_declare(empty_s, set).")
    assert empty_set_store.set_variables[VariableRef("empty_s")].bases == []
    assert empty_set_store.set_variables[VariableRef("empty_s")].assigns == []


def test_ensure_maps_to_check_and_evaluate_adds_declaration() -> None:
    """Verify ensure maps to check() and evaluate/bool_evaluate create artificial definitions."""
    source = """
    variable_declare(x, fromFacts).
    variable_domain(x, val(int, 1..2)).
    ensure(operation(gt, (variable(x), (val(int, 0), ()))), "must_be_pos").
    evaluate(operation(add, (variable(x), (val(int, 1), ()))), "eval_lbl").
    bool_evaluate(operation(eq, (variable(x), (val(int, 1), ()))), "bool_lbl").
    """
    store = convert_string(source)
    assert len(store.constraints) == 1
    constraint = store.constraints[0]
    assert constraint.is_check is True
    assert constraint.label == "must_be_pos"

    eval_def = store.variables[VariableRef("__evaluate_0")].definitions[0]
    assert eval_def.label == "eval_lbl"
    assert store._expressions[eval_def.value] == internal_input.Operation(
        Operator.add, (VariableRef("x"), ValueDef(ValueType.integer, 1))
    )

    bool_def = store.variables[VariableRef("__bool_evaluate_0")].definitions[0]
    assert bool_def.label == "bool_lbl"
    assert store._expressions[bool_def.value] == internal_input.Operation(
        Operator.eq, (VariableRef("x"), ValueDef(ValueType.integer, 1))
    )


def test_ssa_conditional_if_and_seq2() -> None:
    """Verify SSA conversion of if-then-else and seq2 using conditional variable_define."""
    store = convert_file(CORRECTNESS_DIR / "execution" / "main_absolut.lp")
    in_ref = VariableRef("execution_input(absolut,x)")
    out_ref = VariableRef("execution_output(absolut,y)")
    assert in_ref in store.variables
    assert out_ref in store.variables

    merged_ref = VariableRef("loc(absolut_y_3)")
    assert merged_ref in store.variables
    defs = store.variables[merged_ref].definitions
    assert len(defs) == 2
    cond_then = store._expressions[defs[0].condition]
    cond_else = store._expressions[defs[1].condition]
    assert cond_then == internal_input.Operation(Operator.geq, (in_ref, ValueDef(ValueType.integer, 0)))
    assert cond_else == internal_input.Operation(Operator.lnot, (cond_then,))
    assert store._expressions[store.variables[out_ref].definitions[0].value] == merged_ref


def test_ssa_swap_and_change() -> None:
    """Verify SSA variable versioning across sequential assignments and branches."""
    swap_store = convert_file(CORRECTNESS_DIR / "execution" / "main_swap.lp")
    assert VariableRef("execution_output(swap,x)") in swap_store.variables
    assert VariableRef("execution_output(swap,y)") in swap_store.variables

    change_store = convert_file(CORRECTNESS_DIR / "execution" / "change.lp")
    assert VariableRef("execution_output(prg,x)") in change_store.variables


def test_ssa_assert_and_conditional_assert() -> None:
    """Verify top-level and branch-guarded assert statements become checks."""
    assert_store = convert_file(CORRECTNESS_DIR / "execution" / "assert.lp")
    assert len(assert_store.constraints) == 1
    assert assert_store.constraints[0].is_check is True
    store_expr = assert_store._expressions[assert_store.constraints[0].expr]
    assert store_expr == internal_input.Operation(
        Operator.neq,
        (
            VariableRef("execution_input(myfun,x)"),
            VariableRef("execution_input(myfun,y)"),
        ),
    )

    cond_assert_store = convert_file(CORRECTNESS_DIR / "execution" / "conditional_assert.lp")
    assert len(cond_assert_store.constraints) == 1
    cond_expr = cond_assert_store._expressions[cond_assert_store.constraints[0].expr]
    assert isinstance(cond_expr, internal_input.Operation)
    assert cond_expr.op == Operator.limp


def test_ssa_statement_python_tuple_and_internal_vars() -> None:
    """Verify statement_python uses python_eval + tuple_get and hides internal temporaries."""
    list_store = convert_file(CORRECTNESS_DIR / "execution" / "python_list.lp")
    for prg in ("prg1", "prg2", "prg3"):
        tuple_ref = VariableRef(f"loc({prg}__py_tuple_1)")
        x_ssa_ref = VariableRef(f"loc({prg}_x_2)")
        out_ref = VariableRef(f'execution_output({prg},"x")')
        assert tuple_ref in list_store.variables
        assert x_ssa_ref in list_store.variables
        assert out_ref in list_store.variables
        # Internal variable 'l' must NOT be extracted into the store!
        assert all("_l_" not in v.name for v in list_store.variables)

        tuple_def = list_store._expressions[list_store.variables[tuple_ref].definitions[0].value]
        assert isinstance(tuple_def, internal_input.Operation)
        assert tuple_def.op == Operator.python_eval
        assert isinstance(tuple_def.args[0], Python)

        get_def = list_store._expressions[list_store.variables[x_ssa_ref].definitions[0].value]
        assert get_def == internal_input.Operation(Operator.tuple_get, (tuple_ref, ValueDef(ValueType.integer, 1)))


def test_ssa_statement_python_with_inputs_and_integrity() -> None:
    """Verify statement_python passes string-named inputs and emits integrity checks."""
    pyt_store = convert_file(CORRECTNESS_DIR / "execution" / "main_pyt.lp")
    assert VariableRef('execution_output(pyt,"x")') in pyt_store.variables
    assert VariableRef("execution_output(pyt,y)") in pyt_store.variables

    aug_store = convert_file(CORRECTNESS_DIR / "execution" / "python_augassign.lp")
    assert VariableRef('execution_output(prg,"x")') in aug_store.variables

    ign_store = convert_file(CORRECTNESS_DIR / "execution" / "python_integrity_should_be_ignored.lp")
    assert len(ign_store.constraints) == 2
    assert all(c.is_check for c in ign_store.constraints)


@pytest.mark.parametrize("enabled", (False, True))
@pytest.mark.parametrize(
    "code",
    (
        "raise solver_environment.FailIntegrityExn",
        "raise FailIntegrityExn()",
        "solver_environment.constrain(False)",
        "constrain(False)",
        "reject()",
        "y = 3\nraise solver_environment.FailIntegrityExn\ny = 4",
    ),
)
def test_ssa_integrity_failure_models(enabled: bool, code: str) -> None:
    """Reject reached failures while preserving models with inactive statements."""
    def reject() -> None:
        """Signal failure indirectly through a Python context function."""
        raise FailIntegrityExn

    source = f'''
    variable_define(execution_input(p,"enabled"),val(bool,{str(enabled).lower()})).
    execution_run(p).
    execution_declare(p,
        if(variable("enabled"),statement_python({json.dumps(code)}),assign("y",val(int,0))),
        ("enabled",()),("y",())).
    '''
    store = convert_string(source)
    assert VariableRef("__fail") in store.variables
    assert len(store.constraints) == 1
    assert store.constraints[0].is_check
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add_context("reject", reject)
    preprocessor.add(store)
    problem, diagnostics = preprocessor.preprocess()
    assert not diagnostics.has_errors
    result = problem.create_solver(SolveOptions()).solve()
    assert result.unsatisfiable if enabled else result.satisfiable


@pytest.mark.parametrize("separate_executions", (False, True))
@pytest.mark.parametrize("failure_position", (None, 0, 1))
def test_ssa_common_failure_flag(separate_executions: bool, failure_position: int | None) -> None:
    """Keep one write-once failure flag across statements and executions."""
    statements = [
        f"statement_python({json.dumps('raise FailIntegrityExn' if index == failure_position else 'pass')})"
        for index in range(2)
    ]
    if separate_executions:
        source = "\n".join(
            f"execution_run(p{index}). execution_declare(p{index},{statement},(),())."
            for index, statement in enumerate(statements)
        )
    else:
        source = f"execution_run(p). execution_declare(p,seq2({','.join(statements)}),(),())."
    store = convert_string(source)
    assert len(store.constraints) == 1
    definitions = store.variables[VariableRef("__fail")].definitions
    assert len(definitions) == 2
    assert all(store.expressions[entry.value] == ValueDef(ValueType.boolean, True) for entry in definitions)
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    problem, diagnostics = preprocessor.preprocess()
    assert not diagnostics.has_errors
    result = problem.create_solver(SolveOptions()).solve()
    assert result.satisfiable if failure_position is None else result.unsatisfiable


@pytest.mark.parametrize("enabled", (False, True))
def test_ssa_python_internal_failure_condition(enabled: bool) -> None:
    """Keep Python's internal control flow when producing the ordinary failure flag."""
    code = "y = 3\nif enabled:\n    raise FailIntegrityExn\ny = 4"
    source = f'''
    variable_define(execution_input(p,"enabled"),val(bool,{str(enabled).lower()})).
    execution_run(p).
    execution_declare(p,statement_python({json.dumps(code)}),("enabled",()),("y",())).
    '''
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(convert_string(source))
    problem, diagnostics = preprocessor.preprocess()
    assert not diagnostics.has_errors
    result = problem.create_solver(SolveOptions()).solve()
    assert result.unsatisfiable if enabled else result.satisfiable
    if not enabled:
        assert problem.domains[VariableRef('execution_output(p,"y")')] == Domain(ints=frozenset({4}))


@pytest.mark.parametrize(
    "source",
    (
        'variable_define("__fail",val(bool,false)).',
        'variable_declare(__fail,fromFacts).',
        'execution_run(p). execution_declare(p,assign("__fail",val(bool,false)),(),()).',
        'execution_run(p). execution_declare(p,statement_python("__fail = False"),(),()).',
        'execution_run(p). execution_declare(p,statement_python("__fail += 1"),(),()).',
        'execution_declare(p,noop,("__fail",()),()).',
        'execution_declare(p,noop,(),("__fail",())).',
    ),
)
def test_ssa_reserves_failure_variable(source: str) -> None:
    """Prevent legacy input from assigning or supplying the converter's failure flag."""
    with pytest.raises(ConversionError, match="__fail.*reserved"):
        convert_string(source)


def test_ssa_unrun_execution_and_implicit_variables() -> None:
    """Verify unrun executions define None outputs and implicit variables resolve cleanly."""
    unrun_store = convert_string("""
        execution_declare(p, assign(y, val(int, 1)), (x, ()), (y, ())).
        """)
    out_def = unrun_store.variables[VariableRef("execution_output(p,y)")].definitions[0]
    assert unrun_store._expressions[out_def.value] == ValueDef(ValueType.none, None)

    imp_store = convert_file(CORRECTNESS_DIR / "execution" / "implicit_variable.lp")
    v5_def = imp_store.variables[VariableRef("execution_output(miss_input,v5)")].definitions[0]
    assert imp_store._expressions[v5_def.value] == ValueDef(ValueType.none, None)


def test_static_python_and_lambda_expressions() -> None:
    """Verify conversion of python(...) expressions and lambda(...) operations."""
    static_store = convert_file(CORRECTNESS_DIR / "python" / "static.lp")
    assert VariableRef("constant") in static_store.variables
    assert VariableRef("abs_value") in static_store.variables
    assert VariableRef("sum_value") in static_store.variables

    lam_store = convert_string("""
        variable_define(r, operation(lambda((x, ()), operation(add, (variable(x), (val(int, 1), ())))), (val(int, 5), ()))).
        variable_define(f, lambda((x, ()), variable(x))).
        variable_define(call_f, operation(variable(f), (val(int, 3), ()))).
        variable_define(tup, (val(int, 1), val(string, "a"))).
        """)
    assert VariableRef("r") in lam_store.variables
    assert VariableRef("f") in lam_store.variables
    assert VariableRef("call_f") in lam_store.variables
    assert VariableRef("tup") in lam_store.variables


@pytest.mark.parametrize(
    ("fixture", "expected"),
    [
        ("python/static.lp", {"constant": 2, "abs_value": 3, "sum_value": 7}),
        ("expression/python.lp", {"x": 2, "y": -1, "z": 1}),
    ],
)
def test_preprocess_python_expressions(fixture: str, expected: dict[str, int]) -> None:
    """Evaluate legacy Python values and function calls through preprocessing."""
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(convert_file(CORRECTNESS_DIR / fixture))
    prepared, diagnostics = preprocessor.preprocess()
    assert not diagnostics.items
    for name, value in expected.items():
        assert prepared.domains[VariableRef(name)] == Domain(ints=frozenset({value}))


@pytest.mark.parametrize(
    ("expression", "operator", "domain"),
    [
        ('operation(float_div,(val(int,7),(val(int,2),())))', Operator.real_div, Domain(reals=frozenset({3.5}))),
        ('operation(float_from_int,(val(int,2),()))', Operator.real_from_int, Domain(reals=frozenset({2.0}))),
        ('operation(int_from_float,(val(float,float("2.5")),()))', Operator.int_from_real, Domain(ints=frozenset({2}))),
    ],
)
def test_preprocess_renamed_operators(expression: str, operator: Operator, domain: Domain) -> None:
    """Map legacy float operator names to the current real operators."""
    store = convert_string(f"variable_define(result,{expression}).")
    result = VariableRef("result")
    definition = store.expressions[store.variables[result].definitions[0].value]
    assert isinstance(definition, internal_input.Operation)
    assert definition.op == operator
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    prepared, diagnostics = preprocessor.preprocess()
    assert not diagnostics.items
    assert prepared.domains[result] == domain


@pytest.mark.parametrize(
    "bad_source",
    [
        "variable_define(x, bad).",
        "variable_declare(m, multimap).",
        "multimap_assign(m, val(int, 1), val(int, 2)).",
        "variable_define(x, operation(find, (variable(m), (val(int, 1), ())))).",
        "optimize_maximizeSum(variable(x), 0, 0).",
        "optimize_precision(val(int, 1), 0).",
        "preference_maximizeScore.",
        "preference_holds(val(bool, true), 1).",
        "preference_variableValue(x, val(int, 1), 1).",
        "warning_ignore(variable(undeclared)).",
        "warning_forbid(variable(badValue)).",
        "default_mode(depends).",
        "execution_declare(p, while(3, val(bool, true), noop), (), ()).",
        "{ a }.",
        "#maximize { 1 : a }.",
        "variable_define(s, val(symbol, alpha)).",
        "variable_define(s, alpha).",
        'variable_define(s, val(symbol, pair(1, "a"))).',
    ],
)
def test_unsupported_features_raise_error(bad_source: str) -> None:
    """Verify unsupported atoms, operators, and directives raise UnsupportedFeatureError."""
    with pytest.raises(UnsupportedFeatureError):
        convert_string(bad_source)


@pytest.mark.parametrize(
    "invalid_source",
    [
        'variable_define(x, "unterminated).',
        "variable_declare(x, unknown_domain).",
        'execution_declare(p, statement_python("def :"), (), ()).',
    ],
)
def test_syntax_and_malformed_facts_raise_conversion_error(
    invalid_source: str,
) -> None:
    """Verify malformed syntax raises ConversionError."""
    with pytest.raises(ConversionError):
        convert_string(invalid_source)


def test_cli_main(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Verify the CLI entry point converts a file and reports counts."""
    lp_file = tmp_path / "sample.lp"
    lp_file.write_text("variable_define(x, val(int, 42)).\n", encoding="utf-8")
    assert main([str(lp_file)]) == 0
    captured = capsys.readouterr()
    assert "1 variables" in captured.out
    assert main([]) == 2


def test_audit_clingo_six_value_decoding() -> None:
    """Decode Clingo 6 functions, scalars, and tuples into typed comparison keys."""
    from clingo.core import Library
    from clingo.symbol import parse_term

    lib = Library()
    assert legacy_value(parse_term(lib, '(val(bool,true),val(int,1))')) == current_value(
        parse_term(lib, 'tuple((boolean(true),integer(1)))')
    )
    assert legacy_value(parse_term(lib, 'val(float,float("2.5"))')) == ("real", 2.5)


def test_audit_scalar_python_fixture() -> None:
    """Verify model enumeration and all expected scalar values using Clingo 6."""
    result = audit_case(CORRECTNESS_DIR / "python" / "static.lp")
    assert result["status"] == "expectations_match"
    assert result["checked_expectations"] == 3
    assert result["model_count"] == 1
    assert result["rows"] == 3


def test_audit_set_fixture() -> None:
    """Check set memberships while exposing optional legacy scalar choices."""
    result = audit_case(CORRECTNESS_DIR / "set" / "conditional_assign.lp")
    assert result["status"] == "value_mismatch"
    assert result["ignored_expectations"] == []
    assert result["model_count"] == 5
    assert result["checked_expectations"] == 7
    assert result["failures"] == [
        {"kind": "model_count", "expected": 3, "actual": 5}
    ]


@pytest.mark.parametrize(
    "fixture",
    (
        "from_domain",
        "same_val_multi_expr",
        "manipulation_flat",
        "membership_decomposed",
        "membership_python",
        "missing_declare_repair",
        "nondet_simple",
    ),
)
def test_audit_supported_set_fixtures(fixture: str) -> None:
    """Retain verified legacy set values without claiming diagnostic compatibility."""
    result = audit_case(CORRECTNESS_DIR / "set" / f"{fixture}.lp")
    assert result["status"] in {
        "expectations_match",
        "values_match_diagnostics_unchecked",
    }
    assert result["exhausted"]
    assert result["checked_expectations"] > 0
    assert result["failures"] == []


def test_audit_distinguishes_unknown_input_domains() -> None:
    """Expose unsupported tuple contents and downstream propagator requirements."""
    result = audit_case(
        CORRECTNESS_DIR / "type" / "statement_python" / "unknown_vs_untyped.lp",
        domains_only=True,
    )
    assert result["status"] == "domains_only"
    assert len(result["unknown_input_calls"]) == 3
    assert len(result["unknown_result_calls"]) == 3
    assert result["domain_summary"]["roots"]["unknown"] == 4
