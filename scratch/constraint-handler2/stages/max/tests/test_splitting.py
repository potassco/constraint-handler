"""Behavioral tests for cost-guided splitting and Python conversion."""

import math
from collections.abc import Callable
from typing import cast

import pytest

from constraint_handler import (
    ConstraintStore,
    Expr,
    Lambda,
    Operation,
    Operator,
    PreprocessOptions,
    Preprocessor,
    Python,
    VariableRef,
)
from constraint_handler.diagnostics import Diagnostics
from constraint_handler.domains import (
    UNKNOWN_DOMAIN,
    Domain,
    DomainStore,
    compute_domains,
)
from constraint_handler.internal_input import Lambda as InternalLambda
from constraint_handler.internal_input import Operation as InternalOperation
from constraint_handler.internal_input import ValueDef, ValueType
from constraint_handler.python_conversion import convert
from constraint_handler.splitting import DEFAULT_SUBSET_LIMIT, GroundingCost, split
from constraint_handler.static_types import (
    SetOf,
    StaticTypeStore,
    UnknownType,
    compute_static_types,
)
from constraint_handler.util import compute_evaluation_order


def _callback(call: object) -> Callable[..., object]:
    """Load a generated callable using the supported Python evaluation context."""
    assert isinstance(call, InternalOperation) and call.op == Operator.python_eval
    descriptor = call.args[0]
    assert isinstance(descriptor, Python)
    return cast(Callable[..., object], eval(descriptor.fn, {"math": math}))


def test_cryptarithm_equality_remains_flat_linear_comparison() -> None:
    """Avoid extracting a numeric sum solely to compare send + more with money."""
    store = ConstraintStore()
    send, more, money = (VariableRef(name) for name in ("send", "more", "money"))
    for variable, bounds in (
        (send, (1000, 1003)),
        (more, (1000, 1003)),
        (money, (2000, 2005)),
    ):
        store.choose_from_iterator(variable, range(*bounds))
    store.ensure(Operation(Operator.eq, (Operation(Operator.add, (send, more)), money)))
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    problem, diagnostics = preprocessor.preprocess()
    assert not diagnostics.has_errors
    root_id = problem.store.constraints[0].expr
    root = problem.store.expressions[root_id]
    assert isinstance(root, InternalOperation)
    assert root.op == Operator.linear_comparison
    assert root.args == (
        ValueDef(ValueType.string, "eq"),
        (ValueDef(ValueType.integer, 1), send),
        (ValueDef(ValueType.integer, 1), more),
        (ValueDef(ValueType.integer, -1), money),
        ValueDef(ValueType.integer, 0),
    )
    assert set(problem.store.variables) == {send, more, money}
    assert GroundingCost(problem.domains, problem.static_types).complexity(root) == 1
    assert not any(
        fact.name in {"solution", "linear_integer_base"} for fact in problem.asp_facts
    )


@pytest.mark.parametrize(
    "expr, expected",
    [
        (Operation(Operator.linear_integer, ((2, 3), (-1, 4), 5)), 7),
        (Operation(Operator.linear_comparison, ("eq", (2, 3), (-1, 4), -2)), True),
        (Operation(Operator.linear_comparison, ("neq", (2, 3), (-1, 4), -2)), False),
        (Operation(Operator.linear_comparison, ("lt", (2, 3), -7)), True),
        (Operation(Operator.linear_comparison, ("leq", (2, 3), -6)), True),
        (Operation(Operator.linear_comparison, ("gt", (2, 3), -5)), True),
        (Operation(Operator.linear_comparison, ("geq", (2, 3), -6)), True),
        (Operation(Operator.add, ()), 0),
        (Operation(Operator.mult, (2, 3, 4)), 24),
        (Operation(Operator.max, (2, 3)), 3),
        (Operation(Operator.min, (2, 3)), 2),
        (Operation(Operator.conj, (True, False)), False),
        (Operation(Operator.disj, (True, False)), True),
        (Operation(Operator.leqv, (False, False, True)), True),
        (Operation(Operator.lxor, (True, True, True)), True),
        (Operation(Operator.sqrt, (9,)), 3),
        (Operation(Operator.floor, (1.5,)), 1),
        (Operation(Operator.set_make, (1, 2)), frozenset({1, 2})),
        (
            Operation(
                Operator.set_fold,
                (
                    Lambda(
                        (VariableRef("acc"), VariableRef("item")),
                        Operation(
                            Operator.add, (VariableRef("acc"), VariableRef("item"))
                        ),
                    ),
                    frozenset({1, 2}),
                    3,
                ),
            ),
            6,
        ),
        (Operation(Operator.get_or_else, (None, 4)), 4),
        (Operation(Operator.get_or_else, (3, 4)), 3),
        (Operation(Operator.if_, (False, 4)), None),
        (Operation(Operator.ite, (True, 3, 4)), 3),
        (Operation(Operator.tuple_get, ((1, 2), 1)), 2),
        (Operation(Operator.python_eval, (Python("lambda: math.sqrt(9)"),)), 3),
    ],
)
def test_python_conversion_executes_operator_families(
    expr: Expr, expected: object
) -> None:
    """Execute generated source for collections, folds, arithmetic, and logic."""
    store = ConstraintStore()
    store.define(VariableRef("result"), expr)
    body = store.expressions[
        store.variables[VariableRef("result")].definitions[0].value
    ]
    descriptor = convert((), body)
    callback = cast(Callable[[], object], eval(descriptor.fn, {"math": math}))
    assert callback() == expected


def test_python_conversion_evaluates_fallback_input_once() -> None:
    """Avoid duplicating execution of an opaque Python input in a fallback."""
    store = ConstraintStore()
    store.define(
        VariableRef("result"),
        Operation(
            Operator.get_or_else,
            (
                Operation(
                    Operator.python_eval,
                    (Python("lambda values: values.pop()"), VariableRef("x")),
                ),
                0,
            ),
        ),
    )
    body = store.expressions[
        store.variables[VariableRef("result")].definitions[0].value
    ]
    descriptor = convert((VariableRef("x"),), body)
    callback = cast(Callable[..., object], eval(descriptor.fn, {"math": math}))
    values = [1, 2]
    assert callback(values) == 2
    assert values == [1]


def test_python_descriptor_does_not_capture_generated_bindings() -> None:
    """Keep Python descriptor globals separate from generated callable parameters."""
    store = ConstraintStore()
    store.define(
        VariableRef("result"),
        Operation(
            Operator.add,
            (
                VariableRef("x"),
                Operation(
                    Operator.python_eval,
                    (Python("lambda: globals().get('_value0', 7)"),),
                ),
            ),
        ),
    )
    body = store.expressions[
        store.variables[VariableRef("result")].definitions[0].value
    ]
    descriptor = convert((VariableRef("x"),), body)
    callback = cast(Callable[..., object], eval(descriptor.fn, {"math": math}))
    assert callback(3) == 10


def test_split_lowers_python_fold_callbacks() -> None:
    """Keep opaque fold descriptors out of the flat native-operation output."""
    store = ConstraintStore()
    store.define(
        VariableRef("result"),
        Operation(
            Operator.set_fold,
            (Python("lambda acc, item: acc + item"), frozenset({1, 2}), 3),
        ),
    )
    domains, types = _metadata(store)
    _split(store, domains, types)
    definition = store.variables[VariableRef("result")].definitions[0]
    call = store.expressions[definition.value]
    assert _callback(call)() == 6
    before = store.copy()
    _split(store, domains, types)
    assert store == before


def _metadata(store: ConstraintStore) -> tuple[DomainStore, StaticTypeStore]:
    """Compute metadata without applying normalization or splitting."""
    diagnostics = Diagnostics()
    order = compute_evaluation_order(store, diagnostics)
    types = compute_static_types(store, order, diagnostics)
    domains = compute_domains(store, order, diagnostics)
    assert not diagnostics.has_errors
    return domains, types


@pytest.mark.parametrize("profitable", [False, True])
def test_splitting_does_not_recompute_metadata(
    monkeypatch: pytest.MonkeyPatch, profitable: bool
) -> None:
    """Preserve caller metadata without rerunning metadata or dependency analysis."""
    store = ConstraintStore()
    variable = VariableRef("x")
    store.choose_from_iterator(variable, (1, 2))
    second, third, parameter = (VariableRef(name) for name in ("y", "z", "u"))
    store.choose_from_iterator(second, (1, 2))
    store.choose_from_iterator(third, range(10))
    store.define(
        VariableRef("scoped"),
        Operation(Operator.lambda_, (Lambda((parameter,), parameter), variable)),
    )
    store.define(
        VariableRef("result"),
        (
            Operation(
                Operator.add, (Operation(Operator.add, (variable, second)), third)
            )
            if profitable
            else Operation(Operator.add, (Operation(Operator.abs, (variable,)), 1))
        ),
    )
    domains, types = _metadata(store)

    def unexpected_computation(*args: object, **kwargs: object) -> None:
        """Reject whole-store metadata recomputation during splitting."""
        pytest.fail("splitting must only transfer metadata")

    monkeypatch.setattr(
        "constraint_handler.domains.computer._DomainComputer.run",
        unexpected_computation,
    )
    monkeypatch.setattr(
        "constraint_handler.static_types._StaticTypeComputer.run",
        unexpected_computation,
    )
    diagnostics = Diagnostics()
    order = compute_evaluation_order(store, diagnostics)
    diagnostics.warn("existing warning")
    original_diagnostics = tuple(diagnostics.items)
    original_domains = dict(domains)
    original_types = dict(types)
    original_scoped_domains = dict(domains.scoped_expressions)
    original_scoped_types = dict(types.scoped_expressions)
    assert original_scoped_domains and original_scoped_types
    monkeypatch.setattr(
        "constraint_handler.util.compute_evaluation_order", unexpected_computation
    )
    split(store, domains, types, order, diagnostics)
    assert not diagnostics.has_errors
    assert tuple(diagnostics.items) == original_diagnostics
    assert all(domains[expr] is value for expr, value in original_domains.items())
    assert all(types[expr] is value for expr, value in original_types.items())
    assert original_scoped_domains.items() <= domains.scoped_expressions.items()
    assert original_scoped_types.items() <= types.scoped_expressions.items()


def test_lambda_metadata_scopes_do_not_combine_independent_calls() -> None:
    """Transfer shared constants once per lambda without combining sibling scopes."""
    store = ConstraintStore()
    variable = VariableRef("x")
    store.choose_from_iterator(variable, (0, 1))
    for index in range(12):
        store.define(
            VariableRef(f"result_{index}"),
            Operation(Operator.sub, (Operation(Operator.abs, (variable,)), 0)),
        )
    parameter = VariableRef("u")
    store.define(
        VariableRef("scoped"),
        Operation(Operator.lambda_, (Lambda((parameter,), 0), "text")),
    )
    domains, types = _metadata(store)
    original_domains = set(domains.scoped_expressions)
    original_types = set(types.scoped_expressions)
    _split(store, domains, types)
    zero = ValueDef(ValueType.integer, 0)
    for metadata, original in ((domains, original_domains), (types, original_types)):
        scopes = [
            scope
            for expr, scope in metadata.scoped_expressions.keys() - original
            if expr == zero
        ]
        assert len(scopes) == 12
        assert all(len(scope) == 1 for scope in scopes)
        assert all(parameter not in dict(scope) for scope in scopes)


def test_split_preserves_input_with_existing_errors() -> None:
    """Leave an invalid store untouched when the caller has already reported errors."""
    store = ConstraintStore()
    store.define(VariableRef("result"), VariableRef("undefined"))
    diagnostics = Diagnostics()
    order = compute_evaluation_order(store, diagnostics)
    before = store.copy()
    domains, types = DomainStore(), StaticTypeStore()
    split(store, domains, types, order, diagnostics)
    assert store == before
    assert not domains and not types


def _split(
    store: ConstraintStore,
    domains: DomainStore,
    types: StaticTypeStore,
    *,
    subset_limit: int = DEFAULT_SUBSET_LIMIT,
) -> None:
    """Supply caller-owned pass context and check diagnostics after splitting."""
    diagnostics = Diagnostics()
    order = compute_evaluation_order(store, diagnostics)
    split(store, domains, types, order, diagnostics, subset_limit=subset_limit)
    assert not diagnostics.has_errors


@pytest.mark.parametrize("case, count", [(0, 1), (1, 2), (2, 2), (3, 1), (4, 0)])
def test_documented_subset_decisions(case: int, count: int) -> None:
    """Match all five examples, including shared variables and proper subsets."""
    store = ConstraintStore()
    first, second, third, fourth = (VariableRef(name) for name in "abcd")
    variables = (first, second, third, fourth)
    for index, variable in enumerate(variables):
        store.choose_from_iterator(
            variable, range(2 if case == 3 and index < 2 else 10)
        )
    inner = Operation(Operator.add, (first, second))
    examples = (
        Operation(Operator.add, (inner, third)),
        Operation(Operator.sub, (inner, Operation(Operator.add, (third, fourth)))),
        Operation(
            Operator.add,
            (
                Operation(Operator.abs, (first,)),
                Operation(Operator.abs, (second,)),
                third,
            ),
        ),
        Operation(Operator.sub, (inner, Operation(Operator.abs, (third,)))),
        Operation(Operator.sub, (inner, inner)),
    )
    result = VariableRef("result")
    store.define(result, examples[case], label="source")
    domains, types = _metadata(store)
    original_ids = set(store.expressions)
    original_domain = domains[result]
    _split(store, domains, types)
    auxiliaries = set(store.variables) - {*variables, result}
    assert len(auxiliaries) == count
    assert domains[result] == original_domain
    assert set(store.expressions.values()) <= domains.keys() & types.keys()
    for auxiliary in auxiliaries:
        definition = store.variables[auxiliary].definitions[0]
        assert definition.value not in original_ids
        assert domains[auxiliary] == domains[store.expressions[definition.value]]
        assert types[auxiliary] == types[store.expressions[definition.value]]
    diagnostics = Diagnostics()
    assert not compute_evaluation_order(store, diagnostics).cyclic_exprs
    assert not diagnostics.has_errors
    if case == 3:
        definition = store.variables[next(iter(auxiliaries))].definitions[0]
        call = store.expressions[definition.value]
        assert isinstance(call, InternalOperation)
        assert call.args[1:] == (first, second)
        assert _callback(call)(2, 3) == 5
    if case == 4:
        definition = store.variables[result].definitions[0]
        call = store.expressions[definition.value]
        assert isinstance(call, InternalOperation) and call.op == Operator.python_eval
        assert call.args[1:] == (first, second)
        assert _callback(call)(3, 7) == 0
    before = store.copy()
    _split(store, domains, types)
    assert store == before


def test_metadata_stores_share_root_nested_and_variable_keys() -> None:
    """Use one mutable entry for structurally equal root and nested expressions."""
    store = ConstraintStore()
    variable = VariableRef("x")
    store.choose_from_iterator(variable, (1, 2))
    inner = Operation(Operator.minus, (variable,))
    store.define(VariableRef("nested"), Operation(Operator.abs, (inner,)))
    store.define(VariableRef("root"), inner)
    store.define(VariableRef("alias"), variable)
    domains, types = _metadata(store)
    root_id = store.variables[VariableRef("root")].definitions[0].value
    root = store.expressions[root_id]
    nested = InternalOperation(Operator.minus, (variable,))
    assert root == nested
    assert domains[root] == Domain(ints=frozenset({-1, -2}))
    assert types[root] == frozenset({ValueType.integer})
    assert root_id not in domains and root_id not in types
    domains[root] = Domain(ints=frozenset({-3}))
    types[root] = frozenset({ValueType.none})
    assert domains.lookup(nested) == domains.get(root) == Domain(ints=frozenset({-3}))
    assert types.lookup(nested) == types.get(root) == frozenset({ValueType.none})
    alias_id = store.variables[VariableRef("alias")].definitions[0].value
    assert store.expressions[alias_id] == variable
    assert domains[store.expressions[alias_id]] == domains[variable]
    assert types[store.expressions[alias_id]] == types[variable]
    assert domains[variable] == Domain(ints=frozenset({1, 2}))
    assert types[variable] == frozenset({ValueType.integer})


def test_expression_store_lookups_and_lambda_scopes() -> None:
    """Keep nested metadata available without mixing bound and free variables."""
    store = ConstraintStore()
    variable = VariableRef("x")
    store.choose_from_iterator(variable, (1, 2))
    store.define(
        VariableRef("nested"),
        Operation(Operator.abs, (Operation(Operator.minus, (variable,)),)),
    )
    store.define(
        VariableRef("scoped"),
        Operation(Operator.lambda_, (Lambda((variable,), variable), "text")),
    )
    domains, types = _metadata(store)
    nested = InternalOperation(Operator.minus, (variable,))
    assert domains[nested] == Domain(ints=frozenset({-1, -2}))
    assert types[nested] == frozenset({ValueType.integer})
    assert domains[variable] == Domain(ints=frozenset({1, 2}))
    assert types[variable] == frozenset({ValueType.integer})
    text_domain = Domain(strings=frozenset({"text"}))
    text_type = frozenset({ValueType.string})
    assert (
        domains.lookup(variable, scope=frozenset({(variable, text_domain)}))
        == text_domain
    )
    assert types.lookup(variable, scope=frozenset({(variable, text_type)})) == text_type
    root = store.variables[VariableRef("nested")].definitions[0].value
    expression = store.expressions[root]
    assert domains[expression] == Domain(ints=frozenset({1, 2}))
    assert types[expression] == frozenset({ValueType.integer})
    missing = VariableRef("missing")
    with pytest.raises(KeyError):
        domains[missing]
    with pytest.raises(KeyError):
        types[missing]
    domains[missing] = text_domain
    types[missing] = text_type
    assert domains.lookup(missing) == text_domain
    assert types.lookup(missing) == text_type


def test_preprocessor_splits_normalized_linear_terms() -> None:
    """Split nonlinear terms and retain the native sum with valid metadata."""
    store = ConstraintStore()
    variables = tuple(VariableRef(name) for name in "abc")
    for variable in variables:
        store.choose_from_iterator(variable, range(10))
    result = VariableRef("result")
    store.define(
        result,
        Operation(
            Operator.linear_integer,
            (*[(1, Operation(Operator.abs, (variable,))) for variable in variables], 1),
        ),
    )
    preprocessor = Preprocessor(PreprocessOptions())
    preprocessor.add(store)
    prepared, diagnostics = preprocessor.preprocess()
    assert not diagnostics.has_errors
    assert len(prepared.store.variables) == 7
    definition = prepared.store.variables[result].definitions[0]
    expression = prepared.store.expressions[definition.value]
    assert isinstance(expression, InternalOperation)
    assert expression.op == Operator.linear_integer
    assert expression.args[-1] == ValueDef(ValueType.integer, 1)
    for pair, variable in zip(expression.args[:-1], variables, strict=True):
        assert isinstance(pair, tuple)
        coefficient, auxiliary = pair
        assert coefficient == ValueDef(ValueType.integer, 1)
        assert isinstance(auxiliary, VariableRef)
        original = (pair[0], InternalOperation(Operator.abs, (variable,)))
        assert prepared.domains[original].cardinality() == 10
        assert prepared.domains[pair] == prepared.domains[original]
        assert prepared.static_types[pair] == prepared.static_types[original]
    domains, types = _metadata(prepared.store)
    assert domains[result] == prepared.domains[result]
    assert isinstance(types[result], UnknownType)
    assert prepared.static_types[result] == frozenset({ValueType.integer})


def test_implicit_set_membership_cost_and_metadata() -> None:
    """Use member counts rather than enumerating powersets, retaining set kinds."""
    store = ConstraintStore()
    first, second, third = (VariableRef(name) for name in "abc")
    for variable in (first, second, third):
        store.set_contain_choose_from_iterator(variable, range(20))
    result = VariableRef("result")
    store.define(
        result,
        Operation(Operator.union, (Operation(Operator.inter, (first, second)), third)),
    )
    domains, types = _metadata(store)
    _split(store, domains, types)
    (auxiliary,) = set(store.variables) - {result}
    assert domains[auxiliary].implicit_set_elements == frozenset(range(20))
    assert domains[auxiliary].cardinality() == 2**20
    assert types[auxiliary] == frozenset({SetOf(frozenset({ValueType.integer}), True)})


def test_unknown_and_empty_domains_do_not_force_splits() -> None:
    """Treat unknown costs as infinity and products containing zero as zero."""
    for empty in (False, True):
        store = ConstraintStore()
        first, second = VariableRef("a"), VariableRef("b")
        store.choose(first, 1)
        store.choose(second, 1)
        store.ensure(
            Operation(Operator.add, (Operation(Operator.abs, (first,)), second))
        )
        domains, types = _metadata(store)
        if empty:
            domains[second] = Domain()
        domains[first] = UNKNOWN_DOMAIN
        nested = InternalOperation(Operator.abs, (first,))
        domains[nested] = UNKNOWN_DOMAIN
        _split(store, domains, types)
        assert set(store.variables) == {first, second}
        expression = store.expressions[store.constraints[0].expr]
        assert isinstance(expression, InternalOperation)
        assert expression.op == Operator.python_eval


def test_ties_and_repeated_occurrences() -> None:
    """Prefer no split on ties and allocate separate auxiliaries per occurrence."""
    store = ConstraintStore()
    variable = VariableRef("x")
    inputs = (variable, VariableRef("y"), VariableRef("z"))
    for item in inputs:
        store.choose_from_iterator(item, range(10))
    inner = Operation(Operator.add, inputs)
    store.ensure(Operation(Operator.sub, (inner, inner)))
    domains, types = _metadata(store)
    nested = InternalOperation(Operator.add, inputs)
    domains[nested] = Domain(ints=frozenset({1}))
    types[nested] = frozenset({ValueType.integer})
    _split(store, domains, types)
    auxiliaries = set(store.variables) - set(inputs)
    assert len(auxiliaries) == 2
    expression = store.expressions[store.constraints[0].expr]
    assert isinstance(expression, InternalOperation)
    assert expression.args[0] != expression.args[1]
    tied = ConstraintStore()
    tied.choose(variable, 1)
    inner = Operation(Operator.abs, (variable,))
    nested = InternalOperation(Operator.abs, (variable,))
    tied.ensure(Operation(Operator.add, (inner, 0)))
    domains, types = _metadata(tied)
    domains[variable] = Domain(ints=frozenset({1, 2}))
    domains[nested] = Domain(ints=frozenset({1}))
    _split(tied, domains, types)
    assert set(tied.variables) == {variable}


def test_collection_operations_closed_calls_and_fresh_names() -> None:
    """Convert collection nesting and closed expressions without name capture."""
    store = ConstraintStore()
    variable = VariableRef("__split_0")
    store.choose(variable, 1)
    store.define(VariableRef("result"), (Operation(Operator.abs, (variable,)),))
    store.define(
        VariableRef("closed"),
        Operation(Operator.add, (Operation(Operator.abs, (1,)), 2)),
    )
    domains, types = _metadata(store)
    _split(store, domains, types)
    for name, arity in (("result", 1), ("closed", 0)):
        definition = store.variables[VariableRef(name)].definitions[0]
        expression = store.expressions[definition.value]
        assert isinstance(expression, InternalOperation)
        assert expression.op == Operator.python_eval
        assert len(expression.args[1:]) == arity
        assert _callback(expression)(*([1] * arity)) == ((1,) if arity else 3)


def test_wide_expression_guard_and_negative_limit() -> None:
    """Handle many nested parameters with bounded all-or-nothing search."""
    store = ConstraintStore()
    variables = tuple(VariableRef(f"x{index}") for index in range(100))
    for variable in variables:
        store.choose_from_iterator(variable, (False, True))
    store.ensure(
        Operation(
            Operator.disj,
            tuple(Operation(Operator.lnot, (variable,)) for variable in variables),
        )
    )
    domains, types = _metadata(store)
    with pytest.raises(ValueError, match="nonnegative"):
        _split(store, domains, types, subset_limit=-1)
    _split(store, domains, types, subset_limit=4)
    assert len(store.variables) == 200


@pytest.mark.parametrize(
    "operator, names, expected",
    [
        (Operator.leqv, ("p", "q"), 2),
        (Operator.eq, ("first", "second"), 5),
        (Operator.neq, ("first", "second"), 5),
        (Operator.eq, ("x", "y"), 6),
        (Operator.neq, ("x", "y"), 6),
        (Operator.union, ("first", "second"), 5),
        (Operator.inter, ("first", "second"), 2),
        (Operator.diff, ("first", "second"), 3),
        (Operator.subset, ("first", "second"), 3),
        (Operator.set_make, ("x", "y"), 8),
        (Operator.set_isin, ("x", "first"), 3),
        (Operator.set_notin, ("x", "first"), 3),
        (Operator.cardinality, ("first",), 7),
        (Operator.length, ("text",), 3),
    ],
)
def test_specialized_costs(
    operator: Operator, names: tuple[str, ...], expected: int
) -> None:
    """Check exact encoding costs, including implicit sets and mixed kinds."""
    store = ConstraintStore()
    for name, count in (("x", 3), ("y", 5)):
        store.choose_from_iterator(VariableRef(name), range(count))
    for name in ("p", "q"):
        store.choose_from_iterator(VariableRef(name), (False, True))
    for name, count in (("first", 3), ("second", 2)):
        store.set_contain_choose_from_iterator(VariableRef(name), range(count))
    store.choose_from_iterator(VariableRef("text"), ("a", "bb", "ccc"))
    result = VariableRef("result")
    store.define(
        result, Operation(operator, tuple(VariableRef(name) for name in names))
    )
    domains, types = _metadata(store)
    definition = store.variables[result].definitions[0]
    expression = store.expressions[definition.value]
    assert isinstance(expression, InternalOperation)
    costs = GroundingCost(domains, types)
    assert costs.trivial_cost(expression) == expected
    assert costs.complexity(expression) == expected


def test_length_cost_uses_static_set_kind() -> None:
    """Check the cost-table overload independently of string-only validation."""
    variable = VariableRef("set")
    expression = InternalOperation(Operator.length, (variable,))
    domains = DomainStore(
        {
            variable: Domain(implicit_set_elements=frozenset({0, 1, 2})),
            expression: Domain(ints=frozenset(range(4))),
        }
    )
    types = StaticTypeStore(
        {variable: frozenset({SetOf(frozenset({ValueType.integer}), True)})}
    )
    costs = GroundingCost(domains, types)
    assert costs.trivial_cost(expression) == 7
    types[variable] = frozenset({ValueType.string})
    assert costs.trivial_cost(expression) == 8
    types[variable] = UnknownType()
    assert costs.trivial_cost(expression) == 8


def _proper_subset_problem(parameter_count: int) -> ConstraintStore:
    """Build a problem where only replacing the first nested parameter helps."""
    store = ConstraintStore()
    first, second, third = (VariableRef(name) for name in "abc")
    for variable, count in ((first, 2), (second, 2), (third, 10)):
        store.choose_from_iterator(variable, range(count))
    store.define(
        VariableRef("result"),
        Operation(
            Operator.add,
            (
                Operation(Operator.add, (first, second)),
                *(
                    Operation(Operator.abs, (third,))
                    for _ in range(parameter_count - 1)
                ),
            ),
        ),
    )
    return store


@pytest.mark.parametrize("parameter_count, auxiliaries", [(12, 1), (13, 0)])
def test_default_subset_limit_boundary(parameter_count: int, auxiliaries: int) -> None:
    """Search proper subsets at twelve parameters but only all at thirteen."""
    store = _proper_subset_problem(parameter_count)
    domains, types = _metadata(store)
    original = set(store.variables)
    _split(store, domains, types)
    added = set(store.variables) - original
    assert len(added) == auxiliaries
    for variable in added:
        definition = store.variables[variable].definitions[0]
        call = store.expressions[definition.value]
        assert isinstance(call, InternalOperation)
        assert call.args[1:] == (VariableRef("a"), VariableRef("b"))
        assert _callback(call)(2, 3) == 5


@pytest.mark.parametrize("limit, auxiliaries", [(1, 0), (2, 1)])
def test_guard_rejects_unprofitable_all_parameter_split(
    limit: int, auxiliaries: int
) -> None:
    """A profitable proper subset is unavailable above the configured limit."""
    store = _proper_subset_problem(2)
    domains, types = _metadata(store)
    original = set(store.variables)
    _split(store, domains, types, subset_limit=limit)
    assert len(set(store.variables) - original) == auxiliaries


@pytest.mark.parametrize("cardinality", [1, 10])
def test_existing_lambda_arguments_are_split_and_converted(cardinality: int) -> None:
    """Lower nested actual arguments without rewriting the callable's body."""
    store = ConstraintStore()
    variable, parameter = VariableRef("x"), VariableRef("u")
    store.choose_from_iterator(variable, range(cardinality))
    store.define(
        VariableRef("result"),
        Operation(
            Operator.lambda_,
            (
                Lambda((parameter,), parameter),
                Operation(Operator.add, (Operation(Operator.abs, (variable,)), 1)),
            ),
        ),
    )
    domains, types = _metadata(store)
    _split(store, domains, types)
    definition = store.variables[VariableRef("result")].definitions[0]
    call = store.expressions[definition.value]
    assert isinstance(call, InternalOperation) and call.op == Operator.python_eval
    assert all(isinstance(arg, VariableRef) for arg in call.args[1:])
    assert domains[VariableRef("result")] == Domain(
        ints=frozenset(range(1, cardinality + 1))
    )
    assert set(store.variables) == {variable, VariableRef("result")}
    assert _callback(call)(-2) == 3
    before = store.copy()
    _split(store, domains, types)
    assert store == before


@pytest.mark.parametrize("captured_argument", [False, True])
def test_lambda_cost_includes_captures_once(captured_argument: bool) -> None:
    """Reject false savings caused by ignoring a callable's captured inputs."""
    store = ConstraintStore()
    captured, actual, parameter = (VariableRef(name) for name in ("x", "y", "u"))
    for variable in (captured, actual):
        store.choose_from_iterator(variable, range(10))
    argument = captured if captured_argument else actual
    result = VariableRef("result")
    callback = Lambda((parameter,), Operation(Operator.add, (captured, parameter)))
    store.define(
        result,
        Operation(Operator.lambda_, (callback, Operation(Operator.abs, (argument,)))),
    )
    domains, types = _metadata(store)
    definition = store.variables[result].definitions[0]
    expression = store.expressions[definition.value]
    assert isinstance(expression, InternalOperation)
    costs = GroundingCost(domains, types)
    assert costs.trivial_cost(expression) == 100
    direct = InternalOperation(Operator.lambda_, (expression.args[0], captured))
    assert costs.trivial_cost(direct) == 10
    _split(store, domains, types)
    assert set(store.variables) == {captured, actual, result}


def test_lambda_proper_subset_retains_captured_dependencies() -> None:
    """Keep captures in the outer cost even when their nested argument is selected."""
    store = ConstraintStore()
    captured, actual, first, second = (
        VariableRef(name) for name in ("x", "z", "u", "v")
    )
    store.choose_from_iterator(captured, range(-5, 5))
    store.choose_from_iterator(actual, range(10))
    callback = Lambda(
        (first, second), Operation(Operator.add, (captured, first, second))
    )
    result = VariableRef("result")
    store.define(
        result,
        Operation(
            Operator.lambda_,
            (
                callback,
                Operation(Operator.abs, (captured,)),
                Operation(Operator.abs, (actual,)),
            ),
        ),
    )
    domains, types = _metadata(store)
    _split(store, domains, types)
    assert set(store.variables) == {captured, actual, result}


def test_fold_cost_includes_captures() -> None:
    """Include a fold callback's captured inputs in complete-value enumeration."""
    captured, values, initial, accumulator, item = (
        VariableRef(name) for name in ("x", "values", "initial", "acc", "item")
    )
    callback = InternalLambda((accumulator, item), captured)
    expression = InternalOperation(Operator.set_fold, (callback, values, initial))
    domains = DomainStore(
        {
            captured: Domain(ints=frozenset(range(10))),
            values: Domain(implicit_set_elements=frozenset({0, 1})),
            initial: Domain(ints=frozenset({0, 1, 2})),
        }
    )
    assert GroundingCost(domains, StaticTypeStore()).trivial_cost(expression) == 120


def test_existing_lambda_arguments_use_profitable_splits() -> None:
    """Split actual parameters before compiling the existing callable descriptor."""
    store = ConstraintStore()
    first, second, third = (VariableRef(name) for name in "abc")
    for variable in (first, second, third):
        store.choose_from_iterator(variable, range(10))
    left, right = VariableRef("left"), VariableRef("right")
    callback = Lambda((left, right), Operation(Operator.add, (left, right)))
    result = VariableRef("result")
    store.define(
        result,
        Operation(
            Operator.lambda_,
            (callback, Operation(Operator.add, (first, second)), third),
        ),
    )
    domains, types = _metadata(store)
    _split(store, domains, types)
    (auxiliary,) = set(store.variables) - {first, second, third, result}
    definition = store.variables[result].definitions[0]
    call = store.expressions[definition.value]
    assert isinstance(call, InternalOperation)
    assert call.args[1:] == (auxiliary, third)
    assert _callback(call)(3, 4) == 7
    auxiliary_definition = store.variables[auxiliary].definitions[0]
    auxiliary_call = store.expressions[auxiliary_definition.value]
    assert isinstance(auxiliary_call, InternalOperation)
    assert auxiliary_call.args[1:] == (first, second)
    assert _callback(auxiliary_call)(2, 3) == 5


def test_collection_and_python_renaming() -> None:
    """Rename variables inside sets without modifying Python source descriptors."""
    store = ConstraintStore()
    variable = VariableRef("x")
    store.choose_from_iterator(variable, (1, 2))
    store.define(
        VariableRef("set_result"), frozenset({Operation(Operator.abs, (variable,))})
    )
    callback = Python("lambda value: value")
    store.define(
        VariableRef("python_result"),
        Operation(
            Operator.sub,
            (Operation(Operator.python_eval, (callback, variable)), variable),
        ),
    )
    domains, types = _metadata(store)
    _split(store, domains, types)
    for name in ("set_result", "python_result"):
        definition = store.variables[VariableRef(name)].definitions[0]
        call = store.expressions[definition.value]
        assert isinstance(call, InternalOperation) and call.op == Operator.python_eval
        assert call.args[1:] == (variable,)
        if name == "set_result":
            assert _callback(call)(-2) == frozenset({2})
            assert domains[call] == Domain(
                explicit_sets=frozenset({frozenset({1}), frozenset({2})})
            )
        else:
            assert _callback(call)(2) == 0


def test_store_preserves_unknown_and_set_metadata() -> None:
    """Distinguish recorded unknown results from missing metadata."""
    variable = VariableRef("x")
    domains = DomainStore()
    types = StaticTypeStore()
    domains[variable] = UNKNOWN_DOMAIN
    types[variable] = UnknownType()
    assert domains[variable].unknown
    assert isinstance(types[variable], UnknownType)
    literal = ValueDef(ValueType.integer, 1)
    domains[literal] = Domain(ints=frozenset({1}))
    types[literal] = frozenset({ValueType.integer})
    assert domains[literal].cardinality() == 1


def test_lambda_conversion_preserves_existing_scopes_and_captures() -> None:
    """Rename captured variables without capturing an existing lambda parameter."""
    store = ConstraintStore()
    captured = VariableRef("x")
    shadowed = VariableRef("__split_0")
    store.choose_from_iterator(captured, range(10))
    inner = Operation(
        Operator.lambda_,
        (Lambda((shadowed,), Operation(Operator.add, (shadowed, captured))), 1),
    )
    store.define(VariableRef("result"), Operation(Operator.sub, (inner, captured)))
    domains, types = _metadata(store)
    _split(store, domains, types)
    definition = store.variables[VariableRef("result")].definitions[0]
    call = store.expressions[definition.value]
    assert isinstance(call, InternalOperation)
    assert call.args[1:] == (captured,)
    assert _callback(call)(4) == 1
    renamed = VariableRef("__split_1")
    nested = InternalOperation(Operator.add, (shadowed, renamed))
    domain_scope = frozenset(
        {
            (renamed, domains[captured]),
            (shadowed, Domain(ints=frozenset({1}))),
        }
    )
    assert domains.lookup(nested, scope=domain_scope) == Domain(
        ints=frozenset(range(1, 11))
    )
    type_scope = frozenset(
        (parameter, frozenset({ValueType.integer})) for parameter in (renamed, shadowed)
    )
    assert types.lookup(nested, scope=type_scope) == frozenset({ValueType.integer})
