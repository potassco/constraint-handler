from __future__ import annotations

import csv
from dataclasses import dataclass, field
from functools import cache
from itertools import product
from math import prod
from pathlib import Path
from time import perf_counter
from typing import Any, Callable, ClassVar, Iterable, Mapping

import clingo

from constraint_handler.utils.python_domain import (
    Domain,
    DomainAtom,
    PythonEvaluationOutputRequest,
    PythonEvaluationSession,
    cached_function,
    cached_number,
    cached_tuple,
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


@dataclass(frozen=True, slots=True)
class PythonEvaluationCompressedTrace:
    """One wildcard-compressed Python trace for a family of input assignments."""

    bindings: tuple[tuple[int, DomainAtom], ...]
    outputs: PythonEvaluationOutputSignature


@dataclass(frozen=True, slots=True)
class CachedPythonEvaluation:
    """Cached domain plus compressed trace bundle for one Python output request."""

    expr_code: str | None
    domain: Domain
    traces: tuple[PythonEvaluationCompressedTrace, ...]


CachedPythonEvaluations = tuple[CachedPythonEvaluation, ...]
PythonExtractGroupKey = tuple[str, clingo.Symbol]
SetMembershipExportRequest = tuple[frozenset[DomainAtom], frozenset[DomainAtom]]
PYTHON_EVAL_LEAF = object()
DEBUG_EXPR_CSV_PATH = Path("/home/ostrowski/work/potassco/constraint-handler/debug_expr.csv")
DEBUG_CSV_PATH = Path("/home/ostrowski/work/potassco/constraint-handler/debug.csv")
DEBUG_EXPORT_COLUMNS = (
    "python_evaluation_output_symbols",
    "python_evaluation_input_symbols",
    "python_evaluation_symbols",
    "set_expressions",
    "expression_set_domain_value_symbols",
    "expression_set_domain_symbols",
    "expression_domain_symbols",
)
ENABLE_DEBUG = False


@dataclass(slots=True)
class ExportDebugProfiler:
    """Accumulate export timings and rewrite the aggregate CSV after each update."""

    output_path: Path = DEBUG_CSV_PATH
    timings: dict[str, float] = field(default_factory=dict)
    calls: dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if ENABLE_DEBUG:
            self.timings = {name: 0.0 for name in DEBUG_EXPORT_COLUMNS}
            self.calls = {name: 0 for name in DEBUG_EXPORT_COLUMNS}
            self._write()

    def record(self, name: str, elapsed_seconds: float) -> None:
        """Add one timing sample and persist the updated aggregates immediately."""
        if ENABLE_DEBUG:
            self.timings[name] = self.timings.get(name, 0.0) + elapsed_seconds
            self.calls[name] = self.calls.get(name, 0) + 1
            self._write()

    def _write(self) -> None:
        """Write the current aggregate timings to the debug CSV."""
        if ENABLE_DEBUG:
            total_seconds = sum(self.timings.values())
            total_calls = sum(self.calls.values())
            with self.output_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(["name", "seconds", "calls"])
                for name in DEBUG_EXPORT_COLUMNS:
                    writer.writerow([name, f"{self.timings[name]:.9f}", self.calls[name]])
                writer.writerow(["total", f"{total_seconds:.9f}", total_calls])
                handle.flush()


@dataclass(slots=True)
class ExpressionDebugLogger:
    """Stream per-expression compute timings to CSV as domains are derived."""

    output_path: Path = DEBUG_EXPR_CSV_PATH
    _handle: Any = field(init=False, repr=False)
    _writer: Any = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if ENABLE_DEBUG:
            self._handle = self.output_path.open("w", newline="", encoding="utf-8")
            self._writer = csv.writer(self._handle)
            self._writer.writerow(
                [
                    "expression_number",
                    "expression_total",
                    "expression",
                    "seconds",
                    "input_domain_formula",
                    "input_domain_formula_result",
                    "computed_domain_size",
                ]
            )
            self._handle.flush()

    def log(
        self,
        expression_number: int,
        expression_total: int,
        expr: clingo.Symbol,
        elapsed_seconds: float,
        formula: str,
        formula_result: int,
        computed_domain_size: int,
    ) -> None:
        """Append one timing row and flush it immediately."""
        if ENABLE_DEBUG:
            self._writer.writerow(
                [
                    expression_number,
                    expression_total,
                    str(expr),
                    f"{elapsed_seconds:.9f}",
                    formula,
                    formula_result,
                    computed_domain_size,
                ]
            )
            self._handle.flush()

    def close(self) -> None:
        """Close the CSV handle once the compute pass is complete."""
        if ENABLE_DEBUG:
            self._handle.close()


@dataclass(frozen=True, slots=True)
class PythonEvaluationLeaf:
    """Leaf node of one compressed Python evaluation trie."""

    outputs: PythonEvaluationOutputSignature


@dataclass(frozen=True, slots=True)
class PythonEvaluationNode:
    """Interior node of one compressed Python evaluation trie."""

    index: int
    branches: tuple[tuple[DomainAtom, PythonEvaluationLeaf | PythonEvaluationNode], ...]


def python_error_output(message: str) -> PythonWarningOutput:
    """Return the exported `error(expression(pythonError), Message)` symbol."""
    return PythonWarningOutput(
        cached_function(
            "error",
            (
                cached_function("expression", (cached_function("pythonError"),)),
                clingo.String(message),
            ),
        )
    )


def python_trace_signature(
    domain: Domain,
    error_messages: Iterable[str] = (),
) -> PythonEvaluationOutputSignature:
    """Return one stable trace signature including warning outputs when present."""
    outputs: list[PythonEvaluationValue] = [python_error_output(message) for message in error_messages]
    outputs.extend(domain.values(include_bad=True))
    return tuple(sorted(outputs, key=str))


def python_evaluation_trie(
    outputs_by_assignment: Mapping[PythonEvaluationAssignment, PythonEvaluationOutputSignature],
) -> dict[Any, Any]:
    """Build a trie over concrete Python argument tuples."""
    trie: dict[Any, Any] = {}
    for arg_values, output_signature in outputs_by_assignment.items():
        node = trie
        for value in arg_values:
            node = node.setdefault(value, {})
        node[PYTHON_EVAL_LEAF] = output_signature
    return trie


def compress_python_evaluation_trie(
    trie: dict[Any, Any],
    ordered_domains: tuple[tuple[DomainAtom, ...], ...],
    depth: int = 0,
) -> PythonEvaluationLeaf | PythonEvaluationNode:
    """Collapse trie levels when every value in one argument domain shares the same subtree."""
    if depth == len(ordered_domains):
        return PythonEvaluationLeaf(trie[PYTHON_EVAL_LEAF])

    branches = tuple(
        (value, compress_python_evaluation_trie(trie[value], ordered_domains, depth + 1))
        for value in ordered_domains[depth]
    )
    first_child = branches[0][1]
    if all(child == first_child for _, child in branches[1:]):
        return first_child
    return PythonEvaluationNode(depth, branches)


def compressed_python_evaluations(
    arg_domains: tuple[Domain, ...],
    outputs_by_assignment: Mapping[PythonEvaluationAssignment, PythonEvaluationOutputSignature],
) -> tuple[PythonEvaluationCompressedTrace, ...]:
    """Return wildcard-safe Python evaluation traces that still cover the full input product."""
    if not outputs_by_assignment:
        return ()

    ordered_domains = tuple(domain.options() for domain in arg_domains)
    tree = compress_python_evaluation_trie(python_evaluation_trie(outputs_by_assignment), ordered_domains)
    compressed: list[PythonEvaluationCompressedTrace] = []

    def collect(
        node: PythonEvaluationLeaf | PythonEvaluationNode,
        bindings: tuple[tuple[int, DomainAtom], ...],
    ) -> None:
        if isinstance(node, PythonEvaluationLeaf):
            compressed.append(PythonEvaluationCompressedTrace(bindings, node.outputs))
            return
        for value, child in node.branches:
            collect(child, bindings + ((node.index, value),))

    collect(tree, ())
    return tuple(compressed)


def record_compressed_python_evaluation(
    expr: clingo.Symbol,
    arg_exprs: tuple[clingo.Symbol, ...],
    compressed_evaluations: tuple[PythonEvaluationCompressedTrace, ...],
    python_evaluations: list[PythonEvaluationAtom],
    python_evaluation_inputs: list[PythonEvaluationInputAtom],
    python_evaluation_outputs: list[PythonEvaluationOutputAtom],
    *,
    is_extract: bool,
) -> None:
    """Record one already-compressed family of Python input/output traces."""
    for uid, trace in enumerate(compressed_evaluations):
        python_evaluations.append((expr, uid))
        for index, arg_value in trace.bindings:
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
        for output_value in trace.outputs:
            python_evaluation_outputs.append((expr, uid, output_value))


@dataclass(slots=True)
class PythonEvaluationExporter:
    """Export cached Python traces into compile2 python-evaluation atoms."""

    python_evaluations: list[PythonEvaluationAtom]
    python_evaluation_inputs: list[PythonEvaluationInputAtom]
    python_evaluation_outputs: list[PythonEvaluationOutputAtom]

    def replay_cached_evaluation(
        self,
        expr: clingo.Symbol,
        arg_exprs: tuple[clingo.Symbol, ...],
        compressed_evaluations: tuple[PythonEvaluationCompressedTrace, ...],
        *,
        is_extract: bool,
    ) -> None:
        """Append one cached compressed Python trace bundle to the exported lists."""
        record_compressed_python_evaluation(
            expr,
            arg_exprs,
            compressed_evaluations,
            self.python_evaluations,
            self.python_evaluation_inputs,
            self.python_evaluation_outputs,
            is_extract=is_extract,
        )


@dataclass(slots=True)
class PythonEvaluationCapture(PythonEvaluationSession):
    """Capture reusable Python traces without binding them to compile2 expression ids."""

    requests: tuple[PythonEvaluationOutputRequest, ...]
    outputs_by_id: dict[object, dict[PythonEvaluationAssignment, PythonEvaluationOutputSignature]] = field(
        default_factory=dict
    )
    domains_by_id: dict[object, Domain] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.outputs_by_id = {request.output_id: {} for request in self.requests}
        self.domains_by_id = {request.output_id: Domain.empty() for request in self.requests}

    def output_requests(self) -> tuple[PythonEvaluationOutputRequest, ...]:
        """Return the requested reusable outputs for the current Python evaluation."""
        return self.requests

    def record_output(
        self,
        output_id: object,
        arg_values: tuple[DomainAtom, ...],
        assignment_domain: Domain,
        error_messages: tuple[str, ...],
    ) -> None:
        """Store one expression-independent Python output trace."""
        self.domains_by_id[output_id] = Domain.merge(self.domains_by_id[output_id], assignment_domain)
        self.outputs_by_id[output_id][arg_values] = python_trace_signature(
            assignment_domain,
            error_messages,
        )

    def compressed_results(self, arg_domains: tuple[Domain, ...]) -> CachedPythonEvaluations:
        """Return cached domains plus compressed traces keyed only by output code."""
        return tuple(
            CachedPythonEvaluation(
                request.expr_code,
                self.domains_by_id[request.output_id],
                compressed_python_evaluations(
                    arg_domains,
                    self.outputs_by_id[request.output_id],
                ),
            )
            for request in self.requests
        )


@dataclass(slots=True)
class ComputedDomains:
    """Cached compile2 domain-computation outputs for one grounding run."""

    expression_domains: dict[clingo.Symbol, Domain]
    set_expressions: set[clingo.Symbol]
    global_set_uids: dict[frozenset[DomainAtom], int]
    python_evaluations: list[PythonEvaluationAtom]
    python_evaluation_inputs: list[PythonEvaluationInputAtom]
    python_evaluation_outputs: list[PythonEvaluationOutputAtom]
    set_membership_export_requests: tuple[SetMembershipExportRequest, ...]
    export_debug_profiler: ExportDebugProfiler

    def expression_domain_symbols(self) -> Iterable[clingo.Symbol]:
        """Yield `_se_domain/2` facts for all computed expressions."""
        start = perf_counter()
        try:
            for expr, domain in sorted(self.expression_domains.items()):
                yield from domain.expression_domain_symbols(
                    expr,
                    include_set_values=expr not in self.set_expressions,
                )
        finally:
            self.export_debug_profiler.record("expression_domain_symbols", perf_counter() - start)

    def expression_set_domain_symbols(self) -> Iterable[clingo.Symbol]:
        """Yield `_se_set_domain(Expr,Uid)` facts for all computed expressions."""
        start = perf_counter()
        try:
            for expr, domain in sorted(self.expression_domains.items()):
                yield from domain.expression_set_domain_symbols(expr, self.global_set_uids)
        finally:
            self.export_debug_profiler.record("expression_set_domain_symbols", perf_counter() - start)

    def expression_set_domain_value_symbols(self) -> Iterable[clingo.Symbol]:
        """Yield `_se_set_domain(Uid,Sign,Value)` facts across all set expressions."""
        start = perf_counter()
        try:
            seen: set[clingo.Symbol] = set()
            for set_value, candidate_values in self.set_membership_export_requests:
                for symbol in Domain.set_value_domain_symbols(
                    set_value,
                    global_set_uids=self.global_set_uids,
                    candidate_values=candidate_values,
                ):
                    if symbol in seen:
                        continue
                    seen.add(symbol)
                    yield symbol
        finally:
            self.export_debug_profiler.record(
                "expression_set_domain_value_symbols",
                perf_counter() - start,
            )

    def expression_set_domain_symbol_symbols(self, expr: clingo.Symbol) -> Iterable[clingo.Symbol]:
        """Yield `(Uid,SetValue)` tuples for one set-valued expression."""
        domain = self.expression_domains.get(expr)
        if domain is None:
            return ()
        return domain.expression_set_domain_symbol_symbols(self.global_set_uids)

    def python_evaluation_symbols(self) -> Iterable[clingo.Symbol]:
        """Yield `_python_evaluation/2` tuples for all computed Python traces."""
        start = perf_counter()
        try:
            for expr, uid in self.python_evaluations:
                yield cached_tuple((expr, cached_number(uid)))
        finally:
            self.export_debug_profiler.record("python_evaluation_symbols", perf_counter() - start)

    def python_evaluation_input_symbols(self) -> Iterable[clingo.Symbol]:
        """Yield `_python_evaluation_input/4` tuples for all computed Python traces."""
        start = perf_counter()
        try:
            for expr, uid, arg_expr, arg_value in self.python_evaluation_inputs:
                yield cached_tuple(
                    (
                        expr,
                        cached_number(uid),
                        arg_expr,
                        self.python_value_reference_symbol(arg_value),
                    )
                )
        finally:
            self.export_debug_profiler.record("python_evaluation_input_symbols", perf_counter() - start)

    def python_evaluation_output_symbols(self) -> Iterable[clingo.Symbol]:
        """Yield `_python_evaluation_output/3` tuples for all computed Python traces."""
        start = perf_counter()
        try:
            for expr, uid, output_value in self.python_evaluation_outputs:
                yield cached_tuple(
                    (
                        expr,
                        cached_number(uid),
                        self.python_value_reference_symbol(output_value),
                    )
                )
        finally:
            self.export_debug_profiler.record("python_evaluation_output_symbols", perf_counter() - start)

    def set_expression_symbols(self) -> list[clingo.Symbol]:
        """Return the sorted set-valued expressions and time the export."""
        start = perf_counter()
        try:
            return sorted(self.set_expressions)
        finally:
            self.export_debug_profiler.record("set_expressions", perf_counter() - start)

    def python_value_reference_symbol(self, value: PythonEvaluationValue) -> clingo.Symbol:
        """Return one export symbol for a Python trace value or set reference."""
        if isinstance(value, PythonWarningOutput):
            return value.symbol
        if isinstance(value, frozenset):
            return cached_number(self.global_set_uids[value])
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
    def debug_input_domain_sizes(
        cls,
        expr: clingo.Symbol,
        expression_domains: Mapping[clingo.Symbol, Domain],
        variable_sources: Mapping[clingo.Symbol, list[clingo.Symbol]],
        set_sources: Mapping[clingo.Symbol, dict[str, list[clingo.Symbol]]],
    ) -> tuple[int, ...]:
        """Return the immediate input domain sizes used to derive one expression."""
        if cls.is_function(expr, "variable", 1):
            variable_name = expr.arguments[0]
            dependencies = list(variable_sources.get(variable_name, []))
            set_source_map = set_sources.get(variable_name, {})
            dependencies.extend(set_source_map.get("set_assign", []))
            dependencies.extend(set_source_map.get("set_baseDomain", []))
        else:
            dependencies = cls.direct_subexpressions(expr)
        return tuple(
            expression_domains.get(dependency, Domain.empty()).value_count(include_bad=True)
            for dependency in dependencies
        )

    @classmethod
    def debug_input_domain_formula(cls, input_sizes: tuple[int, ...]) -> tuple[str, int]:
        """Render a stable multiplicative formula for one expression's input sizes."""
        if not input_sizes:
            return "1", 1
        return "*".join(str(size) for size in input_sizes), prod(input_sizes)

    @classmethod
    def debug_expression_total(
        cls,
        ordered_expressions: tuple[clingo.Symbol, ...],
        skipped_python_extract_exprs: set[clingo.Symbol],
        python_extract_groups: Mapping[clingo.Symbol, tuple[clingo.Symbol, ...]],
    ) -> int:
        """Count the number of expression rows that will be written to the debug CSV."""
        total = 0
        for expr in ordered_expressions:
            if expr in skipped_python_extract_exprs:
                continue
            if cls.is_function(expr, arity=2) and expr.name in cls.VARIABLE_SOURCE_NAMES:
                continue
            if cls.is_function(expr, "variable", 1):
                total += 1
                continue
            grouped_exprs = python_extract_groups.get(expr)
            total += len(grouped_exprs) if grouped_exprs else 1
        return total

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
    def add_set_membership_export_request(
        cls,
        requests: set[SetMembershipExportRequest],
        expression_domains: Mapping[clingo.Symbol, Domain],
        reference_expr: clingo.Symbol,
        set_value: frozenset[DomainAtom],
    ) -> None:
        """Record one demanded `_se_set_domain/3` export for a referenced concrete set."""
        reference_domain = expression_domains.get(reference_expr)
        if reference_domain is None:
            return
        requests.add((set_value, frozenset(reference_domain.domain_atoms)))

    @classmethod
    def collect_python_set_membership_export_requests(
        cls,
        requests: set[SetMembershipExportRequest],
        expression_domains: Mapping[clingo.Symbol, Domain],
        python_evaluation_inputs: Iterable[PythonEvaluationInputAtom],
        python_evaluation_outputs: Iterable[PythonEvaluationOutputAtom],
    ) -> None:
        """Add set membership exports required by one batch of Python traces."""
        for _, _, arg_expr, arg_value in python_evaluation_inputs:
            if isinstance(arg_value, frozenset):
                cls.add_set_membership_export_request(requests, expression_domains, arg_expr, arg_value)

        for expr, _, output_value in python_evaluation_outputs:
            if isinstance(output_value, frozenset):
                cls.add_set_membership_export_request(requests, expression_domains, expr, output_value)

    @classmethod
    def collect_tuple_set_membership_export_requests(
        cls,
        requests: set[SetMembershipExportRequest],
        expression_domains: Mapping[clingo.Symbol, Domain],
        expr: clingo.Symbol,
    ) -> None:
        """Add set membership exports required by one literal tuple expression."""
        if not cls.is_tuple(expr) or cls.sequence_items(expr) is not None:
            return
        for child_expr in expr.arguments:
            child_domain = expression_domains.get(child_expr)
            if child_domain is None or not child_domain.has_possible_sets():
                continue
            for set_value in child_domain.sets:
                cls.add_set_membership_export_request(requests, expression_domains, child_expr, set_value)

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
        solver_identifiers: tuple[clingo.Symbol, ...],
    ) -> tuple[clingo.Symbol, ...]:
        """Flatten the `_main_solverIdentifiers/1` list term into evaluator identifiers."""
        if len(solver_identifiers) == 1:
            sequence = cls.sequence_items(solver_identifiers[0])
            if sequence is not None:
                return tuple(sequence)
        return solver_identifiers

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
        evaluation_session: PythonEvaluationExporter,
        cached_compute_domain: Callable[[clingo.Symbol, tuple[Domain, ...], tuple[clingo.Symbol, ...]], Domain],
        cached_python_expression_evaluation: Callable[[str, tuple[clingo.Symbol, ...]], CachedPythonEvaluations],
        cached_python_callable_evaluation: Callable[
            [str, tuple[Domain, ...], tuple[clingo.Symbol, ...]],
            CachedPythonEvaluations,
        ],
        cached_python_extract_evaluation: Callable[
            [str, tuple[Domain, ...], tuple[clingo.Symbol, ...], tuple[str, ...]],
            CachedPythonEvaluations,
        ],
        grouped_exprs: tuple[clingo.Symbol, ...] | None = None,
    ) -> dict[clingo.Symbol, Domain]:
        """Evaluate one raw compile2 expression symbol into one or more expression domains."""
        if cls.is_function(expr, "bad", 0):
            domain = Domain.bad()
        elif cls.is_function(expr, "val", 2):
            domain = Domain.from_symbol(expr)
        elif cls.is_function(expr, "python", 1):
            (cached_trace,) = cached_python_expression_evaluation(expr.arguments[0].string, solver_identifiers)
            domain = cached_trace.domain
            evaluation_session.replay_cached_evaluation(expr, (), cached_trace.traces, is_extract=False)
        elif cls.is_function(expr, "operation", 2):
            operator, raw_args = expr.arguments
            arg_exprs = cls.sequence_items(raw_args)
            if arg_exprs is None:
                domain = Domain.bad()
            else:
                arg_expr_tuple = tuple(arg_exprs)
                arg_domains = tuple(expression_domains.get(arg_expr, Domain.empty()) for arg_expr in arg_expr_tuple)
                if cls.is_function(operator, "python", 1):
                    (cached_trace,) = cached_python_callable_evaluation(
                        operator.arguments[0].string,
                        arg_domains,
                        solver_identifiers,
                    )
                    domain = cached_trace.domain
                    evaluation_session.replay_cached_evaluation(
                        expr,
                        arg_expr_tuple,
                        cached_trace.traces,
                        is_extract=False,
                    )
                    return {expr: domain}
                if cls.is_function(operator, "pythonExtract", 2):
                    output_codes = tuple(
                        code
                        for code in dict.fromkeys(
                            cls.python_extract_output_code(group_expr) for group_expr in tuple(grouped_exprs or (expr,))
                        )
                        if code is not None
                    )
                    cached_results = {
                        cached_trace.expr_code: cached_trace
                        for cached_trace in cached_python_extract_evaluation(
                            operator.arguments[0].string,
                            arg_domains,
                            solver_identifiers,
                            output_codes,
                        )
                    }
                    computed_domains: dict[clingo.Symbol, Domain] = {}
                    for group_expr in tuple(grouped_exprs or (expr,)):
                        output_code = cls.python_extract_output_code(group_expr)
                        if output_code is None:
                            continue
                        cached_trace = cached_results[output_code]
                        evaluation_session.replay_cached_evaluation(
                            group_expr,
                            arg_expr_tuple,
                            cached_trace.traces,
                            is_extract=True,
                        )
                        computed_domains[group_expr] = cached_trace.domain
                    return computed_domains
                domain = cached_compute_domain(operator, arg_domains, solver_identifiers)
        elif cls.is_tuple(expr) and cls.sequence_items(expr) is None:
            domain = cls.evaluate_tuple(expr, expression_domains)
        elif cls.is_function(expr, "variable", 1):
            domain = expression_domains.get(expr, Domain.empty())
        else:
            domain = Domain.symbols_only(expr)
        return {expr: domain}

    @classmethod
    def sorted_expressions(
        cls,
        top_level_expressions: Iterable[clingo.Symbol],
        variable_sources: Mapping[clingo.Symbol, list[clingo.Symbol]],
        set_sources: Mapping[clingo.Symbol, dict[str, list[clingo.Symbol]]],
    ) -> Iterable[clingo.Symbol]:
        """Yield expressions in a dependency-first order with variable sources expanded first."""
        expressions = set(top_level_expressions)
        seen: set[clingo.Symbol] = set()
        visiting: set[clingo.Symbol] = set()
        expanded_variables: set[clingo.Symbol] = set()

        def visit(expr: clingo.Symbol):
            if expr in seen or expr in visiting:
                return
            visiting.add(expr)
            if cls.is_function(expr, "variable", 1) and expr.arguments[0] not in expanded_variables:
                expanded_variables.add(expr.arguments[0])
                for dependency in variable_sources.get(expr.arguments[0], []):
                    yield from visit(dependency)
                for dependency in set_sources.get(expr.arguments[0], {}).get("set_assign", []):
                    yield from visit(dependency)
                for dependency in set_sources.get(expr.arguments[0], {}).get("set_baseDomain", []):
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
        solver_identifiers: tuple[clingo.Symbol, ...],
    ) -> ComputedDomains:
        """Compute compile2 expression domains and the derived set export metadata."""

        @cache
        def cached_compute_domain(
            operation: clingo.Symbol,
            domains: tuple[Domain, ...],
            solver_ids: tuple[clingo.Symbol, ...],
        ) -> Domain:
            return Domain.compute_domain(
                operation,
                *domains,
                solver_identifiers=solver_ids,
                evaluation_session=PythonEvaluationSession(),
            )

        @cache
        def cached_python_expression_evaluation(
            code: str,
            solver_ids: tuple[clingo.Symbol, ...],
        ) -> CachedPythonEvaluations:
            session = PythonEvaluationCapture((PythonEvaluationOutputRequest(),))
            Domain.evaluate_python_expression(code, solver_ids, evaluation_session=session)
            return session.compressed_results(())

        @cache
        def cached_python_callable_evaluation(
            code: str,
            domains: tuple[Domain, ...],
            solver_ids: tuple[clingo.Symbol, ...],
        ) -> CachedPythonEvaluations:
            session = PythonEvaluationCapture((PythonEvaluationOutputRequest(),))
            Domain.evaluate_python_callable(code, domains, solver_ids, evaluation_session=session)
            return session.compressed_results(domains)

        @cache
        def cached_python_extract_evaluation(
            stmt: str,
            domains: tuple[Domain, ...],
            solver_ids: tuple[clingo.Symbol, ...],
            output_codes: tuple[str, ...],
        ) -> CachedPythonEvaluations:
            session = PythonEvaluationCapture(
                tuple(PythonEvaluationOutputRequest(output_code, output_code) for output_code in output_codes)
            )
            Domain.evaluate_python_extract(
                stmt,
                output_codes[0],
                domains,
                solver_ids,
                evaluation_session=session,
            )
            return session.compressed_results(domains)

        expressions = set(top_level_expressions)
        Domain.GLOBAL_SET_UIDS.clear()
        Domain.NEXT_SET_UID = 0
        Domain.set_uids.fget.cache_clear()
        solver_identifier_key = cls.normalize_solver_identifiers(solver_identifiers)
        variable_sources, set_sources = cls.source_maps(expressions)
        ordered_expressions = tuple(cls.sorted_expressions(expressions, variable_sources, set_sources))
        python_extract_groups, skipped_python_extract_exprs = cls.group_python_extract_expressions(ordered_expressions)
        expression_domains: dict[clingo.Symbol, Domain] = {}
        set_expressions: set[clingo.Symbol] = set()
        python_evaluations: list[PythonEvaluationAtom] = []
        python_evaluation_inputs: list[PythonEvaluationInputAtom] = []
        python_evaluation_outputs: list[PythonEvaluationOutputAtom] = []
        set_membership_export_requests: set[SetMembershipExportRequest] = set()
        export_debug_profiler = ExportDebugProfiler()
        python_evaluation_exporter = PythonEvaluationExporter(
            python_evaluations,
            python_evaluation_inputs,
            python_evaluation_outputs,
        )
        debug_expression_total = cls.debug_expression_total(
            ordered_expressions,
            skipped_python_extract_exprs,
            python_extract_groups,
        )
        debug_expression_number = 0
        debug_logger = ExpressionDebugLogger()
        try:
            for expr in ordered_expressions:
                if expr in skipped_python_extract_exprs:
                    continue
                if cls.is_function(expr, arity=2) and expr.name in cls.VARIABLE_SOURCE_NAMES:
                    continue
                expr_start = perf_counter()
                if cls.is_function(expr, "variable", 1):
                    ### extend variable domains
                    var = expr.arguments[0]
                    domain_parts: list[Domain] = []
                    for source_expr in variable_sources.get(var, []):
                        domain_parts.append(expression_domains.get(source_expr, Domain.empty()))
                    set_domain = cls.concrete_set_domain(var, expression_domains, set_sources)
                    if set_domain is not None:
                        domain_parts.append(set_domain)
                    domain = Domain.merge(*domain_parts)
                    expression_domains[expr] = domain
                    computed_exprs = (expr,)
                else:
                    ### compute expression domains
                    input_start = len(python_evaluation_inputs)
                    output_start = len(python_evaluation_outputs)
                    computed_domains = cls.evaluate_expression(
                        expr,
                        expression_domains,
                        solver_identifier_key,
                        python_evaluation_exporter,
                        cached_compute_domain,
                        cached_python_expression_evaluation,
                        cached_python_callable_evaluation,
                        cached_python_extract_evaluation,
                        python_extract_groups.get(expr),
                    )
                    expression_domains.update(computed_domains)
                    cls.collect_python_set_membership_export_requests(
                        set_membership_export_requests,
                        expression_domains,
                        python_evaluation_inputs[input_start:],
                        python_evaluation_outputs[output_start:],
                    )
                    computed_exprs = tuple(computed_domains)
                elapsed_seconds = perf_counter() - expr_start
                for computed_expr in computed_exprs:
                    if expression_domains[computed_expr].sets or (
                        cls.is_function(computed_expr, "variable", 1) and computed_expr.arguments[0] in set_sources
                    ):
                        ### mark set-valued expressions for later export
                        set_expressions.add(computed_expr)
                        expression_domains[computed_expr].set_uids
                    cls.collect_tuple_set_membership_export_requests(
                        set_membership_export_requests,
                        expression_domains,
                        computed_expr,
                    )
                    input_sizes = cls.debug_input_domain_sizes(
                        computed_expr,
                        expression_domains,
                        variable_sources,
                        set_sources,
                    )
                    formula, formula_result = cls.debug_input_domain_formula(input_sizes)
                    debug_expression_number += 1
                    debug_logger.log(
                        debug_expression_number,
                        debug_expression_total,
                        computed_expr,
                        elapsed_seconds,
                        formula,
                        formula_result,
                        expression_domains[computed_expr].value_count(include_bad=True),
                    )
        finally:
            debug_logger.close()
        return ComputedDomains(
            expression_domains=expression_domains,
            set_expressions=set_expressions,
            global_set_uids=Domain.GLOBAL_SET_UIDS,
            python_evaluations=python_evaluations,
            python_evaluation_inputs=python_evaluation_inputs,
            python_evaluation_outputs=python_evaluation_outputs,
            set_membership_export_requests=tuple(
                sorted(
                    set_membership_export_requests,
                    key=lambda item: (
                        Domain.set_sort_key(item[0]),
                        tuple(sorted(item[1], key=Domain.set_uid_sort_key)),
                    ),
                )
            ),
            export_debug_profiler=export_debug_profiler,
        )
