"""Tests for the Preprocessor, PreparedProblem, and Solver workflow interface."""

from importlib.resources import files
from itertools import combinations, product
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import ANY, Mock

import pytest
from clingo.control import Control
from clingo.core import Library
from clingo.solve import Model

from constraint_handler import (
    ConstraintStore,
    Engine,
    FailIntegrityExn,
    Operation,
    Operator,
    PreparedProblem,
    PreprocessOptions,
    Preprocessor,
    Python,
    SolveOptions,
    VariableRef,
    asp_facts,
)
from constraint_handler.domains import Domain
from constraint_handler.internal_input import Operation as InternalOperation
from constraint_handler.internal_input import ValueType
from constraint_handler.python_input import Expr
from constraint_handler.static_types import SetOf


def test_minimize_solver_reports_optimal_models_and_cost() -> None:
    """Hide improving incumbents and expose the guarded objective's optimal cost."""
    store = ConstraintStore()
    variable = VariableRef("objective")
    store.choose_from_iterator(variable, (-3, 2, 8))
    store.ensure(Operation(Operator.has_value, (variable,)))
    store.minimize(
        Operation(Operator.add, (Operation(Operator.mult, (-2, variable)), 5))
    )
    processor = Preprocessor(PreprocessOptions())
    processor.add(store)
    problem, diagnostics = processor.preprocess()
    assert not diagnostics.has_errors
    solver = problem.create_solver(SolveOptions(arguments=("0",)))
    assert solver.cost is None
    assert not solver.optimality_proven
    models: list[tuple[int, ...]] = []
    assert solver.solve(
        on_model=lambda model: models.append(tuple(model.cost))
    ).satisfiable
    assert models == [(-11,)]
    assert solver.cost == (-11,)
    assert solver.optimality_proven


@pytest.mark.parametrize(
    "coefficients, offset", (((1, 1), 0), ((-2, 3), 5), ((3, -2), -7))
)
def test_minimize_matches_exhaustive_optional_reference(
    coefficients: tuple[int, int],
    offset: int,
) -> None:
    """Compare all optima with exhaustive arithmetic including absent inputs and guards."""
    store = ConstraintStore()
    left, right, guard = (VariableRef(name) for name in ("left", "right", "guard"))
    store.choose_from_iterator(left, (-3, 1, 7))
    store.choose_from_iterator(right, (-2, 4))
    store.choose_from_iterator(guard, (False, True))
    store.minimize(
        Operation(
            Operator.add,
            (
                Operation(Operator.mult, (coefficients[0], left)),
                Operation(Operator.mult, (coefficients[1], right)),
                offset,
            ),
        ),
        guard,
    )
    processor = Preprocessor(PreprocessOptions())
    processor.add(store)
    problem, diagnostics = processor.preprocess()
    assert not diagnostics.has_errors
    actual: set[tuple[int | bool | None, ...]] = set()

    def receive(model: Model) -> None:
        """Read public optional variable values from each proven optimum."""
        assert model.optimality_proven
        values: dict[str, int | bool] = {}
        for atom in model.symbols(atoms=True):
            if atom.name != "value" or not str(atom.arguments[0]).startswith(
                "variable("
            ):
                continue
            name = atom.arguments[0].arguments[0].string
            payload = atom.arguments[1]
            values[name] = (
                payload.arguments[0].number
                if payload.name == "integer"
                else payload.arguments[0].name == "true"
            )
        actual.add(tuple(values.get(name) for name in ("left", "right", "guard")))

    candidates = {
        (left_value, right_value, condition): (
            coefficients[0] * left_value + coefficients[1] * right_value + offset
            if left_value is not None and right_value is not None and condition is True
            else 0
        )
        for left_value, right_value, condition in product(
            (None, -3, 1, 7), (None, -2, 4), (None, False, True)
        )
    }
    minimum = min(candidates.values())
    solver = problem.create_solver(SolveOptions(arguments=("0",)))
    assert solver.solve(on_model=receive).exhausted
    assert actual == {values for values, cost in candidates.items() if cost == minimum}
    assert solver.cost == (minimum,)
    assert solver.optimality_proven


@pytest.mark.parametrize("condition", (True, False, VariableRef("guard")))
@pytest.mark.parametrize("expr", (5, Operation(Operator.minus, (5,))))
def test_minimize_guarded_constants(expr: Expr, condition: Expr) -> None:
    """Include a constant base only under a defined true condition."""
    store = ConstraintStore()
    store.choose(VariableRef("guard"), True, False)
    store.minimize(expr, condition)
    processor = Preprocessor(PreprocessOptions())
    processor.add(store)
    problem, diagnostics = processor.preprocess()
    assert not diagnostics.has_errors
    solver = problem.create_solver(SolveOptions(arguments=("0",)))
    assert solver.solve().satisfiable
    expected = (5 if expr == 5 else -5) if condition is True else 0
    assert solver.cost == (expected,)
    assert solver.optimality_proven


@pytest.mark.parametrize("cancelled", (False, True))
def test_minimize_retains_undefined_zero_dependencies(cancelled: bool) -> None:
    """Do not turn an undefined zero-valued term into a defined constant penalty."""
    store = ConstraintStore()
    variable = VariableRef("optional")
    store.choose(variable, 2)
    zero = (
        Operation(Operator.sub, (variable, variable))
        if cancelled
        else Operation(Operator.mult, (0, variable))
    )
    store.minimize(Operation(Operator.add, (zero, 5)))
    processor = Preprocessor(PreprocessOptions())
    processor.add(store)
    problem, diagnostics = processor.preprocess()
    assert not diagnostics.has_errors
    solver = problem.create_solver(SolveOptions(arguments=("0",)))
    models: list[set[str]] = []
    solver.solve(
        on_model=lambda model: models.append(
            {str(atom) for atom in model.symbols(atoms=True)}
        )
    )
    assert solver.cost == (0,)
    assert len(models) == 1
    assert 'value(variable("optional"),integer(2))' not in models[0]


def test_minimize_duplicate_statements_and_priorities() -> None:
    """Sum duplicate statements and optimize higher priorities first, including negatives."""
    store = ConstraintStore()
    variable = VariableRef("x")
    store.choose_from_iterator(variable, (-2, 3))
    store.ensure(Operation(Operator.has_value, (variable,)))
    store.minimize(variable, priority=-1)
    store.minimize(variable, priority=-1)
    store.minimize(Operation(Operator.minus, (variable,)), priority=4)
    processor = Preprocessor(PreprocessOptions())
    processor.add(store)
    problem, diagnostics = processor.preprocess()
    assert not diagnostics.has_errors
    solver = problem.create_solver(SolveOptions(arguments=("0", "--opt-mode=ignore")))
    assert solver.solve().satisfiable
    assert solver.cost == (-3, 6)
    assert solver.optimality_proven


def test_minimize_undefined_sum_excludes_remaining_terms_and_base() -> None:
    """Drop the entire sum, including its negative defined term and positive offset."""
    store = ConstraintStore()
    optional, defined = VariableRef("optional"), VariableRef("defined")
    store.choose(optional, 10)
    store.define(defined, -4)
    store.minimize(
        Operation(Operator.add, (optional, defined, 3)),
        Operation(Operator.eq, (defined, -4)),
    )
    processor = Preprocessor(PreprocessOptions())
    processor.add(store)
    problem, diagnostics = processor.preprocess()
    assert not diagnostics.has_errors
    solver = problem.create_solver(SolveOptions(arguments=("0",)))
    models: list[set[str]] = []
    solver.solve(
        on_model=lambda model: models.append(
            {str(atom) for atom in model.symbols(atoms=True)}
        )
    )
    assert solver.cost == (0,)
    assert len(models) == 1
    assert 'value(variable("optional"),integer(10))' not in models[0]


def test_minimize_unsatisfiable_and_repeated_solves() -> None:
    """Reset metadata each solve and never report an optimum for an unsatisfiable problem."""
    store = ConstraintStore()
    store.minimize(5)
    store.ensure(False)
    processor = Preprocessor(PreprocessOptions())
    processor.add(store)
    problem, diagnostics = processor.preprocess()
    assert not diagnostics.has_errors
    solver = problem.create_solver(SolveOptions())
    for _ in range(2):
        assert solver.solve().unsatisfiable
        assert solver.cost is None
        assert not solver.optimality_proven


@pytest.mark.parametrize("unknown", (False, True))
def test_minimize_rejects_non_native_or_unknown_objectives(unknown: bool) -> None:
    """Diagnose unsupported objective engines and unknown domains before fact generation."""
    store = ConstraintStore()
    variable = VariableRef("x")
    store.choose_from_iterator(variable, (1, 2))
    store.minimize(
        Operation(Operator.python_eval, (Python("lambda: float('inf')"),))
        if unknown
        else Operation(Operator.mult, (variable, variable))
    )
    processor = Preprocessor(PreprocessOptions())
    processor.add(store)
    problem, diagnostics = processor.preprocess()
    assert diagnostics.has_errors
    assert any("Optimization requires" in item.message for item in diagnostics.items)
    with pytest.raises(ValueError, match="optimization"):
        problem.create_solver(SolveOptions())


@pytest.mark.parametrize("continue_on_errors", (False, True))
def test_continue_on_errors_preserves_native_nullable_subset(
    continue_on_errors: bool,
) -> None:
    """Continue normal splitting and dispatch without suppressing nullable errors."""
    store = ConstraintStore()
    source, result = VariableRef("source"), VariableRef("result")
    members = ("o3", "without_devices", "other1", "other2")
    store.choose_from_iterator(
        source,
        (
            None,
            *(
                frozenset(selection)
                for size in range(len(members) + 1)
                for selection in combinations(members, size)
            ),
        ),
    )
    store.define(
        result,
        Operation(
            Operator.subset,
            (source, Operation(Operator.set_make, ("o3", "without_devices"))),
        ),
    )
    processor = Preprocessor(PreprocessOptions(continue_on_errors=continue_on_errors))
    processor.add(store)
    prepared, diagnostics = processor.preprocess()
    assert diagnostics.has_errors
    assert any(
        item.message == "subset requires 2 set arguments" for item in diagnostics.items
    )
    if not continue_on_errors:
        assert not prepared.engines
        with pytest.raises(ValueError, match="preprocessing errors"):
            prepared.create_solver(SolveOptions())
        return
    result_id = prepared.store.variables[result].definitions[0].value
    expression = prepared.store.expressions[result_id]
    assert (
        isinstance(expression, InternalOperation) and expression.op == Operator.subset
    )
    assert len(prepared.store.variables) == 3
    assert prepared.engines[result_id] == Engine.native
    assert prepared.engines.keys() == prepared.store.expressions.keys()
    assert not any(fact.name == "solution" for fact in prepared.asp_facts)
    assert prepared.create_solver(SolveOptions()).solve().satisfiable


def test_continue_on_errors_propagates_pipeline_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Do not swallow a processing exception when error continuation is enabled."""
    monkeypatch.setattr(
        "constraint_handler.preprocessor.split",
        Mock(side_effect=RuntimeError("cannot split")),
    )
    store = ConstraintStore()
    store.define(VariableRef("result"), 1)
    processor = Preprocessor(PreprocessOptions(continue_on_errors=True))
    processor.add(store)
    with pytest.raises(RuntimeError, match="cannot split"):
        processor.preprocess()


@pytest.mark.parametrize("payload", (None, False, 0, "", frozenset[int]()))
def test_native_has_value_solver_loads_encoding(payload: Expr) -> None:
    """Load none.lp through the public solver and enforce the expected Boolean."""
    store = ConstraintStore()
    source, result = VariableRef("source"), VariableRef("result")
    store.define(source, payload)
    store.define(result, Operation(Operator.has_value, (source,)))
    store.ensure(Operation(Operator.eq, (result, payload is not None)))
    processor = Preprocessor(PreprocessOptions())
    processor.add(store)
    problem, diagnostics = processor.preprocess()
    assert not diagnostics.has_errors
    result_id = problem.store.variables[result].definitions[0].value
    assert problem.engines[result_id] == Engine.native
    assert problem.create_solver(SolveOptions()).solve().satisfiable


@pytest.mark.parametrize("python_reference", (False, True))
@pytest.mark.parametrize(
    "payload",
    (7, 1.5, "text", True, None, (1, "text"), frozenset[int](), frozenset({1, 2})),
)
def test_native_if_optional_operands(payload: Expr, python_reference: bool) -> None:
    """Match Python tables for defined scalars/sets and absent optional operands."""
    store = ConstraintStore()
    condition, argument, result = (
        VariableRef(name) for name in ("condition", "argument", "result")
    )
    store.choose_from_iterator(condition, (False, True))
    store.choose(argument, payload)
    store.define(
        result,
        Operation(
            Operator.python_eval,
            (
                Python(
                    "lambda condition, argument: argument if condition is True else None"
                ),
                condition,
                argument,
            ),
        )
        if python_reference
        else Operation(Operator.if_, (condition, argument)),
    )
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    prepared, diagnostics = preprocessor.preprocess()
    assert not diagnostics.has_errors
    result_id = prepared.store.variables[result].definitions[0].value
    assert prepared.engines[result_id] == (
        Engine.complex if python_reference else Engine.native
    )
    if not python_reference:
        assert not any(
            fact.name in {"solution", "input", "output"} for fact in prepared.asp_facts
        )
    control = Control(Library(), ["0"])
    control.parse_string("\n".join(f"{fact}." for fact in prepared.asp_facts))
    for encoding in ("native.lp", "boolean.lp", "tuples.lp", "none.lp", "complex.lp"):
        control.parse_string(
            files("constraint_handler").joinpath("encoding", encoding).read_text()
        )
    control.ground([("base", [])])
    models: list[set[str]] = []
    assert control.solve(
        on_model=lambda model: models.append(
            {str(atom) for atom in model.symbols(atoms=True)}
        )
    ).satisfiable
    assert len(models) == 6
    for model in models:
        argument_values = {
            atom.replace('variable("argument")', 'variable("result")')
            for atom in model
            if atom.startswith(
                ('value(variable("argument"),', 'set_value(variable("argument"),')
            )
        }
        actual = {
            atom
            for atom in model
            if atom.startswith(
                ('value(variable("result"),', 'set_value(variable("result"),')
            )
        }
        if not argument_values or not any(
            atom.startswith('value(variable("condition"),') for atom in model
        ):
            assert not actual
        elif 'value(variable("condition"),boolean(true))' in model:
            assert actual == argument_values
        else:
            assert actual == {'value(variable("result"),none)'}


@pytest.mark.parametrize("condition", (None, 0, "true"))
def test_native_if_rejects_nonboolean_condition(condition: Expr) -> None:
    """Preserve Boolean-only validation despite the broader Python template."""
    store = ConstraintStore()
    store.define(VariableRef("condition"), condition)
    store.define(
        VariableRef("result"),
        Operation(Operator.if_, (VariableRef("condition"), 7)),
    )
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    _, diagnostics = preprocessor.preprocess()
    assert diagnostics.has_errors


@pytest.mark.parametrize("nested", (False, True))
def test_native_if_retains_cost_based_splitting(nested: bool) -> None:
    """Keep inexpensive nesting complex without forcing native auxiliary inputs."""
    store = ConstraintStore()
    condition, argument, result = (
        VariableRef(name) for name in ("condition", "argument", "result")
    )
    store.choose_from_iterator(condition, (False, True))
    store.choose_from_iterator(argument, (-2, -1))
    store.define(
        result,
        Operation(
            Operator.if_,
            (condition, Operation(Operator.abs, (argument,)) if nested else argument),
        ),
    )
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    prepared, diagnostics = preprocessor.preprocess()
    assert not diagnostics.has_errors
    assert set(prepared.store.variables) == {condition, argument, result}
    result_id = prepared.store.variables[result].definitions[0].value
    assert prepared.engines[result_id] == (Engine.complex if nested else Engine.native)
    assert prepared.create_solver(SolveOptions()).solve().satisfiable


def test_native_if_set_grounding_is_linear() -> None:
    """Copy optional set members without enumerating the set's solution space."""
    sizes: list[int] = []
    for size in (100, 200):
        store = ConstraintStore()
        condition, argument = VariableRef("condition"), VariableRef("argument")
        store.choose_from_iterator(condition, (False, True))
        store.set_contain_choose_from_iterator(argument, range(size))
        store.define(
            VariableRef("result"), Operation(Operator.if_, (condition, argument))
        )
        preprocessor = Preprocessor(PreprocessOptions())
        preprocessor.add(store)
        prepared, diagnostics = preprocessor.preprocess()
        assert not diagnostics.has_errors
        assert set(prepared.engines.values()) == {Engine.native}
        assert not any(fact.name == "solution" for fact in prepared.asp_facts)
        control = Control(Library())
        control.parse_string("\n".join(f"{fact}." for fact in prepared.asp_facts))
        for encoding in ("native.lp", "boolean.lp"):
            control.parse_string(
                files("constraint_handler").joinpath("encoding", encoding).read_text()
            )
        control.ground([("base", [])])
        control.write_aspif(preprocess=False)
        sizes.append(sum(len(line.split()) for line in control.buffer.splitlines()))
    assert 0 < sizes[0] < sizes[1] <= 2 * sizes[0]


@pytest.mark.parametrize("empty_operand", ("condition", "argument"))
def test_native_if_empty_choices_are_rejected(empty_operand: str) -> None:
    """Preserve rejection of variables with no defining choices."""
    store = ConstraintStore()
    condition, argument = VariableRef("condition"), VariableRef("argument")
    store.choose_from_iterator(
        condition, () if empty_operand == "condition" else (False,)
    )
    store.choose_from_iterator(argument, () if empty_operand == "argument" else (7,))
    store.define(VariableRef("result"), Operation(Operator.if_, (condition, argument)))
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    _, diagnostics = preprocessor.preprocess()
    assert diagnostics.has_errors


def test_native_if_undeclared_argument_is_rejected() -> None:
    """Keep rejecting undeclared operands even under a false condition."""
    store = ConstraintStore()
    store.define(
        VariableRef("result"), Operation(Operator.if_, (False, VariableRef("missing")))
    )
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    _, diagnostics = preprocessor.preprocess()
    assert diagnostics.has_errors


@pytest.mark.parametrize(
    "source",
    (
        "absolute",
        "lambda value: absolute(value)",
        "external.absolute",
        "lambda value: sum(absolute(item) for item in (value,))",
        "lambda value: external.absolute(value) + int(math.sqrt(0))",
    ),
)
def test_python_context(source: str) -> None:
    """Use external functions during domain inference, fact generation, and solving."""
    store = ConstraintStore()
    result = VariableRef("result")
    store.define(result, Operation(Operator.python_eval, (Python(source), -6)))
    store.ensure(Operation(Operator.eq, (result, 6)))
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    preprocessor.add_context("absolute", abs)
    preprocessor.add_context("external", SimpleNamespace(absolute=abs))

    prepared, diagnostics = preprocessor.preprocess()
    assert not diagnostics.items
    assert prepared.domains[result] == Domain(ints=frozenset({6}))
    assert any(
        fact.name == "value"
        and fact.arguments[0].name == "__complex_output"
        and str(fact).endswith(",integer(6))")
        for fact in prepared.asp_facts
    )
    assert prepared.create_solver(SolveOptions()).solve().satisfiable


@pytest.mark.parametrize("all_invalid", (False, True))
def test_python_context_integrity_failure(all_invalid: bool) -> None:
    """Skip deliberate Python failures without rejecting otherwise valid models."""

    def guarded(value: int) -> int:
        """Return a value only for the nonzero candidate."""
        if value == 0:
            raise FailIntegrityExn
        return 6

    store = ConstraintStore()
    argument, result, downstream = (
        VariableRef(name) for name in ("argument", "result", "downstream")
    )
    store.choose_from_iterator(argument, (0,) if all_invalid else (0, 1))
    store.ensure(Operation(Operator.eq, (argument, 0)))
    store.define(result, Operation(Operator.python_eval, (Python("guarded"), argument)))
    store.define(downstream, Operation(Operator.add, (result, 1)))
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add_context("guarded", guarded)
    preprocessor.add(store)
    prepared, diagnostics = preprocessor.preprocess()
    assert not diagnostics.items
    assert prepared.domains[result] == Domain(
        ints=frozenset() if all_invalid else frozenset({6})
    )
    assert prepared.domains[downstream] == Domain(
        ints=frozenset() if all_invalid else frozenset({7})
    )
    assert not any(
        fact.name == "input" and str(fact.arguments[2]) == "integer(0)"
        for fact in prepared.asp_facts
    )
    assert prepared.create_solver(SolveOptions()).solve().satisfiable


def test_failure_name_is_ordinary_core_variable() -> None:
    """Keep the scratch converter's reserved failure name ordinary in the core API."""
    store = ConstraintStore()
    store.define(VariableRef("__fail"), True)
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    prepared, diagnostics = preprocessor.preprocess()
    assert not diagnostics.items
    assert prepared.create_solver(SolveOptions()).solve().satisfiable


def test_python_context_snapshot() -> None:
    """Keep prepared bindings isolated from later additions and replacements."""
    store = ConstraintStore()
    result = VariableRef("result")
    store.define(result, Operation(Operator.python_eval, (Python("convert"), -6)))
    store.ensure(Operation(Operator.eq, (result, 6)))
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    preprocessor.add_context("convert", abs)
    prepared, diagnostics = preprocessor.preprocess()
    assert not diagnostics.items
    original_facts = tuple(map(str, prepared.asp_facts))

    preprocessor.add_context("convert", int)
    preprocessor.add_context("another", str)
    updated, diagnostics = preprocessor.preprocess()
    assert not diagnostics.items
    assert updated.domains[result] == Domain(ints=frozenset({-6}))
    assert "another" not in prepared.python_context
    assert tuple(map(str, prepared.asp_facts)) == original_facts
    assert prepared.create_solver(SolveOptions()).solve().satisfiable
    assert prepared.create_solver(SolveOptions()).solve().satisfiable
    assert updated.create_solver(SolveOptions()).solve().unsatisfiable


@pytest.mark.parametrize(
    ("op", "value"),
    (
        (Operator.conj, True),
        (Operator.disj, False),
        (Operator.lxor, False),
        (Operator.leqv, True),
    ),
)
def test_preprocess_nullary_boolean_operators(op: Operator, value: bool) -> None:
    """Accept nullary Boolean identities through all preprocessing passes."""
    store = ConstraintStore()
    result = VariableRef("result")
    store.define(result, Operation(op, ()))
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    prepared, diagnostics = preprocessor.preprocess()
    assert not diagnostics.items
    assert prepared.static_types[result] == frozenset({ValueType.boolean})
    assert prepared.domains[result] == Domain(bools=frozenset({value}))


@pytest.mark.parametrize(
    ("left", "right", "quotient"),
    ((3.5, 2, 1), (-3.5, 2, -2), (7, -2.0, -4), (7, 2, 3)),
)
def test_preprocess_integer_division(left: float, right: float, quotient: int) -> None:
    """Keep division results integer-valued when used by integer-only operators."""
    store = ConstraintStore()
    divided, result = VariableRef("divided"), VariableRef("result")
    store.define(divided, Operation(Operator.int_div, (left, right)))
    store.define(result, Operation(Operator.linear_integer, ((2, divided), 1)))
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    prepared, diagnostics = preprocessor.preprocess()
    assert not diagnostics.items
    assert prepared.static_types[divided] == frozenset({ValueType.integer})
    assert prepared.static_types[result] == frozenset({ValueType.integer})
    assert prepared.domains[divided] == Domain(ints=frozenset({quotient}))
    assert prepared.domains[result] == Domain(ints=frozenset({2 * quotient + 1}))


@pytest.mark.parametrize("term_count", (1, 3))
def test_preprocess_rejects_linear_integer_without_offset(term_count: int) -> None:
    """Reject a missing constant offset before splitting can rewrite the last term."""
    store = ConstraintStore()
    variables = tuple(VariableRef(f"x{index}") for index in range(term_count))
    for variable in variables:
        store.choose_from_iterator(variable, range(10))
    store.define(
        VariableRef("result"),
        Operation(
            Operator.linear_integer,
            tuple((1, Operation(Operator.abs, (variable,))) for variable in variables),
        ),
    )
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    prepared, diagnostics = preprocessor.preprocess()
    assert diagnostics.has_errors
    assert any(
        error.message
        == "linear_integer constant offset must be a constant integer literal"
        for error in diagnostics.errors
    )
    assert prepared.store == store


def test_preprocessor_workflow() -> None:
    """Verify Preprocessor.add, snapshot isolation, and prepared metadata."""
    x = VariableRef("x")
    y = VariableRef("y")
    s = VariableRef("s")

    store1 = ConstraintStore()
    store1.choose_from_iterator(x, (1, 2))
    store1.default_to(x, 3)

    store2 = ConstraintStore()
    store2.define(y, Operation(Operator.add, (x, 10)))
    store2.set_contain_choose(s, x)
    store2.set_contain(s, 5)
    store2.set_contain_default_to(s, 6)
    store2.ensure(Operation(Operator.lt, (x, y)))

    options = PreprocessOptions(
        arguments=("--opt",), threshold=100, boolean_threshold=10
    )
    preprocessor = Preprocessor(options)
    assert preprocessor.options == options

    preprocessor.add(store1)
    preprocessor.add(store2)

    # Mutating original stores after add must not affect preprocessor
    store1.choose(x, 999)

    prepared, diagnostics = preprocessor.preprocess()
    assert not diagnostics.has_errors
    assert not diagnostics.warnings

    assert prepared.static_types[x] == frozenset({ValueType.integer})
    assert prepared.static_types[y] == frozenset({ValueType.integer})
    assert prepared.static_types[s] == frozenset(
        {SetOf(frozenset({ValueType.integer}), False)}
    )

    assert prepared.domains[x] == Domain(ints=frozenset({1, 2, 3}))
    assert prepared.domains[y] == Domain(ints=frozenset({11, 12, 13}))
    assert prepared.domains[s] == Domain(
        implicit_set_elements=frozenset({1, 2, 3, 5, 6})
    )

    # Adding more to preprocessor after preprocess must not mutate prepared.store
    extra = ConstraintStore()
    extra.define(VariableRef("z"), 42)
    preprocessor.add(extra)
    assert VariableRef("z") not in prepared.store.variables


@pytest.mark.parametrize(
    ("values", "lengths", "implicit"),
    (
        (("", "abc"), frozenset({0, 3}), False),
        (((), (1, True)), frozenset({0, 2}), False),
        ((frozenset[int](), frozenset({1, 2})), frozenset({0, 2}), False),
        (("abc", (1, True), frozenset({1})), frozenset({1, 2, 3}), False),
        ((1, 2), frozenset({0, 1, 2}), True),
    ),
)
def test_preprocess_collection_length(
    values: tuple[Expr, ...], lengths: frozenset[int], implicit: bool
) -> None:
    """Preserve length overload metadata through normalization and splitting."""
    store = ConstraintStore()
    source, length, result, offset = (
        VariableRef(name) for name in ("source", "length", "result", "offset")
    )
    if implicit:
        store.set_contain_choose_from_iterator(source, values)
    else:
        store.choose_from_iterator(source, values)
    store.choose_from_iterator(offset, range(20))
    store.define(length, Operation(Operator.length, (source,)))
    store.define(
        result,
        Operation(Operator.add, (Operation(Operator.length, (source,)), offset)),
    )
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    prepared, diagnostics = preprocessor.preprocess()
    assert not diagnostics.items
    assert prepared.domains[length] == Domain(ints=lengths)
    assert prepared.static_types[length] == frozenset({ValueType.integer})
    assert prepared.domains[result] == Domain(
        ints=frozenset(size + value for size in lengths for value in range(20))
    )
    assert set(prepared.store.expressions.values()) <= (
        prepared.domains.keys() & prepared.static_types.keys()
    )


@pytest.mark.parametrize("value", (True, 1, 1.5, None))
def test_preprocess_length_rejects_scalars(value: Expr) -> None:
    """Keep non-collection length inputs invalid during preprocessing."""
    store = ConstraintStore()
    store.define(VariableRef("result"), Operation(Operator.length, (value,)))
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    _prepared, diagnostics = preprocessor.preprocess()
    assert diagnostics.has_errors
    assert any("length requires" in item.message for item in diagnostics.errors)


def test_preprocess_collects_diagnostics_once_for_shared_order() -> None:
    """Verify undefined variables and cycles are reported once via shared EvaluationOrder."""
    store = ConstraintStore()
    undef = VariableRef("undef")
    a = VariableRef("a")
    b = VariableRef("b")
    store.define(a, b)
    store.define(b, a)
    store.ensure(Operation(Operator.add, (undef, 1)))

    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    _, diagnostics = preprocessor.preprocess()

    assert diagnostics.has_errors
    undef_errors = [d for d in diagnostics.errors if d.variable == undef]
    assert len(undef_errors) == 1
    assert (
        len(
            [
                error
                for error in diagnostics.errors
                if "dependency cycle" in error.message
            ]
        )
        == 2
    )


def test_prepared_problem_and_solver_skeleton_methods() -> None:
    """Verify PreparedProblem and Solver session creation and unimplemented stubs."""
    preprocessor = Preprocessor(PreprocessOptions())
    prepared, _ = preprocessor.preprocess()

    solve_opts = SolveOptions(arguments=("0",))
    solver = prepared.create_solver(solve_opts)
    assert solver.problem is prepared
    assert solver.options == solve_opts

    with pytest.raises(NotImplementedError):
        prepared.dump(Path("problem.ch-prepared"))
    with pytest.raises(NotImplementedError):
        PreparedProblem.load(Path("problem.ch-prepared"))
    with pytest.raises(NotImplementedError):
        solver.add_context("ctx", object())
    with pytest.raises(NotImplementedError):
        solver.preset({VariableRef("x"): 1})
    with pytest.raises(NotImplementedError):
        solver.enforce_query(True)
    assert solver.solve().satisfiable


def test_native_solver_fact_base(monkeypatch: pytest.MonkeyPatch) -> None:
    """Build facts on demand and enforce an unsatisfiable constant ensure."""
    build_facts = Mock(wraps=asp_facts)
    monkeypatch.setattr("constraint_handler.preprocessor.asp_facts", build_facts)
    store = ConstraintStore()
    store.choose_from_iterator(VariableRef("x"), (1, 2), label="input")
    store.ensure(False, label="must be true")
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    prepared, diagnostics = preprocessor.preprocess()
    build_facts.assert_not_called()
    assert not diagnostics.has_errors
    assert prepared.engines.keys() == prepared.store.expressions.keys()
    assert set(prepared.engines.values()) == {Engine.native}
    assert tuple(map(str, prepared.asp_facts)) == tuple(
        map(
            str,
            asp_facts(Library(), prepared.store, prepared.engines, prepared.domains),
        )
    )
    build_facts.assert_called_once_with(
        ANY, prepared.store, prepared.engines, prepared.domains, prepared.python_context
    )
    first = prepared.create_solver(SolveOptions())
    second = prepared.create_solver(SolveOptions(arguments=("0",)))
    assert build_facts.call_count == 3
    assert (
        build_facts.call_args_list[1].args[0]
        is not build_facts.call_args_list[2].args[0]
    )
    assert first.solve().unsatisfiable
    assert second.solve().unsatisfiable
    assert first.solve().unsatisfiable
    assert build_facts.call_count == 3


def test_solver_rejects_preprocessing_errors() -> None:
    """Do not solve a fact base omitted because preprocessing failed."""
    store = ConstraintStore()
    store.ensure(VariableRef("undefined"))
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    prepared, diagnostics = preprocessor.preprocess()
    assert diagnostics.has_errors
    assert not prepared.engines
    with pytest.raises(ValueError, match="preprocessing errors"):
        prepared.create_solver(SolveOptions())
