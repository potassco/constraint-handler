"""Cache approximate domains and evaluated tables for one preprocessing session."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from ..diagnostics import Diagnostics
from ..internal_input import ConstraintStore, Expr, VariableRef
from ._domain import (
    DEFAULT_BOOLEAN_THRESHOLD,
    DEFAULT_THRESHOLD,
    UNKNOWN_DOMAIN,
    Domain,
    PythonTable,
)

type DomainScope = frozenset[tuple[VariableRef, Domain]]


@dataclass(frozen=True, slots=True)
class DomainTable:
    """Store ordered inputs, successful input/output rows, and their output domain."""

    inputs: tuple[Expr, ...]
    input_domains: tuple[Domain, ...]
    bindings: DomainScope
    rows: PythonTable
    output_domain: Domain


class DomainCache:
    """Cache approximate domains and table rows while the store's meaning stays fixed.

    An approximate domain includes every possible result, but may include extra
    values. A table records which outputs were produced for particular inputs.
    """

    def __init__(
        self,
        store: ConstraintStore,
        threshold: int = DEFAULT_THRESHOLD,
        boolean_threshold: int = DEFAULT_BOOLEAN_THRESHOLD,
        python_context: Mapping[str, object] | None = None,
        *,
        diagnostics: Diagnostics | None = None,
    ) -> None:
        """Copy the Python context and keep fixed enumeration limits for this session."""
        from ._domain_computation import _DomainComputation

        if threshold < 0 or boolean_threshold < 0:
            raise ValueError("Domain enumeration thresholds must be nonnegative")
        self._entries: dict[tuple[Expr, DomainScope], Domain] = {}
        self._computing: set[tuple[Expr, DomainScope]] = set()
        self._computation = _DomainComputation(
            self,
            store,
            threshold,
            boolean_threshold,
            dict(python_context or {}),
            diagnostics,
        )

    def get_domain(
        self, expr: Expr, bindings: Mapping[VariableRef, Domain] | None = None
    ) -> Domain:
        """Return an approximate domain, caching it separately for each set of bindings."""
        scope: DomainScope = frozenset(bindings.items()) if bindings else frozenset()
        key = expr, scope
        if key in self._entries:
            return self._entries[key]
        if key in self._computing:
            return UNKNOWN_DOMAIN
        self._computing.add(key)
        try:
            result = self._computation.compute(expr, dict(scope))
            self.set_domain(expr, result, dict(scope))
            return result
        finally:
            self._computing.remove(key)

    def set_domain(
        self,
        expr: Expr,
        known_domain: Domain,
        bindings: Mapping[VariableRef, Domain] | None = None,
    ) -> None:
        """Cache a supplied domain without evaluation; reject a different cached domain.

        The caller must ensure the supplied domain includes every possible
        result. Supplying a domain does not create table rows.
        """
        scope: DomainScope = frozenset(bindings.items()) if bindings else frozenset()
        key = expr, scope
        if key in self._entries and self._entries[key] != known_domain:
            raise ValueError("A different domain is already cached for this expression")
        self._entries[key] = known_domain

    def get_table(
        self, expr: Expr, bindings: Mapping[VariableRef, Domain] | None = None
    ) -> DomainTable | None:
        """Return a cached or newly evaluated table, or None if evaluation is unavailable."""
        scope: DomainScope = frozenset(bindings.items()) if bindings else frozenset()
        return self._computation.table(expr, dict(scope))
