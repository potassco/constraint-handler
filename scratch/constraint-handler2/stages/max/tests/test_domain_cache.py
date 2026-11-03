"""Behavioral contracts for lazy domain bounds and retained finite relations."""

import ast
from pathlib import Path
from unittest.mock import patch

import pytest

import constraint_handler.domains as domain_api
from constraint_handler import (
    ConstraintStore,
    Diagnostics,
    Lambda,
    Operation,
    Operator,
    Python,
    VariableRef,
)
from constraint_handler.domains import EMPTY_DOMAIN, UNKNOWN_DOMAIN, Domain, DomainCache
from constraint_handler.domains._domain import domain_from_values, join_domains
from constraint_handler.internal_input import convert_expression
from constraint_handler.python_conversion import convert


def test_domain_package_public_boundary() -> None:
    """Keep the three-method service and prevent production imports of its internals."""
    methods = {
        name
        for name, value in vars(DomainCache).items()
        if not name.startswith("_") and callable(value)
    }
    assert methods == {"get_domain", "set_domain", "get_table"}
    assert domain_api.DomainCache is DomainCache
    assert not hasattr(domain_api, "prepare_domains")
    assert not hasattr(domain_api, "transfer_domain")
    package = Path(domain_api.__file__).parent
    assert Domain.__module__ == "constraint_handler.domains._domain"
    assert all(
        not (package / name).exists()
        for name in ("values.py", "_values.py", "sets.py", "evaluation.py")
    )
    definitions = [
        source.name
        for source in package.rglob("*.py")
        for node in ast.walk(ast.parse(source.read_text()))
        if isinstance(node, ast.ClassDef) and node.name == "Domain"
    ]
    assert definitions == ["_domain.py"]
    for source in package.parent.rglob("*.py"):
        if package in source.parents:
            continue
        for node in ast.walk(ast.parse(source.read_text())):
            if isinstance(node, ast.ImportFrom) and node.module is not None:
                assert not node.module.startswith(
                    ("domains.", "constraint_handler.domains.")
                ), source
            if isinstance(node, ast.Import):
                assert all(
                    not alias.name.startswith("constraint_handler.domains.")
                    for alias in node.names
                ), source


@pytest.mark.parametrize("operator", [Operator.conj, Operator.disj])
def test_boolean_symbolic_alternatives(operator: Operator) -> None:
    """Keep both outcomes when Boolean operands independently admit both values."""
    operand = VariableRef("operand")
    cache = DomainCache(ConstraintStore())
    cache.set_domain(operand, Domain(bools=(True, False)))
    expression = convert_expression(Operation(operator, (operand, operand)))
    assert cache.get_domain(expression) == Domain(bools=(True, False))


def test_domain_cache_resolves_sources_and_global_bindings() -> None:
    """Resolve sources on demand without capturing the querying lambda's bindings."""
    store = ConstraintStore()
    source, result = VariableRef("source"), VariableRef("result")
    store.choose_from_iterator(source, [1, 2])
    store.define(result, Operation(Operator.add, (source, 1)))
    cache = DomainCache(store)
    assert cache.get_domain(result) == domain_from_values([2, 3])
    assert cache.get_domain(
        result, {source: domain_from_values([100])}
    ) == domain_from_values([2, 3])
    assert cache.get_domain(
        source, {source: domain_from_values([100])}
    ) == domain_from_values([100])


def test_domain_cache_snapshots_bindings_and_trusted_transfers() -> None:
    """Keep trusted entries independent of caller mutations and reject conflicting writes."""
    parameter = VariableRef("parameter")
    expr = convert_expression(Operation(Operator.add, (parameter, 1)))
    cache = DomainCache(ConstraintStore())
    bindings = {parameter: domain_from_values([1])}
    cache.set_domain(expr, EMPTY_DOMAIN, bindings)
    bindings[parameter] = domain_from_values([10])
    assert cache.get_domain(expr, bindings) == domain_from_values([11])
    assert cache.get_domain(expr, {parameter: domain_from_values([1])}) == EMPTY_DOMAIN
    with pytest.raises(ValueError):
        cache.set_domain(expr, UNKNOWN_DOMAIN, bindings)


def test_domain_cache_cycles_and_missing_references() -> None:
    """Return completed unknown bounds rather than recursing or inventing empty values."""
    store = ConstraintStore()
    first, second = VariableRef("first"), VariableRef("second")
    store.define(first, second)
    store.define(second, first)
    cache = DomainCache(store)
    assert cache.get_domain(first) == UNKNOWN_DOMAIN
    assert cache.get_domain(VariableRef("missing")) == UNKNOWN_DOMAIN


def test_domain_cache_reuses_python_rows() -> None:
    """Share callback work between domain and table queries, even across expressions."""
    calls: list[int] = []

    def callback(value: int) -> int:
        """Record each concrete callback invocation."""
        calls.append(value)
        return value + 1

    store = ConstraintStore()
    source = VariableRef("source")
    store.choose_from_iterator(source, [1, 2])
    expr = convert_expression(
        Operation(Operator.python_eval, (Python("callback"), source))
    )
    cache = DomainCache(store, python_context={"callback": callback})
    assert cache.get_domain(expr) == domain_from_values([2, 3])
    table = cache.get_table(expr)
    assert table is not None
    assert table.inputs == (source,)
    assert len(table.rows) == 2
    assert sorted(calls) == [1, 2]
    assert cache.get_table(expr) is table
    assert cache.get_domain(expr) == table.output_domain
    assert len(calls) == 2


def test_domain_cache_negative_table_result_is_cached() -> None:
    """Reject excessive products before expanding input domains."""
    store = ConstraintStore()
    source = VariableRef("source")
    store.choose_from_iterator(source, range(3))
    cache = DomainCache(store, threshold=2)
    expr = convert_expression(
        Operation(Operator.python_eval, (Python("lambda value: value"), source))
    )
    cache.get_domain(source)
    with patch(
        "constraint_handler.domains.Domain.iter_values",
        side_effect=AssertionError("expanded"),
    ):
        assert cache.get_table(expr) is None
        assert cache.get_table(expr) is None


def test_domain_cache_short_circuit_does_not_execute_unused_branch() -> None:
    """Do not inspect a branch whose condition makes its result irrelevant."""
    expr = convert_expression(
        Operation(
            Operator.ite, (True, 7, Operation(Operator.python_eval, (Python("1 / 0"),)))
        )
    )
    assert DomainCache(ConstraintStore()).get_domain(expr) == domain_from_values([7])


def test_domain_cache_filters_invalid_alternatives_without_changing_sources() -> None:
    """Use admissible numeric alternatives while retaining the original source domain."""
    store = ConstraintStore()
    source = VariableRef("source")
    store.choose_from_iterator(source, [1, 2, "bad", True])
    cache = DomainCache(store)
    expr = convert_expression(Operation(Operator.add, (10, source)))
    assert cache.get_domain(expr) == domain_from_values([11, 12])
    assert cache.get_domain(source) == domain_from_values([1, 2, "bad", True])
    table = cache.get_table(expr)
    assert table is not None
    assert {output for _, output in table.rows} == {11, 12}
    assert table.input_domains == (domain_from_values([1, 2]),)


def test_domain_cache_set_bases_and_difference() -> None:
    """Forget exact membership, distinguish empty sets, and retain left difference members."""
    cache = DomainCache(ConstraintStore())
    left = convert_expression(frozenset({1, 2}))
    right = convert_expression(frozenset({2, 3}))
    assert cache.get_domain(left) == Domain(set_base=domain_from_values([1, 2]))
    assert cache.get_domain(left).cardinality() == 4
    assert cache.get_domain(convert_expression(frozenset())) != EMPTY_DOMAIN
    expr = convert_expression(
        Operation(Operator.diff, (frozenset({1, 2}), frozenset({2, 3})))
    )
    assert cache.get_domain(expr) == cache.get_domain(left)
    intersection = convert_expression(
        Operation(Operator.inter, (frozenset({1, 2}), frozenset({2, 3})))
    )
    assert cache.get_domain(intersection).set_base == domain_from_values([2])
    assert cache.get_domain(right).set_base == domain_from_values([2, 3])


def test_domain_cache_large_set_and_tuple_queries_do_not_enumerate() -> None:
    """Compute member bounds and tuple slots without expanding huge implicit axes."""
    store = ConstraintStore()
    source = VariableRef("source")
    cache = DomainCache(store)
    cache.set_domain(source, Domain(set_base=Domain(int_range=(0, 10**12))))
    expr = convert_expression(Operation(Operator.make_tuple, (source, 7)))
    length = convert_expression(Operation(Operator.length, (source,)))
    with patch.object(Domain, "iter_values", side_effect=AssertionError("expanded")):
        assert cache.get_domain(expr).tuple_domains
        assert cache.get_domain(length) == Domain(int_range=(0, 10**12 + 1))
        assert cache.get_table(expr) is None


def test_domain_cache_preserves_float_representation() -> None:
    """Keep integral reals and both signed zeros as distinct callback inputs."""
    store = ConstraintStore()
    source = VariableRef("source")
    cache = DomainCache(store)
    cache.set_domain(source, domain_from_values([1, 1.0, -0.0, 0.0]))
    expr = convert_expression(
        Operation(
            Operator.python_eval,
            (Python("lambda value: type(value).__name__ + ':' + repr(value)"), source),
        )
    )
    assert cache.get_domain(expr).strings == frozenset(
        {"int:1", "float:1.0", "float:-0.0", "float:0.0"}
    )
    assert domain_from_values([-0.0]) != domain_from_values([0.0])
    assert (
        join_domains([Domain(int_range=(1, 3)), Domain(int_range=(7, 9))]).int_count()
        == 6
    )


def test_domain_cache_fold_binds_element_before_accumulator() -> None:
    """Bind folds as (element, accumulator), retaining the initial empty-set case."""
    element, accumulator = VariableRef("element"), VariableRef("accumulator")
    body = Operation(Operator.add, (element, accumulator))
    expr = convert_expression(
        Operation(
            Operator.set_fold,
            (Lambda((element, accumulator), body), frozenset({1, 2}), 10),
        )
    )
    cache = DomainCache(ConstraintStore())
    assert cache.get_domain(expr) == domain_from_values([13])
    element_only = convert_expression(
        Operation(
            Operator.set_fold,
            (Lambda((element, accumulator), element), frozenset({7}), 0),
        )
    )
    assert cache.get_domain(element_only) == domain_from_values([7])


def test_domain_cache_trusted_domain_does_not_invent_table_rows() -> None:
    """Keep trusted output bounds while evaluating a more precise relation separately."""
    cache = DomainCache(ConstraintStore())
    expr = convert_expression(Operation(Operator.add, (1, 2)))
    cache.set_domain(expr, domain_from_values([3, 4]))
    table = cache.get_table(expr)
    assert table is not None and table.rows == (((), 3),)
    assert table.output_domain == domain_from_values([3])
    assert cache.get_domain(expr) == domain_from_values([3, 4])


def test_domain_cache_diagnostics_are_not_replayed() -> None:
    """Report new evaluation failures once and cache completed empty relations."""
    store = ConstraintStore()
    expr = convert_expression(
        Operation(Operator.python_eval, (Python("lambda: 1 / 0"),))
    )
    store.add_expression(expr)
    diagnostics = Diagnostics()
    cache = DomainCache(store, diagnostics=diagnostics)
    cache.get_domain(expr)
    count = len(diagnostics.items)
    assert count > 0
    assert cache.get_domain(expr) == EMPTY_DOMAIN
    table = cache.get_table(expr)
    assert table is not None and table.rows == ()
    assert len(diagnostics.items) == count


def test_domain_cache_lowering_reuses_original_rows() -> None:
    """Preserve input interpretation and completed rows across Python lowering."""
    store = ConstraintStore()
    original = convert_expression(Operation(Operator.add, (1.5, 2.0)))
    root = store.add_expression(original)
    cache = DomainCache(store)
    assert cache.get_domain(original) == domain_from_values([3.5])
    table = cache.get_table(original)
    lowered = convert_expression(
        Operation(Operator.python_eval, (convert((), original),))
    )
    cache.set_domain(lowered, cache.get_domain(original))
    store.replace_expression(root, lowered)
    assert cache.get_table(lowered) is table


@pytest.mark.parametrize("error", [MemoryError, RecursionError])
def test_domain_cache_does_not_swallow_processing_failures(
    error: type[Exception],
) -> None:
    """Propagate process-resource failures instead of treating them as cache results."""

    def callback() -> int:
        """Raise the requested unrecoverable processing failure."""
        raise error

    expr = convert_expression(Operation(Operator.python_eval, (Python("callback"),)))
    with pytest.raises(error):
        DomainCache(
            ConstraintStore(), python_context={"callback": callback}
        ).get_domain(expr)
