"""Tests for lossless ground ASP fact generation."""

import operator
from collections.abc import Callable
from importlib.resources import files
from itertools import combinations, pairwise

import pytest
from clingo.control import Control
from clingo.core import Library
from clingo.script import enable_python
from clingo.solve import Model
from clingo.symbol import Function, Number, String, Symbol, SymbolType, parse_term

from constraint_handler import (
    ConstraintStore,
    Engine,
    Operation,
    Operator,
    PreprocessOptions,
    Preprocessor,
    Python,
    SolveOptions,
    VariableRef,
)
from constraint_handler.asp_facts import asp_facts
from constraint_handler.dispatching import DispatchStore
from constraint_handler.domains import Domain, DomainStore
from constraint_handler.domains.values import SetValue
from constraint_handler.internal_input import SetVariable
from constraint_handler.python_input import Expr, OperationArg


@pytest.fixture
def lib() -> Library:
    """Provide one Clingo library for constructing and parsing test symbols."""
    library = Library()
    enable_python(library)
    return library


@pytest.mark.parametrize("values", ((3, 5), (-7, -2, 4, 23, 42)))
def test_native_linear_integer(lib: Library, values: tuple[int, ...]) -> None:
    """Sum indexed weighted terms only when every optional input is present."""
    store = ConstraintStore()
    left, right, negative = (
        VariableRef(name) for name in ("left", "right", "negative")
    )
    for variable, choices in ((left, values), (right, values), (negative, (4, 6))):
        store.choose_from_iterator(variable, choices)
    result_variable = VariableRef("result")
    store.define(
        result_variable,
        Operation(Operator.linear_integer, ((2, left), (2, right), (-1, negative), 7)),
    )
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    problem, diagnostics = preprocessor.preprocess()
    assert not diagnostics.has_errors
    result_id = problem.store.variables[result_variable].definitions[0].value
    assert problem.engines[result_id] == Engine.native
    assert not any(fact.name == "solution" for fact in problem.asp_facts)
    assert {str(fact) for fact in problem.asp_facts if fact.name == "order_next"} == {
        *(
            f'order_next(variable("{name}"),{lower},{upper})'
            for name in ("left", "right")
            for lower, upper in pairwise(values)
        ),
        'order_next(variable("negative"),4,6)',
    }
    models: list[dict[str, int]] = []
    control = Control(lib, ["0"])
    control.parse_string("\n".join(f"{fact}." for fact in problem.asp_facts))
    for encoding in ("native.lp", "integer.lp"):
        control.parse_string(
            files("constraint_handler").joinpath("encoding", encoding).read_text()
        )
    control.ground([("base", [])])
    outcome = control.solve(
        on_model=lambda model: models.append(
            {
                atom.arguments[0].arguments[0].string: atom.arguments[1]
                .arguments[0]
                .number
                for atom in model.symbols(atoms=True)
                if atom.name == "value"
                and atom.arguments[0].type == SymbolType.Function
                and atom.arguments[0].name == "variable"
            }
        )
    )
    assert outcome.satisfiable
    assert len(models) == (len(values) + 1) ** 2 * 3
    for model in models:
        if all(name in model for name in ("left", "right", "negative")):
            assert model["result"] == (
                2 * model["left"] + 2 * model["right"] - model["negative"] + 7
            )
        else:
            assert "result" not in model


@pytest.mark.parametrize(
    "arguments, expected",
    (
        ((7,), 7),
        (((-2, VariableRef("input")), 7), 1),
        (((0, VariableRef("input")), 7), 7),
        (((2, VariableRef("input")), (2, VariableRef("input")), 7), 19),
    ),
)
def test_native_linear_integer_unfolded(
    lib: Library, arguments: tuple[OperationArg, ...], expected: int
) -> None:
    """Evaluate native edge cases without normalization folding their terms."""
    store = ConstraintStore()
    store.define(VariableRef("input"), 3)
    store.define(VariableRef("result"), Operation(Operator.linear_integer, arguments))
    engines = DispatchStore((expr_id, Engine.native) for expr_id in store.expressions)
    control = Control(lib, ["0"])
    control.parse_string(
        "\n".join(
            f"{fact}."
            for fact in asp_facts(
                lib,
                store,
                engines,
                DomainStore({VariableRef("input"): Domain(ints=frozenset({3}))}),
            )
        )
    )
    for encoding in ("native.lp", "integer.lp"):
        control.parse_string(
            files("constraint_handler").joinpath("encoding", encoding).read_text()
        )
    control.ground([("base", [])])
    models: list[set[str]] = []
    outcome = control.solve(
        on_model=lambda model: models.append(
            {str(atom) for atom in model.symbols(atoms=True)}
        )
    )
    assert outcome.satisfiable
    assert len(models) == 1
    assert f'value(variable("result"),integer({expected}))' in models[0]


@pytest.mark.parametrize("relation", ("eq", "neq", "lt", "leq", "gt", "geq"))
@pytest.mark.parametrize("arity", (0, 1, 3))
def test_native_linear_comparison(lib: Library, relation: str, arity: int) -> None:
    """Compare sparse weighted inputs directly, preserving optional absence."""
    store = ConstraintStore()
    inputs = tuple(VariableRef(f"input{index}") for index in range(arity))
    coefficients = (2, 2, -3)[:arity]
    for variable in inputs:
        store.choose_from_iterator(variable, (-7, -2, 4))
    result_variable = VariableRef("result")
    store.define(
        result_variable,
        Operation(
            Operator.linear_comparison,
            (
                relation,
                *(
                    (coefficient, variable)
                    for coefficient, variable in zip(coefficients, inputs, strict=True)
                ),
                2,
            ),
        ),
    )
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    problem, diagnostics = preprocessor.preprocess()
    assert not diagnostics.has_errors
    result_id = problem.store.variables[result_variable].definitions[0].value
    assert problem.engines[result_id] == Engine.native
    assert not any(
        fact.name in {"solution", "linear_integer_base"} for fact in problem.asp_facts
    )
    control = Control(lib, ["0"])
    control.parse_string("\n".join(f"{fact}." for fact in problem.asp_facts))
    for encoding in ("native.lp", "integer.lp"):
        control.parse_string(
            files("constraint_handler").joinpath("encoding", encoding).read_text()
        )
    control.ground([("base", [])])
    models: list[dict[str, Symbol]] = []
    outcome = control.solve(
        on_model=lambda model: models.append(
            {
                atom.arguments[0].arguments[0].string: atom.arguments[1]
                for atom in model.symbols(atoms=True)
                if atom.name == "value"
                and atom.arguments[0].type == SymbolType.Function
                and atom.arguments[0].name == "variable"
            }
        )
    )
    assert outcome.satisfiable
    assert len(models) == 4**arity
    compare = {
        "eq": operator.eq,
        "neq": operator.ne,
        "lt": operator.lt,
        "leq": operator.le,
        "gt": operator.gt,
        "geq": operator.ge,
    }[relation]
    for model in models:
        if not all(variable.name in model for variable in inputs):
            assert "result" not in model
            continue
        total = 2 + sum(
            coefficient * model[variable.name].arguments[0].number
            for coefficient, variable in zip(coefficients, inputs, strict=True)
        )
        assert model["result"].arguments[0].name == str(compare(total, 0)).lower()


def test_native_linear_comparison_solves_send_more_money(lib: Library) -> None:
    """Solve the full distinct-digit cryptarithm without numeric sum auxiliaries."""
    store = ConstraintStore()
    digits = {name: VariableRef(name) for name in "SENDMORY"}
    for name, variable in digits.items():
        store.choose_from_iterator(variable, range(10))
        store.ensure(Operation(Operator.geq, (variable, 1 if name in "SM" else 0)))
    for left, right in combinations(digits.values(), 2):
        store.ensure(Operation(Operator.neq, (left, right)))
    words = []
    for word in ("SEND", "MORE", "MONEY"):
        words.append(
            Operation(
                Operator.add,
                tuple(
                    Operation(Operator.mult, (10**position, digits[name]))
                    for position, name in enumerate(reversed(word))
                ),
            )
        )
    store.ensure(
        Operation(Operator.eq, (Operation(Operator.add, tuple(words[:2])), words[2]))
    )
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    problem, diagnostics = preprocessor.preprocess()
    assert not diagnostics.has_errors
    assert set(problem.store.variables) == set(digits.values())
    assert set(problem.engines.values()) == {Engine.native}
    assert not any(
        fact.name in {"solution", "linear_integer_base"} for fact in problem.asp_facts
    )
    control = Control(lib, ["0"])
    control.parse_string("\n".join(f"{fact}." for fact in problem.asp_facts))
    for encoding in ("native.lp", "integer.lp"):
        control.parse_string(
            files("constraint_handler").joinpath("encoding", encoding).read_text()
        )
    control.ground([("base", [])])
    models: list[dict[str, int]] = []
    outcome = control.solve(
        on_model=lambda model: models.append(
            {
                atom.arguments[0].arguments[0].string: atom.arguments[1]
                .arguments[0]
                .number
                for atom in model.symbols(atoms=True)
                if atom.name == "value"
                and atom.arguments[0].type == SymbolType.Function
                and atom.arguments[0].name == "variable"
            }
        )
    )
    assert outcome.satisfiable
    assert models == [dict(zip("SENDMORY", (9, 5, 6, 7, 1, 0, 8, 2), strict=True))]


@pytest.mark.parametrize("operator", (Operator.conj, Operator.disj, Operator.leqv))
@pytest.mark.parametrize("arity", (0, 1, 2, 3))
@pytest.mark.parametrize("repeat", (False, True))
def test_native_boolean_short_circuit(
    lib: Library, operator: Operator, arity: int, repeat: bool
) -> None:
    """Evaluate native Boolean operations with optional and repeated operands."""
    store = ConstraintStore()
    inputs = tuple(VariableRef(f"input{index}") for index in range(arity))
    for variable in inputs:
        store.choose_from_iterator(variable, (False, True))
    arguments = inputs + inputs[:1] if repeat else inputs
    result_variable = VariableRef("result")
    store.define(result_variable, Operation(operator, arguments))
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    problem, diagnostics = preprocessor.preprocess()
    assert not diagnostics.has_errors
    result_id = problem.store.variables[result_variable].definitions[0].value
    assert problem.engines[result_id] == Engine.native
    assert set(problem.engines.values()) == {Engine.native}
    assert not any(fact.name == "solution" for fact in problem.asp_facts)
    control = Control(lib, ["0"])
    control.parse_string("\n".join(f"{fact}." for fact in problem.asp_facts))
    for encoding in ("native.lp", "boolean.lp", "complex.lp"):
        control.parse_string(
            files("constraint_handler").joinpath("encoding", encoding).read_text()
        )
    control.ground([("base", [])])
    models: list[dict[str, bool]] = []
    outcome = control.solve(
        on_model=lambda model: models.append(
            {
                atom.arguments[0].arguments[0].string: (
                    atom.arguments[1].arguments[0].name == "true"
                )
                for atom in model.symbols(atoms=True)
                if atom.name == "value"
                and atom.arguments[0].type == SymbolType.Function
                and atom.arguments[0].name == "variable"
            }
        )
    )
    assert outcome.satisfiable
    assert len(models) == 3**arity
    decisive = operator == Operator.disj
    for model in models:
        values = [
            model[variable.name] for variable in arguments if variable.name in model
        ]
        if operator == Operator.leqv:
            if len(values) == len(arguments):
                assert model["result"] == (values.count(False) % 2 == 0)
            else:
                assert "result" not in model
        elif decisive in values:
            assert model["result"] is decisive
        elif len(values) == len(arguments):
            assert model["result"] is not decisive
        else:
            assert "result" not in model


@pytest.mark.parametrize(
    "operator",
    (
        Operator.conj,
        Operator.disj,
        Operator.leqv,
        Operator.eq,
        Operator.neq,
        Operator.linear_integer,
        Operator.linear_comparison,
    ),
)
def test_non_simple_native_operators_remain_complex(operator: Operator) -> None:
    """Use normal splitting costs rather than forcing native implementations."""
    store = ConstraintStore()
    variable, result = VariableRef("input"), VariableRef("result")
    arguments: tuple[OperationArg, ...]
    if operator in {Operator.linear_integer, Operator.linear_comparison}:
        store.choose_from_iterator(variable, (1, 2))
        arguments = ((2, Operation(Operator.abs, (variable,))), 1)
        if operator == Operator.linear_comparison:
            arguments = ("eq", *arguments)
    else:
        store.choose_from_iterator(variable, (False, True))
        arguments = (Operation(Operator.eq, (variable, True)), False)
    store.define(result, Operation(operator, arguments))
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    problem, diagnostics = preprocessor.preprocess()
    assert not diagnostics.has_errors
    result_id = problem.store.variables[result].definitions[0].value
    assert problem.engines[result_id] == Engine.complex
    assert set(problem.store.variables) == {variable, result}
    assert not any(
        fact.name
        in {"boolean_argument", "boolean_equivalence_argument", "linear_integer_term"}
        for fact in problem.asp_facts
    )


@pytest.mark.parametrize("operator", (Operator.conj, Operator.disj))
def test_native_boolean_absent_input_feeds_python(
    lib: Library, operator: Operator
) -> None:
    """Expose short-circuit results to Python despite an absent operand."""
    store = ConstraintStore()
    empty, result = VariableRef("empty"), VariableRef("result")
    decisive = operator == Operator.disj
    store.choose(empty, True, condition=False)
    store.define(result, Operation(operator, (empty, decisive)))
    store.define(VariableRef("negated"), Operation(Operator.lnot, (result,)))
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    problem, diagnostics = preprocessor.preprocess()
    assert not diagnostics.has_errors
    control = Control(lib, ["0"])
    control.parse_string("\n".join(f"{fact}." for fact in problem.asp_facts))
    for encoding in ("native.lp", "boolean.lp", "complex.lp"):
        control.parse_string(
            files("constraint_handler").joinpath("encoding", encoding).read_text()
        )
    control.ground([("base", [])])
    models: list[set[str]] = []
    outcome = control.solve(
        on_model=lambda model: models.append(
            {str(atom) for atom in model.symbols(atoms=True)}
        )
    )
    assert outcome.satisfiable
    assert len(models) == 1
    assert f'value(variable("result"),boolean({str(decisive).lower()}))' in models[0]
    assert (
        f'value(variable("negated"),boolean({str(not decisive).lower()}))' in models[0]
    )


@pytest.mark.parametrize("kind", ("ensure", "check"))
@pytest.mark.parametrize("value", ("boolean(true)", "boolean(false)", "none", None))
def test_constraint_truth_and_existence(
    lib: Library, kind: str, value: str | None
) -> None:
    """Require true values, with absence accepted only by checks."""
    control = Control(lib)
    control.parse_string(f'{kind}(0,"constraint").')
    if value is not None:
        control.parse_string(f"value(0,{value}).")
    control.parse_string(
        files("constraint_handler").joinpath("encoding", "native.lp").read_text()
    )
    control.ground([("base", [])])
    result = control.solve()
    assert result.satisfiable == (
        value == "boolean(true)" or (kind == "check" and value is None)
    )


@pytest.mark.parametrize("kind, expected_models", (("ensure", 1), ("check", 2)))
def test_constraints_on_complex_expression(
    lib: Library, kind: str, expected_models: int
) -> None:
    """Filter false Python rows and distinguish absent optional inputs."""
    store = ConstraintStore()
    variable = VariableRef("x")
    store.choose_from_iterator(variable, (1, 2))
    getattr(store, kind)(Operation(Operator.eq, (variable, 1)))
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    problem, diagnostics = preprocessor.preprocess()
    assert not diagnostics.has_errors
    control = Control(lib, ["0"])
    control.parse_string("\n".join(f"{fact}." for fact in problem.asp_facts))
    for encoding in ("native.lp", "boolean.lp", "integer.lp", "complex.lp"):
        control.parse_string(
            files("constraint_handler").joinpath("encoding", encoding).read_text()
        )
    control.ground([("base", [])])
    models: list[set[str]] = []
    result = control.solve(
        on_model=lambda model: models.append(
            {str(atom) for atom in model.symbols(atoms=True)}
        )
    )
    assert result.satisfiable
    assert len(models) == expected_models
    assert all('value(variable("x"),integer(2))' not in model for model in models)
    assert sum('value(variable("x"),integer(1))' in model for model in models) == 1


@pytest.mark.parametrize(
    ("expression", "expected"),
    (
        (Operation(Operator.abs, (7,)), 7),
        (Operation(Operator.abs, (-7,)), 7),
        (Operation(Operator.abs, (0,)), 0),
        (Operation(Operator.abs, (VariableRef("left"),)), 7),
        (Operation(Operator.abs, (VariableRef("right"),)), 2),
        (Operation(Operator.abs, (-2.5,)), 2.5),
        (Operation(Operator.abs, (VariableRef("real"),)), 2.5),
        (Operation(Operator.add, (VariableRef("left"), VariableRef("right"))), 5),
    ),
)
def test_native_and_complex_scalar_expression(
    lib: Library, expression: Expr, expected: float
) -> None:
    """Evaluate scalar operations through native sums or Python rows."""
    store = ConstraintStore()
    store.define(VariableRef("left"), 7)
    store.define(VariableRef("right"), -2)
    store.define(VariableRef("real"), -2.5)
    store.define(VariableRef("result"), expression)
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    problem, diagnostics = preprocessor.preprocess()
    assert not diagnostics.has_errors
    assert set(problem.engines.values()) == (
        {Engine.native}
        if isinstance(expression, Operation) and expression.op == Operator.add
        else {Engine.native, Engine.complex}
    )
    control = Control(lib, ["0"])
    control.parse_string("\n".join(f"{fact}." for fact in problem.asp_facts))
    for encoding in ("native.lp", "integer.lp", "complex.lp"):
        control.parse_string(
            files("constraint_handler")
            .joinpath("encoding", encoding)
            .read_text(encoding="utf-8")
        )
    control.ground([("base", [])])
    variables = {
        parse_term(lib, f'variable("{name}")') for name in ("left", "right", "result")
    }
    models: list[set[str]] = []
    result = control.solve(
        on_model=lambda model: models.append(
            {
                str(atom)
                for atom in model.symbols(atoms=True)
                if atom.name == "value" and atom.arguments[0] in variables
            }
        )
    )
    assert result.satisfiable
    assert models == [
        {
            'value(variable("left"),integer(7))',
            'value(variable("right"),integer(-2))',
            (
                f'value(variable("result"),integer({expected}))'
                if isinstance(expected, int)
                else f'value(variable("result"),real("{expected}"))'
            ),
        }
    ]


def test_asp_facts_declarations(lib: Library) -> None:
    """Preserve declarations, IDs, labels, priorities, and typed expressions."""
    store = ConstraintStore()
    variable = VariableRef('x"\\\n')
    store.choose(variable, 1, label='input"\\\n')
    store.define(variable, Operation(Operator.add, (variable, 2)))
    store.default_to(variable, 0, priority=-2)
    store.check(True, label="check")
    store.ensure(False, label="ensure")
    engines = DispatchStore((expr_id, Engine.native) for expr_id in store.expressions)
    facts = asp_facts(lib, store, engines)
    control = Control(lib)
    control.parse_string("\n".join(f"{fact}." for fact in facts))
    control.ground([("base", [])])
    models: list[set[Symbol]] = []
    result = control.solve(
        on_model=lambda model: models.append(set(model.symbols(atoms=True)))
    )
    assert result.satisfiable
    assert models == [set(facts)]
    assert (
        Function(
            lib,
            "variable_choose",
            [
                String(lib, variable.name),
                Number(lib, 0),
                Number(lib, 1),
                String(lib, 'input"\\\n'),
            ],
        )
        in facts
    )
    default = next(fact for fact in facts if fact.name == "variable_default_to")
    assert default.arguments[:4] == [
        String(lib, variable.name),
        Number(lib, 4),
        Number(lib, 5),
        Number(lib, -2),
    ]
    assert (
        parse_term(lib, 'expr(2,operation(add,(variable("x\\"\\\\\\n"),integer(2))))')
        in facts
    )
    assert parse_term(lib, "expr(0,integer(1))") in facts
    assert parse_term(lib, "expr(1,boolean(true))") in facts
    assert parse_term(lib, 'check(6,"check")') in facts
    assert parse_term(lib, 'ensure(7,"ensure")') in facts


@pytest.mark.parametrize("operator", (Operator.int_div, Operator.real_div))
@pytest.mark.parametrize("values", ((0, 1), (0,), (1,)))
@pytest.mark.parametrize("exclude_zero", (False, True))
def test_complex_division_by_zero(
    lib: Library, operator: Operator, values: tuple[int, ...], exclude_zero: bool
) -> None:
    """Leave failed division and its dependents undefined without losing models."""
    store = ConstraintStore()
    divisor, quotient, downstream = (
        VariableRef(name) for name in ("divisor", "quotient", "downstream")
    )
    store.choose_from_iterator(divisor, values)
    store.ensure(Operation(Operator.geq, (divisor, 0)))
    store.define(quotient, Operation(operator, (6, divisor)))
    store.define(downstream, Operation(Operator.add, (quotient, 1)))
    if exclude_zero:
        store.ensure(Operation(Operator.neq, (divisor, 0)))
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    problem, diagnostics = preprocessor.preprocess()
    assert not diagnostics.has_errors
    control = Control(lib, ["0"])
    control.parse_string("\n".join(f"{fact}." for fact in problem.asp_facts))
    for encoding in ("native.lp", "integer.lp", "complex.lp"):
        control.parse_string(
            files("constraint_handler").joinpath("encoding", encoding).read_text()
        )
    control.ground([("base", [])])
    models: list[frozenset[str]] = []
    control.solve(
        on_model=lambda model: models.append(
            frozenset(
                str(atom)
                for atom in model.symbols(atoms=True)
                if atom.name == "value"
                and atom.arguments[0].type == SymbolType.Function
                and atom.arguments[0].name == "variable"
            )
        )
    )
    expected = set()
    if 0 in values and not exclude_zero:
        expected.add(frozenset({'value(variable("divisor"),integer(0))'}))
    if 1 in values:
        quotient_term, downstream_term = (
            ("integer(6)", "integer(7)")
            if operator == Operator.int_div
            else ('real("6.0")', 'real("7.0")')
        )
        expected.add(
            frozenset(
                {
                    'value(variable("divisor"),integer(1))',
                    f'value(variable("quotient"),{quotient_term})',
                    f'value(variable("downstream"),{downstream_term})',
                }
            )
        )
    assert len(models) == len(expected)
    assert set(models) == expected


@pytest.mark.parametrize(
    ("source", "invalid", "valid"),
    (
        ("lambda value: 6 // value", 0, 1),
        ("lambda value: int(value)", "bad", "6"),
        ("lambda value: (6,)[value]", 1, 0),
        ("lambda value: {1: 6}[value]", 0, 1),
        ("lambda value: value + 1", "bad", 5),
    ),
)
@pytest.mark.parametrize("all_invalid", (False, True))
def test_complex_python_partial_evaluation(
    source: str, invalid: Expr, valid: Expr, all_invalid: bool
) -> None:
    """Infer only successful Python results and allow fully undefined outputs."""
    store = ConstraintStore()
    argument, result, downstream = (
        VariableRef(name) for name in ("argument", "result", "downstream")
    )
    store.choose(argument, invalid)
    if not all_invalid:
        store.choose(argument, valid)
    store.define(result, Operation(Operator.python_eval, (Python(source), argument)))
    store.define(downstream, Operation(Operator.add, (result, 1)))
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    problem, diagnostics = preprocessor.preprocess()
    assert not diagnostics.has_errors
    assert problem.domains[result] == Domain(
        ints=frozenset() if all_invalid else frozenset({6})
    )
    assert problem.domains[downstream] == Domain(
        ints=frozenset() if all_invalid else frozenset({7})
    )
    assert sorted(
        str(fact.arguments[1]) for fact in problem.asp_facts if fact.name == "output"
    ) == ([] if all_invalid else ["integer(6)", "integer(7)"])
    assert problem.create_solver(SolveOptions()).solve().satisfiable


@pytest.mark.parametrize(
    ("source", "error", "message"),
    (
        ("lambda value: [value]", TypeError, "unsupported Python result type"),
        ("lambda value: float('inf')", ValueError, "finite values"),
        ("missing_callback", NameError, "missing_callback"),
        ("1", TypeError, "must evaluate to a callable"),
        (
            "lambda value: (_ for _ in ()).throw(RuntimeError('unexpected'))",
            RuntimeError,
            "unexpected",
        ),
    ),
)
def test_complex_unexpected_failures(
    source: str, error: type[Exception], message: str
) -> None:
    """Keep setup errors, invalid outputs, and unexpected exceptions visible."""
    store = ConstraintStore()
    store.define(
        VariableRef("result"),
        Operation(Operator.python_eval, (Python(source), 1)),
    )
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    problem, diagnostics = preprocessor.preprocess()
    assert not diagnostics.has_errors
    with pytest.raises(error, match=message):
        _ = problem.asp_facts


@pytest.mark.parametrize("with_engine", (False, True))
def test_complex_solution_rows(lib: Library, with_engine: bool) -> None:
    """Match every input and keep rows from separate expressions isolated."""
    store = ConstraintStore()
    first, second = VariableRef("a"), VariableRef("b")
    store.define(first, 42)
    store.choose_from_iterator(second, (1, 2))
    store.define(
        VariableRef("sum"),
        Operation(Operator.python_eval, (Python("lambda a, b: a + b"), first, second)),
    )
    store.define(VariableRef("negative"), Operation(Operator.minus, (second,)))
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    problem, diagnostics = preprocessor.preprocess()
    assert not diagnostics.has_errors
    facts = problem.asp_facts
    fact_text = {str(fact) for fact in facts}
    for row, second_value in enumerate((1, 2)):
        assert f'input({row},variable("a"),integer(42))' in fact_text
        assert f'input({row},variable("b"),integer({second_value}))' in fact_text
        assert f"output({row},integer({42 + second_value}))" in fact_text
    outputs = [fact for fact in facts if fact.name == "output"]
    assert len(outputs) == 2
    assert len({fact.arguments[0] for fact in outputs}) == 2
    control = Control(lib, ["0"])
    control.parse_string(
        "\n".join(
            f"{fact}."
            for fact in facts
            if with_engine
            or fact.name != "engine"
            or fact.arguments[0].name != "complex"
        )
    )
    for encoding in ("native.lp", "integer.lp", "complex.lp"):
        control.parse_string(
            files("constraint_handler").joinpath("encoding", encoding).read_text()
        )
    control.ground([("base", [])])
    variables = {
        parse_term(lib, f'variable("{name}")') for name in ("a", "b", "sum", "negative")
    }
    models: list[set[str]] = []
    result = control.solve(
        on_model=lambda model: models.append(
            {
                str(atom)
                for atom in model.symbols(atoms=True)
                if atom.name == "value" and atom.arguments[0] in variables
            }
        )
    )
    assert result.satisfiable
    assert {frozenset(model) for model in models} == {
        frozenset({'value(variable("a"),integer(42))'}),
        *(
            frozenset(
                {
                    'value(variable("a"),integer(42))',
                    f'value(variable("b"),integer({value}))',
                    f'value(variable("sum"),integer({42 + value}))',
                    f'value(variable("negative"),integer({-value}))',
                }
            )
            for value in (1, 2)
        ),
    }


@pytest.mark.parametrize(
    "expression, term",
    (
        (Operation(Operator.sqrt, (9,)), 'real("3.0")'),
        (Operation(Operator.real_div, (7, 2)), 'real("3.5")'),
        (Operation(Operator.int_div, (-3.5, 2)), "integer(-2)"),
        (Operation(Operator.concat, ("a", "b")), 'string("ab")'),
        (Operation(Operator.lt, (1.0, 2.0)), "boolean(true)"),
        (Operation(Operator.tuple_get, ((1, 2), 1)), "integer(2)"),
        (Operation(Operator.python_eval, (Python("lambda: 0"),)), "integer(0)"),
        (
            Operation(Operator.python_eval, (Python("lambda: (True, 1, 1.5)"),)),
            'tuple((boolean(true),integer(1),real("1.5")))',
        ),
    ),
)
def test_complex_operator_families(expression: Expr, term: str) -> None:
    """Support scalar operator families and calls with no free inputs."""
    store = ConstraintStore()
    store.define(VariableRef("result"), expression)
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    problem, diagnostics = preprocessor.preprocess()
    assert not diagnostics.has_errors
    assert f"output(0,{term})" in {str(fact) for fact in problem.asp_facts}
    assert problem.create_solver(SolveOptions()).solve().satisfiable


@pytest.mark.parametrize(
    "expression, expected",
    (
        (frozenset({1, 2}), frozenset({1, 2})),
        (frozenset(), frozenset()),
        (Operation(Operator.cardinality, (frozenset({1, 2}),)), 2),
        (Operation(Operator.set_make, (1, 2)), frozenset({1, 2})),
        (
            Operation(Operator.python_eval, (Python("lambda: frozenset({1, 2})"),)),
            frozenset({1, 2}),
        ),
        (
            Operation(Operator.python_eval, (Python("lambda: {1, 2}"),)),
            frozenset({1, 2}),
        ),
        (
            Operation(Operator.python_eval, (Python("lambda: frozenset()"),)),
            frozenset(),
        ),
    ),
)
def test_set_expression_outputs(
    lib: Library, expression: Expr, expected: int | frozenset[int]
) -> None:
    """Represent set results by a definedness marker and separate membership atoms."""
    store = ConstraintStore()
    store.define(VariableRef("result"), expression)
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    problem, diagnostics = preprocessor.preprocess()
    assert not diagnostics.has_errors
    control = Control(lib, ["0"])
    control.parse_string("\n".join(f"{fact}." for fact in problem.asp_facts))
    for encoding in (
        "native.lp",
        "integer.lp",
        "boolean.lp",
        "eq.lp",
        "set.lp",
        "complex.lp",
    ):
        control.parse_string(
            files("constraint_handler").joinpath("encoding", encoding).read_text()
        )
    control.ground([("base", [])])
    models: list[set[str]] = []
    outcome = control.solve(
        on_model=lambda model: models.append(
            {
                str(atom)
                for atom in model.symbols(atoms=True)
                if atom.name in {"value", "set_value"}
                and str(atom.arguments[0]) == 'variable("result")'
            }
        )
    )
    assert outcome.satisfiable
    assert models == [
        {
            'value(variable("result"),set)',
            *(f'set_value(variable("result"),integer({item}))' for item in expected),
        }
        if isinstance(expected, frozenset)
        else {f'value(variable("result"),integer({expected}))'}
    ]


def _variable_models(
    lib: Library, store: ConstraintStore
) -> list[dict[str, str | frozenset[str]]]:
    """Solve a store and retain typed scalar values or exact set memberships."""
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    problem, diagnostics = preprocessor.preprocess()
    assert not diagnostics.has_errors
    assert Engine.propagator not in problem.engines.values()
    control = Control(lib, ["0"])
    control.parse_string("\n".join(f"{fact}." for fact in problem.asp_facts))
    for encoding in (
        "native.lp",
        "integer.lp",
        "boolean.lp",
        "eq.lp",
        "set.lp",
        "complex.lp",
    ):
        control.parse_string(
            files("constraint_handler").joinpath("encoding", encoding).read_text()
        )
    control.ground([("base", [])])
    models: list[dict[str, str | frozenset[str]]] = []

    def collect(model: Model) -> None:
        """Keep empty sets distinct from variables with no value."""
        atoms = model.symbols(atoms=True)
        members: dict[Symbol, set[str]] = {}
        for atom in atoms:
            if atom.name == "set_value":
                members.setdefault(atom.arguments[0], set()).add(str(atom.arguments[1]))
        models.append(
            {
                subject.arguments[0].string: (
                    frozenset(members.get(subject, ()))
                    if str(value) == "set"
                    else str(value)
                )
                for atom in atoms
                if atom.name == "value"
                for subject, value in (atom.arguments,)
                if subject.type == SymbolType.Function and subject.name == "variable"
            }
        )

    outcome = control.solve(on_model=collect)
    assert outcome.exhausted
    return models


@pytest.mark.parametrize(
    "left, right, expected",
    (
        ("same", "same", True),
        ("left", "right", False),
        (True, True, True),
        (True, False, False),
        (True, 1, False),
        (False, 0.0, False),
        (None, None, True),
        (None, "None", False),
        (1, 1.0, True),
        (1.0, 1, True),
        (1, 1.5, False),
        (1.5, 1.5, True),
        (0, -0.0, True),
        (1e30, 1e30, True),
        ("1", 1, False),
        ((1, (2.0,)), (1.0, (2,)), True),
        ((True,), (1,), False),
        ((1,), (1, 2), False),
        (frozenset({1}), 1, False),
        (1, frozenset({1}), False),
        (frozenset(), frozenset(), True),
        (frozenset(), frozenset({1.0}), False),
        (frozenset({1}), frozenset({1.0}), True),
        (frozenset({1.0}), frozenset({1}), True),
        (frozenset({0}), frozenset({-0.0}), True),
        (frozenset({1, 2.5}), frozenset({1.0, 2.5}), True),
        (frozenset({1}), frozenset({1.5}), False),
        (frozenset({1, 2}), frozenset({1.0}), False),
        (frozenset({True}), frozenset({1}), False),
        (frozenset({False}), frozenset({0.0}), False),
        (frozenset({"1"}), frozenset({1}), False),
    ),
)
def test_native_equality(lib: Library, left: Expr, right: Expr, expected: bool) -> None:
    """Compare scalar and set values using typed keys and guarded absence."""
    store = ConstraintStore()
    first, second = VariableRef("left"), VariableRef("right")
    store.choose(first, left)
    store.choose(second, right)
    for operation in (Operator.eq, Operator.neq):
        store.define(
            VariableRef(operation.value), Operation(operation, (first, second))
        )
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    problem, diagnostics = preprocessor.preprocess()
    assert not diagnostics.has_errors
    assert set(problem.engines.values()) == {Engine.native}
    assert not any(fact.name == "solution" for fact in problem.asp_facts)
    assert problem.create_solver(SolveOptions()).solve().satisfiable
    models = _variable_models(lib, store)
    assert len(models) == 4
    for model in models:
        if "left" in model and "right" in model:
            assert model["eq"] == f"boolean({str(expected).lower()})"
            assert model["neq"] == f"boolean({str(not expected).lower()})"
        else:
            assert "eq" not in model and "neq" not in model


@pytest.mark.parametrize("numeric", (False, True))
@pytest.mark.parametrize("set_members", (False, True))
def test_native_equality_grounding_is_linear(
    lib: Library, numeric: bool, set_members: bool
) -> None:
    """Keep grounded rule counts and bodies linear as operand domains grow."""
    sizes: list[int] = []
    for size in (100, 200):
        store = ConstraintStore()
        left, right = VariableRef("left"), VariableRef("right")
        choose = (
            store.set_contain_choose_from_iterator
            if set_members
            else store.choose_from_iterator
        )
        choose(left, range(size) if numeric else (str(index) for index in range(size)))
        choose(
            right,
            (float(index) for index in range(size))
            if numeric
            else (str(index) for index in range(size)),
        )
        for operation in (Operator.eq, Operator.neq):
            store.define(
                VariableRef(operation.value), Operation(operation, (left, right))
            )
        preprocessor = Preprocessor(PreprocessOptions())
        preprocessor.add(store)
        problem, diagnostics = preprocessor.preprocess()
        assert not diagnostics.has_errors
        assert not any(fact.name == "solution" for fact in problem.asp_facts)
        control = Control(lib)
        control.parse_string("\n".join(f"{fact}." for fact in problem.asp_facts))
        for encoding in ("native.lp", "eq.lp", "set.lp"):
            control.parse_string(
                files("constraint_handler").joinpath("encoding", encoding).read_text()
            )
        control.ground([("base", [])])
        control.write_aspif(preprocess=False)
        sizes.append(sum(len(line.split()) for line in control.buffer.splitlines()))
    assert 0 < sizes[0] < sizes[1] <= 2 * sizes[0]


@pytest.mark.parametrize(
    "expression, reference",
    (
        (
            Operation(Operator.cardinality, (VariableRef("s"),)),
            lambda items: f"integer({len(items)})",
        ),
        (
            Operation(Operator.length, (VariableRef("s"),)),
            lambda items: f"integer({len(items)})",
        ),
        (
            Operation(Operator.union, (VariableRef("s"), frozenset({2, 3}))),
            lambda items: frozenset(f"integer({item})" for item in items | {2, 3}),
        ),
        (
            Operation(Operator.inter, (VariableRef("s"), frozenset({2, 3}))),
            lambda items: frozenset(f"integer({item})" for item in items & {2, 3}),
        ),
        (
            Operation(Operator.diff, (VariableRef("s"), frozenset({2, 3}))),
            lambda items: frozenset(f"integer({item})" for item in items - {2, 3}),
        ),
        (
            Operation(Operator.subset, (VariableRef("s"), frozenset({2, 3}))),
            lambda items: f"boolean({str(items <= {2, 3}).lower()})",
        ),
        (
            Operation(Operator.eq, (VariableRef("s"), frozenset({2}))),
            lambda items: f"boolean({str(items == {2}).lower()})",
        ),
        (
            Operation(Operator.neq, (VariableRef("s"), frozenset({2}))),
            lambda items: f"boolean({str(items != {2}).lower()})",
        ),
        (
            Operation(Operator.set_isin, (2, VariableRef("s"))),
            lambda items: f"boolean({str(2 in items).lower()})",
        ),
        (
            Operation(Operator.set_notin, (2, VariableRef("s"))),
            lambda items: f"boolean({str(2 not in items).lower()})",
        ),
    ),
)
def test_native_set_input_rows(
    lib: Library,
    expression: Expr,
    reference: Callable[[frozenset[int]], str | frozenset[str]],
) -> None:
    """Evaluate flat set operations natively over every subset without Python rows."""
    store = ConstraintStore()
    source, result = VariableRef("s"), VariableRef("result")
    store.set_contain_choose(source, 1)
    store.set_contain_choose(source, 2)
    store.define(result, expression)
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    problem, diagnostics = preprocessor.preprocess()
    assert not diagnostics.has_errors
    result_id = problem.store.variables[result].definitions[0].value
    assert problem.engines[result_id] == Engine.native
    assert not any(fact.name == "solution" for fact in problem.asp_facts)
    models = _variable_models(lib, store)
    assert len(models) == 4
    for model in models:
        members = model["s"]
        assert isinstance(members, frozenset)
        inputs = frozenset(
            parse_term(lib, member).arguments[0].number for member in members
        )
        assert model["result"] == reference(inputs)


@pytest.mark.parametrize(
    "operation, reference",
    (
        (Operator.union, operator.or_),
        (Operator.inter, operator.and_),
        (Operator.diff, operator.sub),
        (Operator.subset, operator.le),
        (Operator.eq, operator.eq),
        (Operator.neq, operator.ne),
    ),
)
def test_native_set_optional_operands(
    lib: Library,
    operation: Operator,
    reference: Callable[[frozenset[str], frozenset[str]], frozenset[str] | bool],
) -> None:
    """Require both optional sets and compare whole sets rather than chosen members."""
    store = ConstraintStore()
    left, right, result = (VariableRef(name) for name in ("left", "right", "result"))
    for variable, choices in (
        (left, (frozenset(), frozenset({1}), frozenset({1, 2}))),
        (right, (frozenset(), frozenset({2}), frozenset({1, 2}), frozenset({3}))),
    ):
        store.choose_from_iterator(variable, choices)
    store.define(result, Operation(operation, (left, right)))
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    problem, diagnostics = preprocessor.preprocess()
    assert not diagnostics.has_errors
    assert set(problem.engines.values()) == {Engine.native}
    assert not any(fact.name == "solution" for fact in problem.asp_facts)
    assert problem.create_solver(SolveOptions()).solve().satisfiable
    models = _variable_models(lib, store)
    assert len(models) == 20
    for model in models:
        if not {"left", "right"} <= model.keys():
            assert "result" not in model
            continue
        left_value, right_value = model["left"], model["right"]
        assert isinstance(left_value, frozenset)
        assert isinstance(right_value, frozenset)
        expected = reference(left_value, right_value)
        assert model["result"] == (
            f"boolean({str(expected).lower()})"
            if isinstance(expected, bool)
            else expected
        )


@pytest.mark.parametrize("arity", (0, 1, 2, 3))
def test_native_set_make(lib: Library, arity: int) -> None:
    """Construct sets with duplicate values only when all scalar inputs exist."""
    store = ConstraintStore()
    inputs = tuple(VariableRef(f"input{index}") for index in range(arity))
    for variable in inputs:
        store.choose_from_iterator(variable, (1, 2))
    result = VariableRef("result")
    store.define(result, Operation(Operator.set_make, inputs))
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    problem, diagnostics = preprocessor.preprocess()
    assert not diagnostics.has_errors
    assert set(problem.engines.values()) == {Engine.native}
    assert not any(fact.name == "solution" for fact in problem.asp_facts)
    models = _variable_models(lib, store)
    assert len(models) == 3**arity
    for model in models:
        if not all(variable.name in model for variable in inputs):
            assert "result" not in model
            continue
        assert model["result"] == frozenset(model[variable.name] for variable in inputs)


@pytest.mark.parametrize("operation", (Operator.set_isin, Operator.set_notin))
def test_native_set_typed_membership(lib: Library, operation: Operator) -> None:
    """Keep Boolean and integer elements distinct and require both operands."""
    store = ConstraintStore()
    member, source, result = (
        VariableRef(name) for name in ("member", "source", "result")
    )
    store.choose_from_iterator(member, (True, 1, None, "text"))
    store.choose_from_iterator(
        source, (frozenset(), frozenset({True}), frozenset({"text"}))
    )
    store.define(result, Operation(operation, (member, source)))
    models = _variable_models(lib, store)
    assert len(models) == 20
    for model in models:
        if not {"member", "source"} <= model.keys():
            assert "result" not in model
            continue
        members = model["source"]
        assert isinstance(members, frozenset)
        expected = (model["member"] in members) == (operation == Operator.set_isin)
        assert model["result"] == f"boolean({str(expected).lower()})"


@pytest.mark.parametrize(
    "operation",
    (
        Operator.union,
        Operator.inter,
        Operator.diff,
        Operator.subset,
        Operator.eq,
        Operator.neq,
        Operator.cardinality,
        Operator.length,
        Operator.set_make,
        Operator.set_isin,
        Operator.set_notin,
    ),
)
def test_nested_set_operations_remain_complex(operation: Operator) -> None:
    """Retain ordinary cost-based splitting instead of forcing native set roots."""
    store = ConstraintStore()
    source, result = VariableRef("source"), VariableRef("result")
    store.set_contain_choose_from_iterator(source, (1, 2))
    nested = Operation(Operator.union, (source, frozenset({3})))
    arguments: tuple[OperationArg, ...]
    if operation in {Operator.cardinality, Operator.length}:
        arguments = (nested,)
    elif operation == Operator.set_make:
        arguments = (Operation(Operator.cardinality, (source,)),)
    elif operation in {Operator.set_isin, Operator.set_notin}:
        arguments = (1, nested)
    else:
        arguments = (nested, source)
    store.define(result, Operation(operation, arguments))
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    problem, diagnostics = preprocessor.preprocess()
    assert not diagnostics.has_errors
    result_id = problem.store.variables[result].definitions[0].value
    assert problem.engines[result_id] == Engine.complex
    assert set(problem.store.variables) == {result}


def test_split_set_operations_become_native() -> None:
    """Use native member rules when normal splitting exposes flat set operations."""
    store = ConstraintStore()
    first, second, third = (VariableRef(name) for name in ("first", "second", "third"))
    for variable in (first, second, third):
        store.set_contain_choose_from_iterator(variable, range(20))
    result = VariableRef("result")
    store.define(
        result,
        Operation(Operator.union, (Operation(Operator.inter, (first, second)), third)),
    )
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    problem, diagnostics = preprocessor.preprocess()
    assert not diagnostics.has_errors
    assert len(set(problem.store.variables) - {result}) == 1
    assert set(problem.engines.values()) == {Engine.native}
    assert not any(fact.name == "solution" for fact in problem.asp_facts)
    assert problem.create_solver(SolveOptions()).solve().satisfiable


@pytest.mark.parametrize("kind", ("implicit", "explicit", "mixed", "empty"))
def test_complex_set_universe_shared_between_rows(
    lib: Library, monkeypatch: pytest.MonkeyPatch, kind: str
) -> None:
    """Share argument universes without changing scalar, empty, or set row facts."""
    store = ConstraintStore()
    source, offset = VariableRef("source"), VariableRef("offset")
    members = set() if kind == "empty" else {1, 2}
    values: list[int | frozenset[int]] = [frozenset(), frozenset(members)]
    if kind == "implicit":
        store.set_contain_choose_from_iterator(source, sorted(members))
        values = [frozenset(), frozenset({1}), frozenset({2}), frozenset(members)]
    else:
        if kind == "mixed":
            values.append(9)
        store.choose_from_iterator(source, values)
    store.choose_from_iterator(offset, (10, 20))
    store.define(
        VariableRef("result"),
        Operation(
            Operator.python_eval,
            (Python("lambda items, offset: offset"), source, offset),
        ),
    )
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    problem, diagnostics = preprocessor.preprocess()
    assert not diagnostics.has_errors
    original = Domain.potential_set_members
    calls: list[Domain] = []

    def counted_members(domain: Domain) -> frozenset[SetValue]:
        """Count universe construction during fact emission only."""
        calls.append(domain)
        return original(domain)

    monkeypatch.setattr(Domain, "potential_set_members", counted_members)
    facts = asp_facts(lib, problem.store, problem.engines, problem.domains)
    predicates = {
        "solution",
        "input",
        "output",
        "set_input_include",
        "set_input_exclude",
        "set_output",
    }
    actual = [str(fact) for fact in facts if fact.name in predicates]
    expected: list[str] = []
    expression_id = next(
        expr_id
        for expr_id, engine in problem.engines.items()
        if engine == Engine.complex
    )
    row = 0
    for value in sorted(
        set(values), key=lambda value: (type(value).__name__, repr(value))
    ):
        for offset_value in (10, 20):
            expected.append(f"solution({expression_id},{row})")
            input_value = "set" if isinstance(value, frozenset) else f"integer({value})"
            expected.append(f'input({row},variable("source"),{input_value})')
            if isinstance(value, frozenset):
                for predicate, elements in (
                    ("set_input_include", value),
                    ("set_input_exclude", members - value),
                ):
                    expected.extend(
                        f'{predicate}({row},variable("source"),integer({member}))'
                        for member in sorted(elements)
                    )
            expected.append(f'input({row},variable("offset"),integer({offset_value}))')
            expected.append(f"output({row},integer({offset_value}))")
            row += 1
    assert actual == expected
    assert calls == [problem.domains[source]]


def test_complex_mixed_set_and_scalar_inputs(lib: Library) -> None:
    """Feed set outputs into later calls and require optional scalar inputs."""
    store = ConstraintStore()
    source, offset, result = (VariableRef(name) for name in ("s", "offset", "result"))
    store.set_contain_choose(source, 1)
    store.set_contain_choose(source, 2)
    store.choose_from_iterator(offset, (10, 20))
    store.define(
        result,
        Operation(
            Operator.python_eval,
            (
                Python("lambda items, offset: {item + offset for item in items}"),
                source,
                offset,
            ),
        ),
    )
    store.define(VariableRef("alias"), result)
    store.define(VariableRef("size"), Operation(Operator.cardinality, (result,)))
    models = _variable_models(lib, store)
    assert len(models) == 12
    for model in models:
        if "offset" not in model:
            assert not {"result", "alias", "size"} & model.keys()
            continue
        members = model["s"]
        assert isinstance(members, frozenset)
        offset_value = parse_term(lib, str(model["offset"])).arguments[0].number
        expected = frozenset(
            f"integer({parse_term(lib, member).arguments[0].number + offset_value})"
            for member in members
        )
        assert model["result"] == model["alias"] == expected
        assert model["size"] == f"integer({len(members)})"


def test_native_empty_set_variable(lib: Library) -> None:
    """A declared set without entries exists as the empty set."""
    store = ConstraintStore()
    source = VariableRef("s")
    store.set_variables[source] = SetVariable()
    store.define(VariableRef("alias"), source)
    store.define(VariableRef("size"), Operation(Operator.cardinality, (source,)))
    assert _variable_models(lib, store) == [
        {"s": frozenset(), "alias": frozenset(), "size": "integer(0)"}
    ]


def test_native_set_choices(lib: Library) -> None:
    """Choose entire sets, keeping an absent value distinct from an empty set."""
    store = ConstraintStore()
    source = VariableRef("s")
    store.choose_from_iterator(source, (frozenset(), frozenset({1}), frozenset({1, 2})))
    store.define(VariableRef("size"), Operation(Operator.cardinality, (source,)))
    models = _variable_models(lib, store)
    assert len(models) == 4
    assert {frozenset(model.items()) for model in models} == {
        frozenset(),
        frozenset({("s", frozenset()), ("size", "integer(0)")}),
        frozenset({("s", frozenset({"integer(1)"})), ("size", "integer(1)")}),
        frozenset(
            {("s", frozenset({"integer(1)", "integer(2)"})), ("size", "integer(2)")}
        ),
    }


@pytest.mark.parametrize("same", (False, True))
def test_native_set_definitions_must_agree(lib: Library, same: bool) -> None:
    """Reject different set definitions instead of silently unioning their members."""
    store = ConstraintStore()
    source = VariableRef("s")
    store.define(source, frozenset({1}))
    store.define(source, frozenset({1}) if same else frozenset({1, 2}))
    models = _variable_models(lib, store)
    assert models == ([{"s": frozenset({"integer(1)"})}] if same else [])


@pytest.mark.parametrize("defined", (False, True))
def test_native_duplicate_set_choices(lib: Library, defined: bool) -> None:
    """Equivalent set candidates must not introduce extra source-selection models."""
    store = ConstraintStore()
    source = VariableRef("s")
    store.choose_from_iterator(source, (frozenset({1}), frozenset({1})))
    if defined:
        store.define(source, frozenset({1}))
    models = _variable_models(lib, store)
    assert len(models) == (1 if defined else 2)
    assert {frozenset(model.items()) for model in models} == {
        frozenset({("s", frozenset({"integer(1)"}))}),
        *(() if defined else (frozenset(),)),
    }


def test_native_set_membership_guards_and_types(lib: Library) -> None:
    """Guard set entries and preserve mixed scalar element types."""
    store = ConstraintStore()
    source, missing = VariableRef("s"), VariableRef("missing")
    store.choose(missing, True, condition=False)
    for member in (True, 2, None, "text", 2.5):
        store.set_contain(source, member)
    store.set_contain(source, 42, condition=False)
    store.set_contain(source, 43, condition=missing)
    store.set_contain_choose(source, 44, condition=False)
    store.set_contain_choose(source, 45, condition=missing)
    store.define(VariableRef("alias"), source)
    expected = frozenset(
        {"boolean(true)", "integer(2)", "none", 'string("text")', 'real("2.5")'}
    )
    assert _variable_models(lib, store) == [{"s": expected, "alias": expected}]


def test_complex_set_and_scalar_output_rows(lib: Library) -> None:
    """Distinguish empty sets, scalar outputs, and absent input rows in one call."""
    store = ConstraintStore()
    source = VariableRef("flag")
    store.choose_from_iterator(source, (False, True))
    store.define(
        VariableRef("result"),
        Operation(
            Operator.python_eval,
            (Python("lambda flag: frozenset() if flag else 7"), source),
        ),
    )
    models = _variable_models(lib, store)
    assert len(models) == 3
    assert {frozenset(model.items()) for model in models} == {
        frozenset(),
        frozenset({("flag", "boolean(true)"), ("result", frozenset())}),
        frozenset({("flag", "boolean(false)"), ("result", "integer(7)")}),
    }


def test_complex_rejects_unknown_inputs() -> None:
    """Do not silently omit operations that would need an unimplemented propagator."""
    store = ConstraintStore()
    unknown = VariableRef("unknown")
    store.define(
        unknown, Operation(Operator.python_eval, (Python("lambda: object()"),))
    )
    store.define(VariableRef("result"), Operation(Operator.abs, (unknown,)))
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    problem, diagnostics = preprocessor.preprocess()
    assert not diagnostics.has_errors
    assert Engine.propagator in problem.engines.values()
    with pytest.raises(NotImplementedError, match="unknown input domains"):
        problem.create_solver(SolveOptions())


@pytest.mark.parametrize(
    ("value", "term"),
    (
        (True, "boolean(true)"),
        (1, "integer(1)"),
        (1.0, 'real("1.0")'),
        (-0.0, 'real("-0.0")'),
        ("hello\nworld", 'string("hello\\nworld")'),
        (None, "none"),
        ((), "tuple(())"),
        ((1,), "tuple((integer(1),))"),
        ((1, True), "tuple((integer(1),boolean(true)))"),
        (((1,), frozenset({2})), "tuple((tuple((integer(1),)),set((integer(2),))))"),
        (frozenset[Expr](), "set(())"),
        (frozenset({1, 2}), "set((integer(1),integer(2)))"),
    ),
)
def test_asp_facts_values(lib: Library, value: Expr, term: str) -> None:
    """Round-trip supported scalar and collection values through Clingo's parser."""
    store = ConstraintStore()
    store.define(VariableRef("x"), value)
    facts = asp_facts(
        lib,
        store,
        DispatchStore((expr_id, Engine.native) for expr_id in store.expressions),
    )
    assert parse_term(lib, f"expr(0,{term})") in facts
    assert parse_term(lib, f"constant({term})") in facts
    assert parse_term(lib, "constant(boolean(true))") in facts
    for fact in facts:
        assert parse_term(lib, str(fact)) == fact


@pytest.mark.parametrize(
    "expr",
    (
        VariableRef("y"),
        (1, (VariableRef("y"),)),
        frozenset({1, VariableRef("y")}),
        Operation(Operator.add, (VariableRef("y"), 1)),
    ),
)
def test_asp_facts_nonconstant_values(lib: Library, expr: Expr) -> None:
    """Do not mark variable-dependent expressions or collections as constants."""
    store = ConstraintStore()
    store.define(VariableRef("x"), expr)
    facts = asp_facts(
        lib,
        store,
        DispatchStore((expr_id, Engine.native) for expr_id in store.expressions),
    )
    constants = [fact for fact in facts if fact.name == "constant"]
    assert parse_term(lib, "constant(boolean(true))") in constants
    assert all("variable" not in str(fact) for fact in constants)


def test_asp_facts_set_entries(lib: Library) -> None:
    """Retain set-variable candidates, assignments, and prioritized defaults."""
    store = ConstraintStore()
    variable = VariableRef("s")
    store.set_contain_choose(variable, 1, label="choice")
    store.set_contain(variable, 2, label="define")
    store.set_contain_default_to(variable, 3, priority=4, label="default")
    facts = asp_facts(
        lib,
        store,
        DispatchStore((expr_id, Engine.native) for expr_id in store.expressions),
    )
    assert parse_term(lib, 'set_contain_choose("s",0,1,"choice")') in facts
    assert parse_term(lib, 'set_contain("s",2,3,"define")') in facts
    assert parse_term(lib, 'set_contain_default_to("s",4,5,4,"default")') in facts


def test_asp_facts_requires_complete_dispatch(lib: Library) -> None:
    """Reject missing engine assignments rather than dropping expressions."""
    store = ConstraintStore()
    store.ensure(True)
    with pytest.raises(ValueError, match="classify exactly"):
        asp_facts(lib, store, DispatchStore())


@pytest.mark.parametrize("engine", (Engine.complex, Engine.propagator))
def test_asp_facts_other_engines(lib: Library, engine: Engine) -> None:
    """Retain non-native expressions and trusted source without executing it."""
    store = ConstraintStore()
    store.define(
        VariableRef("x"), Operation(Operator.python_eval, (Python("lambda: 1"),))
    )
    engines = DispatchStore((expr_id, engine) for expr_id in store.expressions)
    facts = asp_facts(lib, store, engines)
    assert parse_term(lib, f"engine({engine.value},0)") in facts
    assert (
        parse_term(lib, 'expr(0,operation(python_eval,(python("lambda: 1"),)))')
        in facts
    )


@pytest.mark.parametrize("value", (-(2**31) - 1, 2**31))
@pytest.mark.parametrize("as_priority", (False, True))
def test_asp_facts_rejects_integer_overflow(
    lib: Library, value: int, as_priority: bool
) -> None:
    """Reject overflowing literals and priorities instead of changing their value."""
    store = ConstraintStore()
    store.default_to(
        VariableRef("x"),
        0 if as_priority else value,
        priority=value if as_priority else 0,
    )
    engines = DispatchStore((expr_id, Engine.native) for expr_id in store.expressions)
    with pytest.raises(ValueError, match="signed 32-bit"):
        asp_facts(lib, store, engines)
