from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import ClassVar, Iterable, Mapping

import clingo
from constraint_handler.utils.python_domain import Domain, DomainAtom

@dataclass(slots=True)
class ComputedDomains:
    """Cached compile2 domain-computation outputs for one grounding run."""

    expression_domains: dict[clingo.Symbol, Domain]
    set_candidate_domains: dict[clingo.Symbol, set[DomainAtom]]
    set_expressions: set[clingo.Symbol]
    global_set_uids: dict[frozenset[DomainAtom], int]

    def expression_domain_symbols(self) -> Iterable[clingo.Symbol]:
        """Yield `_se_domain/2` facts for all computed expressions."""
        for expr, domain in sorted(self.expression_domains.items()):
            yield from domain.expression_domain_symbols(
                expr,
                include_set_values=expr not in self.set_expressions,
            )

    def expression_set_domain_symbols(self) -> Iterable[clingo.Symbol]:
        """Yield `_se_set_domain(Expr,Uid)` facts for all computed expressions."""
        for expr, domain in sorted(self.expression_domains.items()):
            yield from domain.expression_set_domain_symbols(expr, self.global_set_uids)

    def expression_set_domain_value_symbols(self) -> Iterable[clingo.Symbol]:
        """Yield `_se_set_domain(Uid,Sign,Value)` facts across all set expressions."""
        seen: set[clingo.Symbol] = set()
        for expr, domain in sorted(self.expression_domains.items()):
            for symbol in domain.set_domain_value_symbols(
                self.global_set_uids,
                self.set_candidate_domains.get(expr, ()),
            ):
                if symbol in seen:
                    continue
                seen.add(symbol)
                yield symbol

    def expression_set_domain_symbol_symbols(self, expr: clingo.Symbol) -> Iterable[clingo.Symbol]:
        """Yield `(Uid,SetValue)` tuples for one set-valued expression."""
        domain = self.expression_domains.get(expr)
        if domain is None:
            return ()
        return domain.expression_set_domain_symbol_symbols(self.global_set_uids)


class DomainComputation:
    """Compute compile2 expression domains directly from raw clingo symbols."""

    VARIABLE_SOURCE_NAMES: ClassVar[frozenset[str]] = frozenset({
        "variable_define",
        "variable_domain",
        "set_assign",
        "set_baseDomain",
    })
    @classmethod
    def is_function(cls, symbol: clingo.Symbol, name: str | None = None, arity: int | None = None) -> bool:
        """Check whether one symbol is a function term with an optional signature."""
        if symbol.type != clingo.SymbolType.Function:
            return False
        if name is not None and symbol.name != name:
            return False
        if arity is not None and len(symbol.arguments) != arity:
            return False
        return True

    @classmethod
    def is_tuple(cls, symbol: clingo.Symbol, arity: int | None = None) -> bool:
        """Check whether one symbol is represented as an anonymous tuple term."""
        return cls.is_function(symbol, "", arity)

    @classmethod
    def sequence_items(cls, symbol: clingo.Symbol) -> list[clingo.Symbol] | None:
        """Flatten one nested pair-list into a Python list when it ends in ()."""
        items: list[clingo.Symbol] = []
        current = symbol
        while cls.is_tuple(current, 2):
            items.append(current.arguments[0])
            current = current.arguments[1]
        if cls.is_tuple(current, 0):
            return items
        return None

    @classmethod
    def domain_values(cls, domain: Domain) -> set[DomainAtom]:
        """Return all non-set runtime values stored in one domain."""
        return {value for value in domain.values() if not isinstance(value, frozenset)}

    @classmethod
    def set_uid_sort_key(cls, value: object):
        """Build a deterministic structural ordering key for set-uid assignment."""
        if value is None:
            return (0,)
        if isinstance(value, bool):
            return (1, int(value))
        if isinstance(value, int):
            return (2, value)
        if isinstance(value, float):
            return (3, value)
        if isinstance(value, str):
            return (4, value)
        if isinstance(value, clingo.Symbol):
            return (5, value)
        if isinstance(value, tuple):
            return (6, tuple(cls.set_uid_sort_key(item) for item in value))
        if isinstance(value, frozenset):
            return (7, tuple(sorted(cls.set_uid_sort_key(item) for item in value)))
        return (8, repr(value))

    @classmethod
    def set_sort_key(cls, value: frozenset[DomainAtom]):
        """Build a deterministic structural ordering key for one concrete set value."""
        return tuple(sorted(cls.set_uid_sort_key(member) for member in value))

    @classmethod
    def direct_subexpressions(cls, expr: clingo.Symbol) -> list[clingo.Symbol]:
        """Return the immediate child expressions that influence one expression domain."""
        if cls.is_function(expr, "operation", 2):
            arg_exprs = cls.sequence_items(expr.arguments[1])
            return [] if arg_exprs is None else arg_exprs
        if cls.is_function(expr, "python", 1):
            return []
        if cls.is_function(expr, "variable", 1) or cls.is_function(expr, "val", 2) or cls.is_function(expr, "bad", 0):
            return []
        if cls.is_tuple(expr) and cls.sequence_items(expr) is None:
            return list(expr.arguments)
        return []

    @classmethod
    def flatten_set_values(cls, domain: Domain) -> set[DomainAtom]:
        """Collect all members appearing in the concrete set values of one domain."""
        values: set[DomainAtom] = set()
        for set_value in domain.sets:
            values.update(set_value)
        return values

    @classmethod
    def register_set_uids(cls, domain: Domain, global_set_uids: dict[frozenset[DomainAtom], int]) -> None:
        """Assign stable integer ids to newly seen concrete set values."""
        for set_value in sorted(domain.sets, key=cls.set_sort_key):
            global_set_uids.setdefault(set_value, len(global_set_uids))

    @classmethod
    def source_maps(
        cls,
        top_level_expressions: Iterable[clingo.Symbol],
    ) -> tuple[dict[clingo.Symbol, list[clingo.Symbol]], dict[clingo.Symbol, dict[str, list[clingo.Symbol]]]]:
        """Split top-level variable-related declarations into scalar and set source maps."""
        variable_sources: dict[clingo.Symbol, list[clingo.Symbol]] = {}
        set_sources: dict[clingo.Symbol, dict[str, list[clingo.Symbol]]] = {}
        for expr in sorted(top_level_expressions):
            if not cls.is_function(expr, arity=2) or expr.name not in cls.VARIABLE_SOURCE_NAMES:
                continue
            var, source_expr = expr.arguments
            if expr.name in {"variable_define", "variable_domain"}:
                variable_sources.setdefault(var, []).append(source_expr)
                continue
            bucket = set_sources.setdefault(var, {"set_assign": [], "set_baseDomain": []})
            bucket[expr.name].append(source_expr)
        return variable_sources, set_sources

    @classmethod
    def normalize_solver_identifiers(
        cls,
        solver_identifiers: Iterable[clingo.Symbol] | None,
    ) -> tuple[clingo.Symbol, ...]:
        """Flatten the `_main_solverIdentifiers/1` list term into evaluator identifiers."""
        raw_identifiers = tuple(solver_identifiers or ())
        if len(raw_identifiers) == 1:
            sequence = cls.sequence_items(raw_identifiers[0])
            if sequence is not None:
                return tuple(sequence)
        return raw_identifiers

    @classmethod
    def domain_from_value(cls, symbol: clingo.Symbol) -> Domain:
        """Convert one compile2 val(...) term into the matching runtime domain."""
        return Domain.from_symbol(symbol)

    @classmethod
    def evaluate_tuple(cls, expr: clingo.Symbol, expression_domains: Mapping[clingo.Symbol, Domain]) -> Domain:
        """Enumerate tuple values from already-computed child domains."""
        child_domains = [expression_domains.get(child, Domain.empty()) for child in expr.arguments]
        if any(not child.has_values() and not child.is_none for child in child_domains):
            return Domain.empty()
        tuple_values = {values for values in product(*(child.values(include_bad=True) for child in child_domains))}
        return Domain.tuple_values(*tuple_values)

    @classmethod
    def concrete_set_domain(
        cls,
        var: clingo.Symbol,
        expression_domains: Mapping[clingo.Symbol, Domain],
        set_sources: Mapping[clingo.Symbol, dict[str, list[clingo.Symbol]]],
    ) -> set[frozenset[DomainAtom]] | None:
        """Enumerate the concrete set values implied by one set variable and its sources."""
        if var not in set_sources:
            return None
        source_info = set_sources[var]
        optional_candidates: set[DomainAtom] = set()
        for source_expr in source_info["set_baseDomain"]:
            optional_candidates.update(cls.domain_values(expression_domains.get(source_expr, Domain.empty())))
        required_scalars: set[DomainAtom] = set()
        required_set_options: list[tuple[frozenset[DomainAtom], ...]] = []
        for source_expr in source_info["set_assign"]:
            source_domain = expression_domains.get(source_expr, Domain.empty())
            required_scalars.update(cls.domain_values(source_domain))
            set_options = tuple(source_domain.sets)
            if set_options:
                required_set_options.append(set_options)
        concrete_sets: set[frozenset[DomainAtom]] = set()
        set_combinations = product(*required_set_options) if required_set_options else [()]
        for chosen_sets in set_combinations:
            required_members = set(required_scalars)
            for chosen_set in chosen_sets:
                required_members.update(chosen_set)
            optional_members = optional_candidates.difference(required_members)
            ordered_optional = tuple(optional_members)
            for mask in range(1 << len(ordered_optional)):
                members = set(required_members)
                for index, member in enumerate(ordered_optional):
                    if mask & (1 << index):
                        members.add(member)
                concrete_sets.add(frozenset(members))
        return concrete_sets

    @classmethod
    def set_candidate_domain(
        cls,
        expr: clingo.Symbol,
        expression_domains: Mapping[clingo.Symbol, Domain],
        set_sources: Mapping[clingo.Symbol, dict[str, list[clingo.Symbol]]],
    ) -> set[DomainAtom] | None:
        """Collect candidate element values used when exporting set-domain memberships."""
        if cls.is_function(expr, "variable", 1):
            var = expr.arguments[0]
            if var not in set_sources:
                candidates = cls.flatten_set_values(expression_domains.get(expr, Domain.empty()))
                return candidates or None
            candidates: set[DomainAtom] = set()
            for source_expr in set_sources[var]["set_baseDomain"] + set_sources[var]["set_assign"]:
                source_domain = expression_domains.get(source_expr, Domain.empty())
                candidates.update(cls.domain_values(source_domain))
                candidates.update(cls.flatten_set_values(source_domain))
            return candidates or None
        candidates = cls.flatten_set_values(expression_domains.get(expr, Domain.empty()))
        return candidates or None

    @classmethod
    def evaluate_expression(
        cls,
        expr: clingo.Symbol,
        expression_domains: Mapping[clingo.Symbol, Domain],
        solver_identifiers: tuple[clingo.Symbol, ...],
    ) -> Domain:
        """Evaluate one raw compile2 expression symbol into a runtime domain."""
        if cls.is_function(expr, "bad", 0):
            return Domain.bad()
        if cls.is_function(expr, "val", 2):
            return cls.domain_from_value(expr)
        if cls.is_function(expr, "python", 1):
            return Domain.evaluate_python_expression(expr.arguments[0].string, solver_identifiers)
        if cls.is_function(expr, "operation", 2):
            operator, raw_args = expr.arguments
            arg_exprs = cls.sequence_items(raw_args)
            if arg_exprs is None:
                return Domain.bad()
            arg_domains = [expression_domains.get(arg_expr, Domain.empty()) for arg_expr in arg_exprs]
            return Domain.compute_domain(operator, *arg_domains, solver_identifiers=solver_identifiers)
        if cls.is_tuple(expr) and cls.sequence_items(expr) is None:
            return cls.evaluate_tuple(expr, expression_domains)
        if cls.is_function(expr, "variable", 1):
            return expression_domains.get(expr, Domain.empty())
        return Domain.symbols_only(expr)

    @classmethod
    def sorted_expressions(cls, top_level_expressions: Iterable[clingo.Symbol]) -> Iterable[clingo.Symbol]:
        """Yield expressions in a dependency-first order with variable sources expanded first."""
        expressions = set(top_level_expressions)
        seen: set[clingo.Symbol] = set()
        visiting: set[clingo.Symbol] = set()
        expanded_variables: set[clingo.Symbol] = set()
        variable_sources = {
            var: sorted(
                [
                    expr
                    for expr in expressions
                    if cls.is_function(expr, arity=2) and expr.name in cls.VARIABLE_SOURCE_NAMES and expr.arguments[0] == var
                ]
            )
            for var in {
                expr.arguments[0]
                for expr in expressions
                if cls.is_function(expr, arity=2) and expr.name in cls.VARIABLE_SOURCE_NAMES
            }
        }

        def visit(expr: clingo.Symbol):
            if expr in seen or expr in visiting:
                return
            visiting.add(expr)
            if cls.is_function(expr, "variable", 1) and expr.arguments[0] not in expanded_variables:
                expanded_variables.add(expr.arguments[0])
                for dependency in variable_sources.get(expr.arguments[0], []):
                    yield from visit(dependency)
            children = [expr.arguments[1]] if expr.name in cls.VARIABLE_SOURCE_NAMES and len(expr.arguments) == 2 else cls.direct_subexpressions(expr)
            for child in children:
                yield from visit(child)
            visiting.remove(expr)
            seen.add(expr)
            yield expr

        for expr in sorted(expressions):
            yield from visit(expr)

    @classmethod
    def compute(
        cls,
        top_level_expressions: Iterable[clingo.Symbol],
        solver_identifiers: Iterable[clingo.Symbol] | None = None,
    ) -> ComputedDomains:
        """Compute compile2 expression domains and the derived set export metadata."""
        expressions = set(top_level_expressions)
        solver_identifier_key = cls.normalize_solver_identifiers(solver_identifiers)
        variable_sources, set_sources = cls.source_maps(expressions)
        expression_domains: dict[clingo.Symbol, Domain] = {}
        set_candidate_domains: dict[clingo.Symbol, set[DomainAtom]] = {}
        set_expressions: set[clingo.Symbol] = set()
        global_set_uids: dict[frozenset[DomainAtom], int] = {}
        for expr in cls.sorted_expressions(expressions):
            if cls.is_function(expr, arity=2) and expr.name in cls.VARIABLE_SOURCE_NAMES:
                continue
            if cls.is_function(expr, "variable", 1):
                var = expr.arguments[0]
                domain = Domain.empty()
                for source_expr in variable_sources.get(var, []):
                    domain.absorb(expression_domains.get(source_expr, Domain.empty()))
                concrete_sets = cls.concrete_set_domain(var, expression_domains, set_sources)
                if concrete_sets is not None:
                    domain.sets.update(concrete_sets)
                expression_domains[expr] = domain
            else:
                expression_domains[expr] = cls.evaluate_expression(expr, expression_domains, solver_identifier_key)
            if expression_domains[expr].sets or (cls.is_function(expr, "variable", 1) and expr.arguments[0] in set_sources):
                set_expressions.add(expr)
            candidate_domain = cls.set_candidate_domain(expr, expression_domains, set_sources)
            if candidate_domain is not None:
                set_candidate_domains[expr] = candidate_domain
            cls.register_set_uids(expression_domains[expr], global_set_uids)
        return ComputedDomains(
            expression_domains=expression_domains,
            set_candidate_domains=set_candidate_domains,
            set_expressions=set_expressions,
            global_set_uids=global_set_uids,
        )