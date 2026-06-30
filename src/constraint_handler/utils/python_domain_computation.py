from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Any, ClassVar, Iterable, Mapping

import clingo

from constraint_handler.utils.python_domain import (
    Domain,
    DomainAtom,
    PythonEvaluationOutputRequest,
    PythonEvaluationSession,
)


@dataclass(frozen=True, slots=True)
class PythonWarningOutput:
    """Pre-encoded non-domain output emitted for Python evaluation warnings."""

    symbol: clingo.Symbol


PythonEvaluationValue = DomainAtom | PythonWarningOutput
PythonEvaluationAtom = tuple[clingo.Symbol, int]
PythonEvaluationInputAtom = tuple[clingo.Symbol, int, clingo.Symbol, DomainAtom]
PythonEvaluationOutputAtom = tuple[clingo.Symbol, int, PythonEvaluationValue]
PythonEvaluationAssignment = tuple[DomainAtom, ...]
PythonEvaluationOutputSignature = tuple[PythonEvaluationValue, ...]
PythonEvaluationCompressedTrace = tuple[tuple[tuple[int, DomainAtom], ...], PythonEvaluationOutputSignature]
PythonExtractGroupKey = tuple[str, clingo.Symbol]
PYTHON_EVAL_LEAF = object()


@dataclass(frozen=True, slots=True)
class PythonEvaluationLeaf:
    """Leaf node of one compressed Python evaluation trie."""

    outputs: PythonEvaluationOutputSignature


@dataclass(frozen=True, slots=True)
class PythonEvaluationNode:
    """Interior node of one compressed Python evaluation trie."""

    index: int
    branches: tuple[tuple[DomainAtom, PythonEvaluationLeaf | PythonEvaluationNode], ...]


@dataclass(slots=True)
class PythonEvaluationCollector(PythonEvaluationSession):
    """Collect and export Python traces for the expression currently being evaluated."""

    python_evaluations: list[PythonEvaluationAtom]
    python_evaluation_inputs: list[PythonEvaluationInputAtom]
    python_evaluation_outputs: list[PythonEvaluationOutputAtom]
    current_expr: clingo.Symbol | None = None
    current_group_exprs: tuple[clingo.Symbol, ...] = ()
    current_arg_exprs: tuple[clingo.Symbol, ...] = ()
    current_arg_domains: list[Domain] | None = None
    current_is_extract: bool = False
    current_output_requests: tuple[PythonEvaluationOutputRequest, ...] = ()
    current_outputs_by_expr: (
        dict[clingo.Symbol, dict[PythonEvaluationAssignment, PythonEvaluationOutputSignature]] | None
    ) = None
    current_domains_by_expr: dict[clingo.Symbol, Domain] | None = None

    def start_expression(
        self,
        expr: clingo.Symbol,
        expression_domains: Mapping[clingo.Symbol, Domain],
        grouped_exprs: tuple[clingo.Symbol, ...] | None = None,
    ) -> None:
        """Prepare trace metadata for one expression before evaluation starts."""
        self.finish_expression()
        self.current_expr = None
        self.current_group_exprs = ()
        self.current_arg_exprs = ()
        self.current_arg_domains = None
        self.current_is_extract = False
        self.current_output_requests = ()
        self.current_outputs_by_expr = None
        self.current_domains_by_expr = None

        if DomainComputation.is_function(expr, "python", 1):
            self.current_expr = expr
            self.current_group_exprs = (expr,)
            self.current_arg_domains = []
            self.current_output_requests = (PythonEvaluationOutputRequest(expr),)
            self.current_outputs_by_expr = {expr: {}}
            self.current_domains_by_expr = {expr: Domain.empty()}
            return

        if not DomainComputation.is_function(expr, "operation", 2):
            return

        operator, raw_args = expr.arguments
        is_extract = DomainComputation.is_function(operator, "pythonExtract", 2)
        if not (DomainComputation.is_function(operator, "python", 1) or is_extract):
            return

        arg_exprs = DomainComputation.sequence_items(raw_args)
        group_exprs = tuple(grouped_exprs or (expr,))
        self.current_expr = expr
        self.current_group_exprs = group_exprs
        self.current_arg_exprs = () if arg_exprs is None else tuple(arg_exprs)
        self.current_arg_domains = (
            [] if arg_exprs is None else [expression_domains.get(arg_expr, Domain.empty()) for arg_expr in arg_exprs]
        )
        self.current_is_extract = is_extract
        if is_extract:
            self.current_output_requests = tuple(
                PythonEvaluationOutputRequest(group_expr, DomainComputation.python_extract_output_code(group_expr))
                for group_expr in group_exprs
            )
        else:
            self.current_output_requests = (PythonEvaluationOutputRequest(expr),)
        self.current_outputs_by_expr = {group_expr: {} for group_expr in group_exprs}
        self.current_domains_by_expr = {group_expr: Domain.empty() for group_expr in group_exprs}

    def output_requests(self) -> tuple[PythonEvaluationOutputRequest, ...]:
        """Return the outputs requested for the currently active expression family."""
        return self.current_output_requests

    def record_output(
        self,
        output_id: object,
        arg_values: tuple[DomainAtom, ...],
        assignment_domain: Domain,
        error_messages: tuple[str, ...],
    ) -> None:
        """Record one concrete Python evaluation for the current expression."""
        if self.current_outputs_by_expr is None or self.current_domains_by_expr is None:
            raise AssertionError("python evaluation emitted without active trace context")
        if not isinstance(output_id, clingo.Symbol):
            raise AssertionError(f"python evaluation emitted for unexpected output id: {output_id!r}")
        if output_id not in self.current_outputs_by_expr:
            raise AssertionError(f"python evaluation emitted for unknown output expression: {output_id!r}")
        self.current_domains_by_expr[output_id].absorb(assignment_domain)
        self.current_outputs_by_expr[output_id][arg_values] = self.python_trace_signature(
            assignment_domain,
            error_messages,
        )

    def finish_expression(self) -> dict[clingo.Symbol, Domain]:
        """Flush the current expression trace into the exported trace lists."""
        if (
            self.current_outputs_by_expr is None
            or self.current_arg_domains is None
            or self.current_domains_by_expr is None
        ):
            return {}
        for expr, outputs_by_assignment in self.current_outputs_by_expr.items():
            self.record_python_evaluation(
                expr,
                self.current_arg_exprs,
                self.current_arg_domains,
                outputs_by_assignment,
                self.python_evaluations,
                self.python_evaluation_inputs,
                self.python_evaluation_outputs,
                is_extract=self.current_is_extract,
            )
        domains_by_expr = self.current_domains_by_expr
        self.current_expr = None
        self.current_group_exprs = ()
        self.current_arg_exprs = ()
        self.current_arg_domains = None
        self.current_is_extract = False
        self.current_output_requests = ()
        self.current_outputs_by_expr = None
        self.current_domains_by_expr = None
        return domains_by_expr

    @classmethod
    def python_trace_signature(
        cls,
        domain: Domain,
        error_messages: Iterable[str] = (),
    ) -> PythonEvaluationOutputSignature:
        """Return one stable trace signature including warning outputs when present."""
        outputs: list[PythonEvaluationValue] = [cls.python_error_output(message) for message in error_messages]
        outputs.extend(domain.values(include_bad=True))
        return tuple(sorted(outputs, key=str))

    @classmethod
    def python_error_output(cls, message: str) -> PythonWarningOutput:
        """Return the exported `error(expression(pythonError), Message)` symbol."""
        return PythonWarningOutput(
            clingo.Function(
                "error",
                [
                    clingo.Function("expression", [clingo.Function("pythonError")]),
                    clingo.String(message),
                ],
            )
        )

    @classmethod
    def python_evaluation_trie(
        cls,
        outputs_by_assignment: dict[PythonEvaluationAssignment, PythonEvaluationOutputSignature],
    ) -> dict[Any, Any]:
        """Build a trie over concrete Python argument tuples."""
        trie: dict[Any, Any] = {}
        for arg_values, output_signature in outputs_by_assignment.items():
            node = trie
            for value in arg_values:
                node = node.setdefault(value, {})
            node[PYTHON_EVAL_LEAF] = output_signature
        return trie

    @classmethod
    def compress_python_evaluation_trie(
        cls,
        trie: dict[Any, Any],
        ordered_domains: tuple[tuple[DomainAtom, ...], ...],
        depth: int = 0,
    ) -> PythonEvaluationLeaf | PythonEvaluationNode:
        """Collapse trie levels when every value in one argument domain shares the same subtree."""
        if depth == len(ordered_domains):
            return PythonEvaluationLeaf(trie[PYTHON_EVAL_LEAF])

        branches = tuple(
            (value, cls.compress_python_evaluation_trie(trie[value], ordered_domains, depth + 1))
            for value in ordered_domains[depth]
        )
        first_child = branches[0][1]
        if all(child == first_child for _, child in branches[1:]):
            return first_child
        return PythonEvaluationNode(depth, branches)

    @classmethod
    def compressed_python_evaluations(
        cls,
        arg_domains: list[Domain],
        outputs_by_assignment: dict[PythonEvaluationAssignment, PythonEvaluationOutputSignature],
    ) -> list[PythonEvaluationCompressedTrace]:
        """Return wildcard-safe Python evaluation traces that still cover the full input product."""
        if not outputs_by_assignment:
            return []

        ordered_domains = tuple(domain.options() for domain in arg_domains)
        tree = cls.compress_python_evaluation_trie(cls.python_evaluation_trie(outputs_by_assignment), ordered_domains)
        compressed: list[PythonEvaluationCompressedTrace] = []

        def collect(
            node: PythonEvaluationLeaf | PythonEvaluationNode,
            bindings: tuple[tuple[int, DomainAtom], ...],
        ) -> None:
            if isinstance(node, PythonEvaluationLeaf):
                compressed.append((bindings, node.outputs))
                return
            for value, child in node.branches:
                collect(child, bindings + ((node.index, value),))

        collect(tree, ())
        return compressed

    @classmethod
    def record_python_evaluation(
        cls,
        expr: clingo.Symbol,
        arg_exprs: tuple[clingo.Symbol, ...],
        arg_domains: list[Domain],
        outputs_by_assignment: dict[PythonEvaluationAssignment, PythonEvaluationOutputSignature],
        python_evaluations: list[PythonEvaluationAtom],
        python_evaluation_inputs: list[PythonEvaluationInputAtom],
        python_evaluation_outputs: list[PythonEvaluationOutputAtom],
        *,
        is_extract: bool,
    ) -> None:
        """Compress and record one family of Python input/output traces."""
        for uid, (bindings, output_signature) in enumerate(
            cls.compressed_python_evaluations(arg_domains, outputs_by_assignment)
        ):
            python_evaluations.append((expr, uid))
            for index, arg_value in bindings:
                arg_expr = arg_exprs[index]
                if (
                    is_extract
                    and DomainComputation.is_tuple(arg_expr, 2)
                    and isinstance(arg_value, tuple)
                    and len(arg_value) == 2
                ):
                    python_evaluation_inputs.append((expr, uid, arg_expr.arguments[1], arg_value[1]))
                    continue
                python_evaluation_inputs.append((expr, uid, arg_expr, arg_value))
            for output_value in output_signature:
                python_evaluation_outputs.append((expr, uid, output_value))


@dataclass(slots=True)
class ComputedDomains:
    """Cached compile2 domain-computation outputs for one grounding run."""

    expression_domains: dict[clingo.Symbol, Domain]
    set_expressions: set[clingo.Symbol]
    global_set_uids: dict[frozenset[DomainAtom], int]
    python_evaluations: list[PythonEvaluationAtom]
    python_evaluation_inputs: list[PythonEvaluationInputAtom]
    python_evaluation_outputs: list[PythonEvaluationOutputAtom]

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
                domain.domain_atoms,
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

    def python_evaluation_symbols(self) -> Iterable[clingo.Symbol]:
        """Yield `_python_evaluation/2` tuples for all computed Python traces."""
        for expr, uid in self.python_evaluations:
            yield clingo.Tuple_([expr, clingo.Number(uid)])

    def python_evaluation_input_symbols(self) -> Iterable[clingo.Symbol]:
        """Yield `_python_evaluation_input/4` tuples for all computed Python traces."""
        for expr, uid, arg_expr, arg_value in self.python_evaluation_inputs:
            yield clingo.Tuple_(
                [
                    expr,
                    clingo.Number(uid),
                    arg_expr,
                    self.python_value_reference_symbol(arg_value),
                ]
            )

    def python_evaluation_output_symbols(self) -> Iterable[clingo.Symbol]:
        """Yield `_python_evaluation_output/3` tuples for all computed Python traces."""
        for expr, uid, output_value in self.python_evaluation_outputs:
            yield clingo.Tuple_(
                [
                    expr,
                    clingo.Number(uid),
                    self.python_value_reference_symbol(output_value),
                ]
            )

    def python_value_reference_symbol(self, value: PythonEvaluationValue) -> clingo.Symbol:
        """Return one export symbol for a Python trace value or set reference."""
        if isinstance(value, PythonWarningOutput):
            return value.symbol
        if isinstance(value, frozenset):
            return clingo.Number(self.global_set_uids[value])
        return Domain.value_to_symbol(value)


class DomainComputation:
    """Compute compile2 expression domains directly from raw clingo symbols."""

    VARIABLE_SOURCE_NAMES: ClassVar[frozenset[str]] = frozenset(
        {
            "variable_define",
            "variable_domain",
            "set_assign",
            "set_baseDomain",
        }
    )

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
    def python_extract_group_key(cls, expr: clingo.Symbol) -> PythonExtractGroupKey | None:
        """Return the grouping key for PythonExtract expressions that share one statement execution."""
        if not cls.is_function(expr, "operation", 2):
            return None
        operator, raw_args = expr.arguments
        if not cls.is_function(operator, "pythonExtract", 2):
            return None
        return operator.arguments[0].string, raw_args

    @classmethod
    def python_extract_output_code(cls, expr: clingo.Symbol) -> str | None:
        """Return the PythonExtract output expression code for one operation symbol."""
        if not cls.is_function(expr, "operation", 2):
            return None
        operator = expr.arguments[0]
        if not cls.is_function(operator, "pythonExtract", 2):
            return None
        return operator.arguments[1].string

    @classmethod
    def group_python_extract_expressions(
        cls,
        ordered_expressions: tuple[clingo.Symbol, ...],
    ) -> tuple[dict[clingo.Symbol, tuple[clingo.Symbol, ...]], set[clingo.Symbol]]:
        """Return representative PythonExtract groups and the redundant members to skip in the main loop."""
        grouped: dict[PythonExtractGroupKey, list[clingo.Symbol]] = {}
        for expr in ordered_expressions:
            group_key = cls.python_extract_group_key(expr)
            if group_key is None:
                continue
            grouped.setdefault(group_key, []).append(expr)
        representative_groups: dict[clingo.Symbol, tuple[clingo.Symbol, ...]] = {}
        skipped_exprs: set[clingo.Symbol] = set()
        for group_exprs in grouped.values():
            representative_groups[group_exprs[0]] = tuple(group_exprs)
            skipped_exprs.update(group_exprs[1:])
        return representative_groups, skipped_exprs

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
    def evaluate_tuple(cls, expr: clingo.Symbol, expression_domains: Mapping[clingo.Symbol, Domain]) -> Domain:
        """Enumerate tuple values from already-computed child domains."""
        child_domains = [expression_domains.get(child, Domain.empty()) for child in expr.arguments]
        child_options = [domain.options() for domain in child_domains]
        if any(not options for options in child_options):
            return Domain.empty()
        tuple_values = {values for values in product(*child_options)}
        return Domain.tuple_values(*tuple_values)

    @classmethod
    def concrete_set_domain(
        cls,
        var: clingo.Symbol,
        expression_domains: Mapping[clingo.Symbol, Domain],
        set_sources: Mapping[clingo.Symbol, dict[str, list[clingo.Symbol]]],
    ) -> Domain | None:
        """Build the set-valued domain implied by one set variable and its sources."""
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
        if not required_scalars and not required_set_options:
            return Domain.all_subsets(*optional_candidates)
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
            return Domain.set_values(*concrete_sets)

    @classmethod
    def evaluate_expression(
        cls,
        expr: clingo.Symbol,
        expression_domains: Mapping[clingo.Symbol, Domain],
        solver_identifiers: tuple[clingo.Symbol, ...],
        evaluation_session: PythonEvaluationSession,
        grouped_exprs: tuple[clingo.Symbol, ...] | None = None,
    ) -> dict[clingo.Symbol, Domain]:
        """Evaluate one raw compile2 expression symbol into one or more expression domains."""
        evaluation_session.start_expression(expr, expression_domains, grouped_exprs)
        if cls.is_function(expr, "bad", 0):
            domain = Domain.bad()
        elif cls.is_function(expr, "val", 2):
            domain = Domain.from_symbol(expr)
        elif cls.is_function(expr, "python", 1):
            domain = Domain.evaluate_python_expression(
                expr.arguments[0].string,
                solver_identifiers,
                evaluation_session=evaluation_session,
            )
        elif cls.is_function(expr, "operation", 2):
            operator, raw_args = expr.arguments
            arg_exprs = cls.sequence_items(raw_args)
            if arg_exprs is None:
                domain = Domain.bad()
            else:
                arg_domains = [expression_domains.get(arg_expr, Domain.empty()) for arg_expr in arg_exprs]
                domain = Domain.compute_domain(
                    operator,
                    *arg_domains,
                    solver_identifiers=solver_identifiers,
                    evaluation_session=evaluation_session,
                )
        elif cls.is_tuple(expr) and cls.sequence_items(expr) is None:
            domain = cls.evaluate_tuple(expr, expression_domains)
        elif cls.is_function(expr, "variable", 1):
            domain = expression_domains.get(expr, Domain.empty())
        else:
            domain = Domain.symbols_only(expr)

        collected_domains = evaluation_session.finish_expression()
        if collected_domains:
            return collected_domains
        return {expr: domain}

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
                    if cls.is_function(expr, arity=2)
                    and expr.name in cls.VARIABLE_SOURCE_NAMES
                    and expr.arguments[0] == var
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
            children = (
                [expr.arguments[1]]
                if expr.name in cls.VARIABLE_SOURCE_NAMES and len(expr.arguments) == 2
                else cls.direct_subexpressions(expr)
            )
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
        Domain.GLOBAL_SET_UIDS.clear()
        Domain.NEXT_SET_UID = 0
        solver_identifier_key = cls.normalize_solver_identifiers(solver_identifiers)
        variable_sources, set_sources = cls.source_maps(expressions)
        ordered_expressions = tuple(cls.sorted_expressions(expressions))
        python_extract_groups, skipped_python_extract_exprs = cls.group_python_extract_expressions(ordered_expressions)
        expression_domains: dict[clingo.Symbol, Domain] = {}
        set_expressions: set[clingo.Symbol] = set()
        python_evaluations: list[PythonEvaluationAtom] = []
        python_evaluation_inputs: list[PythonEvaluationInputAtom] = []
        python_evaluation_outputs: list[PythonEvaluationOutputAtom] = []
        python_evaluation_collector = PythonEvaluationCollector(
            python_evaluations,
            python_evaluation_inputs,
            python_evaluation_outputs,
        )

        for expr in ordered_expressions:
            if expr in skipped_python_extract_exprs:
                continue
            if cls.is_function(expr, arity=2) and expr.name in cls.VARIABLE_SOURCE_NAMES:
                continue
            if cls.is_function(expr, "variable", 1):
                ### extend variable domains
                var = expr.arguments[0]
                domain = Domain.empty()
                for source_expr in variable_sources.get(var, []):
                    domain.absorb(expression_domains.get(source_expr, Domain.empty()))
                set_domain = cls.concrete_set_domain(var, expression_domains, set_sources)
                if set_domain is not None:
                    domain.absorb(set_domain)
                expression_domains[expr] = domain
                computed_exprs = (expr,)
            else:
                ### compute expression domains
                computed_domains = cls.evaluate_expression(
                    expr,
                    expression_domains,
                    solver_identifier_key,
                    python_evaluation_collector,
                    python_extract_groups.get(expr),
                )
                expression_domains.update(computed_domains)
                computed_exprs = tuple(computed_domains)
            for computed_expr in computed_exprs:
                if expression_domains[computed_expr].sets or (
                    cls.is_function(computed_expr, "variable", 1) and computed_expr.arguments[0] in set_sources
                ):
                    ### mark set-valued expressions for later export
                    set_expressions.add(computed_expr)
                    expression_domains[computed_expr].set_uids
        return ComputedDomains(
            expression_domains=expression_domains,
            set_expressions=set_expressions,
            global_set_uids=Domain.GLOBAL_SET_UIDS,
            python_evaluations=python_evaluations,
            python_evaluation_inputs=python_evaluation_inputs,
            python_evaluation_outputs=python_evaluation_outputs,
        )
