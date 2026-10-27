"""Test complete, deterministic engine classification of preprocessed stores."""

import pytest

from constraint_handler import (
    ConstraintStore,
    DispatchStore,
    Engine,
    PreprocessOptions,
    Preprocessor,
    Python,
    VariableRef,
    dispatch,
)
from constraint_handler.domains import UNKNOWN_DOMAIN, Domain, DomainStore
from constraint_handler.internal_input import (
    Expr,
    Lambda,
    Operation,
    ValueDef,
    ValueType,
)
from constraint_handler.python_input import Operator


def test_dispatch_partitions_roots_without_mutation() -> None:
    """Classify bare roots, collections, and opaque calls without result domains."""
    store = ConstraintStore()
    known, unknown = VariableRef("known"), VariableRef("unknown")
    literal = ValueDef(ValueType.integer, 1)
    collection = frozenset({literal})
    roots: tuple[Expr, ...] = (
        literal,
        unknown,
        collection,
        (literal,),
        Operation(Operator.eq, (known, literal)),
        Operation(Operator.set_isin, (known, collection)),
        Operation(Operator.python_eval, (Python("lambda value: value"), known)),
        Operation(Operator.python_eval, (Python("lambda: 1"),)),
        Operation(Operator.python_eval, (Python("lambda value: value"), unknown)),
        Operation(Operator.eq, (known, unknown)),
        Operation(Operator.linear_integer, ((literal, known), literal)),
    )
    for root in roots:
        store.add_expression(root)
    domains = DomainStore(
        {
            known: Domain(ints=frozenset({1})),
            unknown: UNKNOWN_DOMAIN,
            collection: Domain(explicit_sets=frozenset({frozenset({1})})),
        }
    )
    before, metadata = store.copy(), dict(domains)
    engines = dispatch(store, domains)
    assert isinstance(engines, DispatchStore)
    assert list(engines) == list(store.expressions)
    assert list(engines.values()) == [Engine.native] * 6 + [Engine.complex] * 2 + [
        Engine.propagator
    ] * 2 + [Engine.native]
    assert store == before and dict(domains) == metadata
    assert list(dispatch(store, domains).items()) == list(engines.items())
    assert dispatch(ConstraintStore(), DomainStore()) == {}


def test_dispatch_requires_all_input_metadata() -> None:
    """Raise on a missing domain even after encountering an unknown input."""
    store = ConstraintStore()
    unknown, missing = VariableRef("unknown"), VariableRef("missing")
    store.add_expression(
        Operation(Operator.python_eval, (Python("lambda *values: 1"), unknown, missing))
    )
    with pytest.raises(KeyError):
        dispatch(store, DomainStore({unknown: UNKNOWN_DOMAIN}))


@pytest.mark.parametrize("operator", (Operator.conj, Operator.disj))
def test_dispatch_native_boolean_unknown_input(operator: Operator) -> None:
    """Keep Boolean short-circuiting native even with unknown operand domains."""
    store = ConstraintStore()
    unknown = VariableRef("unknown")
    expr_id = store.add_expression(
        Operation(operator, (unknown, ValueDef(ValueType.boolean, True)))
    )
    assert (
        dispatch(store, DomainStore({unknown: UNKNOWN_DOMAIN}))[expr_id]
        == Engine.native
    )


@pytest.mark.parametrize(
    "root",
    [
        Operation(Operator.lambda_, (Lambda((), ValueDef(ValueType.integer, 1)),)),
        Operation(Operator.add, (Operation(Operator.abs, (VariableRef("x"),)),)),
        (Operation(Operator.abs, (VariableRef("x"),)),),
        Operation(
            Operator.python_eval,
            (
                Python("lambda value: value"),
                (Operation(Operator.abs, (VariableRef("x"),)),),
            ),
        ),
    ],
)
def test_dispatch_rejects_unconverted_expressions(root: Expr) -> None:
    """Fail explicitly rather than assigning an invalid preprocessing shape."""
    store = ConstraintStore()
    store.add_expression(root)
    with pytest.raises(TypeError):
        dispatch(store, DomainStore())


def test_preprocessed_store_can_be_dispatched() -> None:
    """Dispatch all IDs produced by preprocessing, including compiled calls."""
    from constraint_handler.python_input import Lambda as InputLambda
    from constraint_handler.python_input import Operation as InputOperation

    store = ConstraintStore()
    variable, parameter = VariableRef("x"), VariableRef("u")
    store.choose_from_iterator(variable, (1, 2))
    store.define(
        VariableRef("result"),
        InputOperation(
            Operator.lambda_, (InputLambda((parameter,), parameter), variable)
        ),
    )
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    prepared, diagnostics = preprocessor.preprocess()
    assert not diagnostics.has_errors
    engines = dispatch(prepared.store, prepared.domains)
    result_id = prepared.store.variables[VariableRef("result")].definitions[0].value
    assert engines[result_id] == Engine.complex
    assert engines.keys() == prepared.store.expressions.keys()
