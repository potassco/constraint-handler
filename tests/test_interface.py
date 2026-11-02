from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from constraint_handler import (
    Context,
    PreparedProblem,
    PreprocessOptions,
    Preprocessor,
    Query,
    SolveOptions,
    Solver,
)
from constraint_handler.schemas.expression import Variable


@pytest.fixture(scope="module")
def prepared_problem():
    preprocessor = Preprocessor()
    preprocessor.add('variable_declare("x",fromFacts). variable_domain("x",val(int,1)).')
    preprocessor.add('variable_domain("x",val(int,2)).')
    prepared, diagnostics = PreparedProblem.from_preprocessor(preprocessor)
    assert diagnostics == prepared.diagnostics == ()
    return prepared


def test_preparation_snapshots_inputs():
    preprocessor = Preprocessor()
    preprocessor.add('variable_define("x",val(int,1)).')
    original, _ = PreparedProblem.from_preprocessor(preprocessor)
    repeated, _ = PreparedProblem.from_preprocessor(preprocessor)
    assert repeated == original

    preprocessor.add('variable_define("y",val(int,2)).')
    updated, _ = PreparedProblem.from_preprocessor(preprocessor)
    original_model = Solver(original).solve()
    updated_model = Solver(updated).solve()

    assert original_model.values == {"x": 1}
    assert updated_model.values == {
        "x": 1,
        "y": 2,
    }


def test_load_snapshots_file_contents(tmp_path):
    source = tmp_path / "problem.lp"
    source.write_text('variable_define("x",val(int,7)).', encoding="utf-8")
    preprocessor = Preprocessor()
    preprocessor.load(source)
    source.unlink()

    prepared, _ = PreparedProblem.from_preprocessor(preprocessor)

    assert Solver(prepared).solve().values == {"x": 7}


def test_prepared_problem_is_immutable(prepared_problem):
    assert isinstance(prepared_problem.declarations, tuple)
    assert all(isinstance(declaration, str) for declaration in prepared_problem.declarations)
    with pytest.raises(FrozenInstanceError):
        prepared_problem.declarations = ()


def test_enumeration_returns_detached_models(prepared_problem):
    solver = Solver(prepared_problem)
    models = list(solver.enumerate())

    assert {frozenset(model.values.items()) for model in models} == {
        frozenset({("x", 1)}),
        frozenset({("x", 2)}),
    }
    assert all(model.diagnostics == () for model in models)
    assert all(model.optimization_value == () for model in models)
    assert all(isinstance(model.optimality_proven, bool) for model in models)
    with pytest.raises(TypeError):
        models[0].values["x"] = 99
    assert len(list(solver.enumerate())) == 2
    assert {model.values["x"] for model in models} == {1, 2}


def test_solve_returns_one_model(prepared_problem):
    solver = Solver(prepared_problem)

    for _ in range(2):
        model = solver.solve()
        assert model is not None
        assert model.values["x"] in {1, 2}
        assert not hasattr(model, "optimality_proven")
        assert repr(model)


@pytest.mark.parametrize("model_limit, expected_count", [(None, 2), (1, 1), (2, 2)])
def test_model_limit(prepared_problem, model_limit, expected_count):
    solver = Solver(prepared_problem, SolveOptions(model_limit=model_limit))

    assert len(list(solver.enumerate())) == expected_count


@pytest.mark.parametrize("show_by_default", [True, False])
def test_visibility_is_session_local(prepared_problem, show_by_default):
    first = Solver(prepared_problem, SolveOptions(show_by_default=show_by_default))
    second = Solver(prepared_problem)

    assert bool(first.solve().values) is show_by_default
    first.hide(Variable("x"))
    assert all(model.values == {} for model in first.enumerate())
    first.show(Variable("x"))
    assert all("x" in model.values for model in first.enumerate())
    first.hide(Variable("x"))
    assert all("x" in model.values for model in second.enumerate())


def test_solver_unsat(prepared_problem):
    problem = replace(
        prepared_problem,
        declarations=prepared_problem.declarations + ("ch_core(ensure(val(bool,false)),_label_anonymous)",),
    )
    solver = Solver(problem)

    assert solver.solve() is None
    assert list(solver.enumerate()) == []


@pytest.mark.parametrize("program", ["ensure(val(bool,false)).", '{ variable_define("x",val(int,1)) }.'])
def test_preparation_rejects_unsat_or_ambiguous_input(program):
    preprocessor = Preprocessor()
    preprocessor.add(program)

    with pytest.raises(ValueError, match="exactly one uninterrupted model"):
        PreparedProblem.from_preprocessor(preprocessor)


def test_preprocessing_options_are_not_implemented():
    with pytest.raises(NotImplementedError):
        Preprocessor(PreprocessOptions())


@pytest.mark.parametrize(
    "target, method, arguments",
    [
        ("preprocessor", "add_context", ("context", Context())),
        ("prepared", "dump", (Path("unused.ch-prepared"),)),
        ("prepared", "load", (Path("unused.ch-prepared"),)),
        ("solver", "add_context", ("context", Context())),
        ("solver", "preset", ({},)),
        ("solver", "enforce_query", (Query(),)),
        ("solver", "union", ()),
        ("solver", "intersection", ()),
        ("solver", "supremum", ()),
        ("solver", "infimum", ()),
    ],
)
def test_unimplemented_methods_raise(prepared_problem, target, method, arguments):
    targets = {"preprocessor": Preprocessor(), "prepared": prepared_problem, "solver": Solver(prepared_problem)}

    with pytest.raises(NotImplementedError):
        getattr(targets[target], method)(*arguments)
