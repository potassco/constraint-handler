"""Construct caches for tests of individual preprocessing passes."""

from collections.abc import Mapping

from constraint_handler import ConstraintStore, Diagnostics, DomainCache
from constraint_handler.domains import (
    DEFAULT_BOOLEAN_THRESHOLD,
    DEFAULT_THRESHOLD,
    Domain,
)
from constraint_handler.internal_input import Expr
from constraint_handler.util import EvaluationOrder


def compute_domains(
    store: ConstraintStore,
    order: EvaluationOrder,
    diagnostics: Diagnostics,
    *,
    threshold: int = DEFAULT_THRESHOLD,
    boolean_threshold: int = DEFAULT_BOOLEAN_THRESHOLD,
    python_context: Mapping[str, object] | None = None,
) -> DomainCache:
    """Prepare pass metadata without making the cache depend on an evaluation order."""
    cache = DomainCache(
        store, threshold, boolean_threshold, python_context, diagnostics=diagnostics
    )
    for variable in (*store.variables, *store.set_variables):
        cache.get_domain(variable)
    for expression in store.expressions.values():
        cache.get_domain(expression)
    return cache


def seeded_domains(
    values: Mapping[Expr, Domain] | None = None, *, store: ConstraintStore | None = None
) -> DomainCache:
    """Register trusted test bounds without exposing mutable cache dictionaries."""
    cache = DomainCache(store if store is not None else ConstraintStore())
    for expression, domain in (values or {}).items():
        cache.set_domain(expression, domain)
    return cache
