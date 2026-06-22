_top_level_expression(E) :- _passed(compile2,LBL,DECL), DECL=bool_evaluate(E).
_top_level_expression(E) :- _passed(compile2,LBL,DECL), DECL=ensure(E).
_top_level_expression(operation(OP,ARGS)) :- _passed(compile2,LBL,DECL), DECL=evaluate(OP,ARGS).

%_top_level_expression((K;B)) :- _passed(compile2,LBL,DECL), DECL=multimap_assign(X,K,B).
_top_level_expression(E) :- _passed(compile2,LBL,DECL), DECL=optimize_maximizeSum(E,X,P).
_top_level_expression(E) :- _passed(compile2,LBL,DECL), DECL=optimize_precision(E,PRIO).
_top_level_expression(E) :- _passed(compile2,LBL,DECL), DECL=preference_holds(E,K).

_top_level_expression(E) :- _passed(compile2,LBL,DECL), DECL=variable_define(X,E).
_top_level_expression(E) :- _passed(compile2,LBL,DECL), DECL=variable_domain(X,E).
_top_level_expression(E) :- _passed(compile2,LBL,DECL), DECL=set_assign(X,E).
_top_level_expression(E) :- _passed(compile2,LBL,DECL), DECL=set_baseDomain(X,E).
_top_level_expression(operation(set_make,())) :- _passed(compile2,LBL,DECL), DECL=variable_declare(X,set).

_top_level_expression(variable_define(X,E)) :- _passed(compile2,LBL,DECL), DECL=variable_define(X,E).
_top_level_expression(variable_domain(X,E)) :- _passed(compile2,LBL,DECL), DECL=variable_domain(X,E).
_top_level_expression(set_assign(X,E)) :- _passed(compile2,LBL,DECL), DECL=set_assign(X,E).
_top_level_expression(set_baseDomain(X,E)) :- _passed(compile2,LBL,DECL), DECL=set_baseDomain(X,E).
_top_level_expression(set_baseDomain(X,operation(set_make,()))) :- _passed(compile2,LBL,DECL), DECL=variable_declare(X,set).

_top_level_expression(variable(X)) :- _passed(compile2,LBL,DECL), DECL=variable_define(X,E).
_top_level_expression(variable(X)) :- _passed(compile2,LBL,DECL), DECL=variable_domain(X,E).
_top_level_expression(variable(X)) :- _passed(compile2,LBL,DECL), DECL=variable_declare(X,set).
load_top_level_expressions :- _ = @loadTopLevelExpression(E), _top_level_expression(E).
load_solver_identifiers :- _ = @loadSolverIdentifiers(ID), _main_solverIdentifiers(ID).

_se_domain(Expr, Value) :- (Expr, Value) = @expressionDomain(), load_top_level_expressions, load_solver_identifiers.
_se_set_domain(Expr, Uid) :- (Expr, Uid) = @expressionSetDomain(), load_top_level_expressions, load_solver_identifiers.
_se_set_domain(Expr, Uid, Sign, Value) :- (Expr, Uid, Sign, Value) = @expressionSetDomainValue(), load_top_level_expressions, load_solver_identifiers.
_se_is_set(Expr) :- Expr = @expressionSet(), load_top_level_expressions, load_solver_identifiers.
_python_evaluation(Expr, Uid) :- (Expr, Uid) = @pythonEvaluation(), load_top_level_expressions, load_solver_identifiers.
_python_evaluation_input(PyExpr, Uid, ArgExpr, ArgVal) :-
    (PyExpr, Uid, ArgExpr, ArgVal) = @pythonEvaluationInput(),
    load_top_level_expressions,
    load_solver_identifiers.
_python_evaluation_output(PyExpr, Uid, OutputVal) :-
    (PyExpr, Uid, OutputVal) = @pythonEvaluationOutput(),
    load_top_level_expressions,
    load_solver_identifiers.

#script(python)
import itertools
from collections.abc import Iterable
from typing import Any, NamedTuple, TypeAlias

import clingo

import constraint_handler.arithmetic as arithmetic
import constraint_handler.evaluator as evaluator
import constraint_handler.logic as logic
import constraint_handler.multimap as multimap
import constraint_handler.myClorm as myClorm
import constraint_handler.schemas.operators as operators
import constraint_handler.schemas.warning as warning
import constraint_handler.set as set_ops
import constraint_handler.schemas.expression as expression


Expr: TypeAlias = expression.Expr | expression.constant
ReducedExpr: TypeAlias = expression.ReducedExpr
ExpressionDomains: TypeAlias = dict[Expr, set[ReducedExpr]]
ExpressionGraph: TypeAlias = dict[Expr, set[Expr]]
VariableSources: TypeAlias = dict[clingo.Symbol, set[Expr]]
SetCandidateDomains: TypeAlias = dict[Expr, set[ReducedExpr]]
SetVariableSources: TypeAlias = dict[clingo.Symbol, dict[str, set[Expr]]]
SetUidMaps: TypeAlias = dict[Expr, dict[frozenset[ReducedExpr], int]]
PythonEvaluationOutputTerm: TypeAlias = ReducedExpr
PythonEvaluationOutputValue: TypeAlias = PythonEvaluationOutputTerm | int
PythonEvaluationInputValue: TypeAlias = ReducedExpr | int
PythonEvaluationAtom: TypeAlias = tuple[Expr, int]
PythonEvaluationInputAtom: TypeAlias = tuple[Expr, int, Expr, PythonEvaluationInputValue]
PythonEvaluationOutputAtom: TypeAlias = tuple[Expr, int, PythonEvaluationOutputValue]
PythonEvaluationAssignment: TypeAlias = tuple[ReducedExpr, ...]
PythonEvaluationOutputSignature: TypeAlias = tuple[PythonEvaluationOutputTerm, ...]
PythonEvaluationCompressedTrace: TypeAlias = tuple[tuple[tuple[int, ReducedExpr], ...], PythonEvaluationOutputSignature]
PythonExtractExecution: TypeAlias = tuple[dict[str, Any] | None, list[tuple[warning.Kind, Any]], bool | None]
ClingoSymbolCache: TypeAlias = dict[Any, clingo.Symbol]


class DomainCache(NamedTuple):
    expression_domains: ExpressionDomains
    set_candidate_domains: SetCandidateDomains
    set_expressions: set[Expr]
    set_uid_maps: SetUidMaps
    python_evaluations: list[PythonEvaluationAtom]
    python_evaluation_inputs: list[PythonEvaluationInputAtom]
    python_evaluation_outputs: list[PythonEvaluationOutputAtom]


class PythonEvaluationLeaf(NamedTuple):
    outputs: PythonEvaluationOutputSignature


class PythonEvaluationNode(NamedTuple):
    index: int
    branches: tuple[tuple[ReducedExpr, Any], ...]


top_level_expressions: set[clingo.Symbol] = set()
solver_identifiers: tuple[expression.constant, ...] = ()
cached_domains: DomainCache | None = None
SET_DOMAIN_POS = clingo.Function("pos")
SET_DOMAIN_NEG = clingo.Function("neg")
PYTHON_EVAL_LEAF = object()

def _cached_pytocl(value: Any, cache: ClingoSymbolCache) -> clingo.Symbol:
    """Convert one hashable value to a clingo symbol once and reuse it."""
    try:
        cached = cache.get(value)
    except TypeError:
        return myClorm.pytocl(value)
    if cached is None:
        cached = myClorm.pytocl(value)
        cache[value] = cached
    return cached


def loadTopLevelExpression(cl_expr: clingo.Symbol) -> clingo.Symbol:
    """Collect a top-level compile2 expression symbol during grounding."""
    global cached_domains
    top_level_expressions.add(cl_expr)
    cached_domains = None
    return myClorm.pytocl(True)


def loadSolverIdentifiers(cl_ids: clingo.Symbol) -> clingo.Symbol:
    """Store solver-environment identifiers used for Python-backed evaluation."""
    global solver_identifiers, cached_domains
    solver_identifiers = tuple(myClorm.cltopy(cl_ids, list[expression.constant]))
    cached_domains = None
    return myClorm.pytocl(True)


def _direct_subexpressions(expr_: Expr) -> list[Expr]:
    """Return immediate child expressions used to build the dependency graph."""
    match expr_:
        case expression.Operation(op, args):
            result = list(args)
            if isinstance(op, (expression.Variable, expression.Operation, expression.Lambda)):
                result.insert(0, op)
            return result
        case (
            expression.Val(_, _)
            | expression.Variable(_)
            | expression.Python(_)
            | expression.PythonExtract(_, _)
            | expression.Bad.bad
        ):
            return []
        case expression.Lambda(_, body):
            return [body]
        case tuple(args) | frozenset(args):
            return list(args)
        case _:
            return []


def _is_scalar_expression(expr_: Expr) -> bool:
    """Check whether an expression leaf can be treated as a direct scalar value."""
    return isinstance(expr_, (bool, float, int, str, type(None), clingo.Symbol))


def _expand_expression(expr_: Expr, expressions: set[Expr]) -> None:
    """Recursively add an expression and all reachable subexpressions to a set."""
    if expr_ in expressions:
        return
    expressions.add(expr_)
    for subexpr in _direct_subexpressions(expr_):
        _expand_expression(subexpr, expressions)


def _unwrap_top_level_expression(cl_expr: clingo.Symbol) -> tuple[str | None, clingo.Symbol | None, Expr]:
    """Split variable-domain declarations from ordinary top-level expressions."""
    if cl_expr.type == clingo.SymbolType.Function and cl_expr.name in {
        "variable_define",
        "variable_domain",
        "set_assign",
        "set_baseDomain",
    } and len(cl_expr.arguments) == 2:
        return cl_expr.name, cl_expr.arguments[0], myClorm.cltopy(cl_expr.arguments[1], expression.Expr)
    return None, None, myClorm.cltopy(cl_expr, expression.Expr)


def _build_expression_graph() -> tuple[ExpressionGraph, VariableSources, SetVariableSources]:
    """Build expression dependencies and variable source mappings."""
    all_expressions: set[Expr] = set()
    variable_sources: VariableSources = {}
    set_sources: SetVariableSources = {}

    for cl_expr in top_level_expressions:
        kind, var, expr_ = _unwrap_top_level_expression(cl_expr)
        _expand_expression(expr_, all_expressions)
        if kind in {"variable_define", "variable_domain"}:
            variable_sources.setdefault(var, set()).add(expr_)
        if kind in {"set_assign", "set_baseDomain"}:
            source_bucket = set_sources.setdefault(var, {"set_assign": set(), "set_baseDomain": set()})
            source_bucket[kind].add(expr_)
            all_expressions.add(expression.Variable(var))

    graph = {expr_: set() for expr_ in all_expressions}
    for expr_ in all_expressions:
        graph[expr_].update(subexpr for subexpr in _direct_subexpressions(expr_) if subexpr in all_expressions)
        if isinstance(expr_, expression.Variable):
            graph[expr_].update(variable_sources.get(expr_.arg, set()))
            for sources in set_sources.get(expr_.arg, {}).values():
                graph[expr_].update(sources)

    return graph, variable_sources, set_sources


def _topological_order(graph: ExpressionGraph) -> Iterable[Expr]:
    """Return a stable dependency-first order over the expression graph."""
    visited: set[Expr] = set()

    def visit(node: Expr) -> Iterable[Expr]:
        if node in visited:
            return
        visited.add(node)
        for dep in sorted(graph[node], key=str):
            yield from visit(dep)
        yield node

    for node in sorted(graph, key=str):
        yield from visit(node)


def _reduced_to_runtime(value: ReducedExpr) -> Any:
    """Convert a reduced expression domain value into evaluator runtime data."""
    match value:
        case expression.Val(_, raw_value):
            return raw_value
        case tuple(args):
            return tuple(_reduced_to_runtime(arg) for arg in args)
        case frozenset(args):
            return frozenset(_reduced_to_runtime(arg) for arg in args)
        case expression.Lambda():
            return value
        case expression.Bad.bad:
            return value
        case _:
            return value


def _domain_product(domains: list[set[ReducedExpr]]) -> Iterable[tuple[ReducedExpr, ...]]:
    """Yield Cartesian products for child domains, including the empty product."""
    if any(not domain for domain in domains):
        return ()
    if not domains:
        return [()]
    return itertools.product(*(sorted(domain, key=str) for domain in domains))


def _powerset(values: Iterable[ReducedExpr]) -> Iterable[frozenset[ReducedExpr]]:
    """Yield all subsets of a finite set in a stable order."""
    ordered_values = tuple(sorted(set(values), key=str))
    for size in range(len(ordered_values) + 1):
        for combination in itertools.combinations(ordered_values, size):
            yield frozenset(combination)


def _declared_set_expressions() -> set[Expr]:
    """Return set-valued variables declared by the input program."""
    return {
        expression.Variable(cl_expr.arguments[0])
        for cl_expr in top_level_expressions
        if cl_expr.type == clingo.SymbolType.Function
        and (
            (cl_expr.name in {"set_assign", "set_baseDomain"} and len(cl_expr.arguments) == 2)
            or (cl_expr.name == "variable_declare" and len(cl_expr.arguments) == 2 and str(cl_expr.arguments[1]) == "set")
        )
    }

def _evaluate_python_expr(code: str, solver_identifiers) -> set[ReducedExpr]:
    """Evaluate a bare Python expression as a singleton domain."""
    try:
        globals_env = evaluator.get_environment(solver_identifiers)
        result = eval(evaluator.get_compiled_eval(code), globals_env, {})
    except Exception:
        return {expression.Bad.bad}
    reduced, errors = evaluator.reducedExpr(result)
    return {expression.Bad.bad if errors else reduced}


_BOOLEAN_OUTPUT_OPERATORS = frozenset(
    {
        operators.ArithmeticOperator.leq,
        operators.ArithmeticOperator.lt,
        operators.ArithmeticOperator.geq,
        operators.ArithmeticOperator.gt,
        expression.EqOperator.eq,
        expression.EqOperator.neq,
        operators.LogicOperator.conj,
        operators.LogicOperator.disj,
        operators.LogicOperator.leqv,
        operators.LogicOperator.limp,
        operators.LogicOperator.lnot,
        operators.LogicOperator.lxor,
        operators.LogicOperator.snot,
        operators.LogicOperator.wnot,
        operators.SetOperator.set_isin,
        operators.SetOperator.set_notin,
        operators.SetOperator.subset,
        operators.MultimapOperator.multimap_isin,
        expression.ConditionalOperator.hasValue,
    }
)


def _boolean_output_domain() -> set[ReducedExpr]:
    """Return the coarse domain used to skip expensive boolean-domain enumeration."""
    reduced_true, true_errors = evaluator.reducedExpr(True)
    reduced_false, false_errors = evaluator.reducedExpr(False)
    return {
        expression.Bad.bad if true_errors else reduced_true,
        expression.Bad.bad if false_errors else reduced_false,
        expression.Bad.bad,
    }


def _has_boolean_output(op_value: Any) -> bool:
    """Check whether a concrete operator is known to produce a boolean-valued result."""
    return op_value in _BOOLEAN_OUTPUT_OPERATORS


def _apply_operation(
    op_value: Any, arg_values: tuple[ReducedExpr, ...], solver_identifiers: dict[Any, Any]
) -> ReducedExpr | None:
    """Apply one operator value to one tuple of reduced argument values."""
    recoverable = {
        operators.LogicOperator.conj,
        operators.LogicOperator.disj,
        operators.LogicOperator.limp,
        operators.LogicOperator.ite,
        expression.ConditionalOperator.IF,
        expression.ConditionalOperator.default,
        operators.ArithmeticOperator.pow,
    }

    if op_value == expression.Bad.bad or (expression.Bad.bad in arg_values and op_value not in recoverable):
        return expression.Bad.bad

    runtime_args = [_reduced_to_runtime(value) for value in arg_values]
    try:
        result = evaluator.operator(op_value, runtime_args, solver_identifiers, {}).value
    except Exception:
        return expression.Bad.bad
    if isinstance(result, dict) and not isinstance(result, multimap.HashableDict):
        result = multimap.HashableDict(result)
    try:
        reduced, errors = evaluator.reducedExpr(result)
        return expression.Bad.bad if errors else reduced
    except Exception:
        return expression.Bad.bad


def _flatten_set_values(values: set[ReducedExpr]) -> set[ReducedExpr]:
    """Return the union of all members from concrete set values."""
    candidates: set[ReducedExpr] = set()
    for value in values:
        if isinstance(value, frozenset):
            candidates.update(value)
    return candidates


def _set_candidate_domain(
    expr_: Expr,
    expression_domains: ExpressionDomains,
    set_sources: SetVariableSources,
) -> set[ReducedExpr] | None:
    """Collect candidate element values for set-valued expressions."""

    match expr_:
        case expression.Variable(var):
            if var not in set_sources:
                return None
            candidates: set[ReducedExpr] = set()
            for source_expr in set_sources[var]["set_baseDomain"] | set_sources[var]["set_assign"]:
                source_values = expression_domains.get(source_expr, set())
                candidates.update(value for value in source_values if not isinstance(value, frozenset) and value != expression.Bad.bad)
                candidates.update(_flatten_set_values(source_values))
            return candidates
        case _:
            candidates = _flatten_set_values(expression_domains.get(expr_, set()))
            return candidates or None


def _concrete_set_domain(
    expr_: Expr,
    expression_domains: ExpressionDomains,
    set_sources: SetVariableSources,
) -> set[ReducedExpr] | None:
    """Enumerate concrete set values for set expressions using candidate and required members."""

    def scalar_values(source_expr: Expr) -> set[ReducedExpr]:
        return {
            value
            for value in expression_domains.get(source_expr, set())
            if not isinstance(value, frozenset) and value != expression.Bad.bad
        }

    def set_values(source_expr: Expr) -> set[frozenset[ReducedExpr]]:
        return {
            value
            for value in expression_domains.get(source_expr, set())
            if isinstance(value, frozenset)
        }

    match expr_:
        case expression.Variable(var):
            declared_set_expressions = _declared_set_expressions()
            if var not in set_sources:
                if expression.Variable(var) in declared_set_expressions:
                    return {frozenset()}
                return None

            source_info = set_sources[var]
            optional_candidates: set[ReducedExpr] = set()
            for source_expr in source_info["set_baseDomain"]:
                optional_candidates.update(scalar_values(source_expr))

            required_scalars: set[ReducedExpr] = set()
            required_set_options: list[tuple[frozenset[ReducedExpr], ...]] = []
            for source_expr in source_info["set_assign"]:
                required_scalars.update(scalar_values(source_expr))
                set_options = tuple(sorted(set_values(source_expr), key=str))
                if set_options:
                    required_set_options.append(set_options)

            concrete_sets: set[ReducedExpr] = set()
            set_combinations = itertools.product(*required_set_options) if required_set_options else [()]
            for chosen_sets in set_combinations:
                required_members = set(required_scalars)
                for chosen_set in chosen_sets:
                    required_members.update(chosen_set)

                optional_members = optional_candidates.difference(required_members)
                for subset in _powerset(optional_members):
                    concrete_sets.add(frozenset(required_members | set(subset)))
            return concrete_sets
        case _:
            values = expression_domains.get(expr_, set())
            concrete_sets = {value for value in values if isinstance(value, frozenset)}
            return concrete_sets or None


def _set_uid_map(values: set[ReducedExpr]) -> dict[frozenset[ReducedExpr], int]:
    """Create stable identifiers for the concrete set values in one expression domain."""
    set_values = [value for value in sorted(values, key=str) if isinstance(value, frozenset)]
    return {set_value: uid for uid, set_value in enumerate(set_values)}


def _python_result_terms(result: Any, errors: list[tuple[warning.Kind, Any]]) -> list[PythonEvaluationOutputTerm]:
    """Convert evaluator outputs into exported Python evaluation terms."""
    if errors:
        return [expression.Bad.bad]
    if isinstance(result, dict) and not isinstance(result, multimap.HashableDict):
        result = multimap.HashableDict(result)
    try:
        reduced, reduction_errors = evaluator.reducedExpr(result)
        return [expression.Bad.bad if reduction_errors else reduced]
    except Exception as exn:
        _ = exn
        return [expression.Bad.bad]


def _python_output_signature(output_terms: list[PythonEvaluationOutputTerm]) -> PythonEvaluationOutputSignature:
    """Canonicalize one Python evaluation result so equivalent leaves can be merged."""
    return tuple(sorted(_python_domain_values(output_terms), key=str))


def _python_evaluation_trie(
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


def _compress_python_evaluation_trie(
    trie: dict[Any, Any],
    ordered_domains: tuple[tuple[ReducedExpr, ...], ...],
    depth: int = 0,
) -> PythonEvaluationLeaf | PythonEvaluationNode:
    """Collapse trie levels when every value in an argument domain leads to the same subtree."""
    if depth == len(ordered_domains):
        return PythonEvaluationLeaf(trie[PYTHON_EVAL_LEAF])

    branches = tuple(
        (value, _compress_python_evaluation_trie(trie[value], ordered_domains, depth + 1))
        for value in ordered_domains[depth]
    )
    first_child = branches[0][1]
    if all(child == first_child for _, child in branches[1:]):
        return first_child
    return PythonEvaluationNode(depth, branches)


def _compressed_python_evaluations(
    arg_domains: list[set[ReducedExpr]],
    outputs_by_assignment: dict[PythonEvaluationAssignment, PythonEvaluationOutputSignature],
) -> list[PythonEvaluationCompressedTrace]:
    """Return wildcard-safe Python evaluation traces that still cover the full input product."""
    if not outputs_by_assignment:
        return []

    ordered_domains = tuple(tuple(sorted(domain, key=str)) for domain in arg_domains)
    tree = _compress_python_evaluation_trie(_python_evaluation_trie(outputs_by_assignment), ordered_domains)

    compressed: list[PythonEvaluationCompressedTrace] = []

    def collect(
        node: PythonEvaluationLeaf | PythonEvaluationNode,
        bindings: tuple[tuple[int, ReducedExpr], ...],
    ) -> None:
        if isinstance(node, PythonEvaluationLeaf):
            compressed.append((bindings, node.outputs))
            return
        for value, child in node.branches:
            collect(child, bindings + ((node.index, value),))

    collect(tree, ())
    return compressed

def _python_operation_output_terms(
    op_value: expression.Python | expression.PythonExtract,
    arg_values: tuple[ReducedExpr, ...],
    solver_identifiers,
) -> list[PythonEvaluationOutputTerm]:
    """Evaluate one Python operation on one concrete tuple of reduced arguments."""
    runtime_args = [_reduced_to_runtime(value) for value in arg_values]
    try:
        applied = evaluator.operator(op_value, runtime_args, solver_identifiers, {})
    except Exception as exn:
        _ = exn
        return [expression.Bad.bad]
    return _python_result_terms(applied.value, list(applied.errors))


def _execute_python_extract_statement(
    stmt: str,
    arg_values: tuple[ReducedExpr, ...],
    solver_identifiers,
) -> PythonExtractExecution:
    """Execute one Python statement body once for a concrete tuple of inputs."""
    runtime_args = [_reduced_to_runtime(value) for value in arg_values]
    try:
        locals_env = {name: val for name, val in runtime_args}
    except ValueError:
        return None, [], None
    if any(value == expression.Bad.bad for value in locals_env.values()):
        return None, [], None

    errors: list[tuple[warning.Kind, Any]] = []
    try:
        evaluator.stmt_python(stmt, solver_identifiers, locals_env, errors)
        succeeds = True
    except evaluator.solver_environment.FailIntegrityExn:
        succeeds = False
    return locals_env, errors, succeeds


def _python_extract_output_terms(
    stmt: str,
    expr_code: str,
    arg_values: tuple[ReducedExpr, ...],
    solver_identifiers,
    execution_cache: dict[tuple[str, tuple[ReducedExpr, ...]], PythonExtractExecution],
) -> list[PythonEvaluationOutputTerm]:
    """Evaluate one extracted Python output while reusing the underlying statement run."""
    cache_key = (stmt, arg_values)
    cached_execution = execution_cache.get(cache_key)
    if cached_execution is None:
        cached_execution = _execute_python_extract_statement(stmt, arg_values, solver_identifiers)
        execution_cache[cache_key] = cached_execution
    locals_env, errors, succeeds = cached_execution

    if locals_env is None:
        return [expression.Bad.bad]
    if errors:
        return _python_result_terms(expression.Bad.bad, errors)
    if expr_code == "__succeeds":
        return _python_result_terms(succeeds, [])

    try:
        globals_env = evaluator.get_environment(solver_identifiers)
        result = eval(evaluator.get_compiled_eval(expr_code), globals_env, locals_env)
    except Exception as exn:
        kind = warning.Expression(warning.ExpressionWarning.pythonError)
        return _python_result_terms(expression.Bad.bad, [(kind, repr(exn))])
    return _python_result_terms(result, [])


def _python_expression_output_terms(expr_: expression.Python, solver_identifiers) -> list[PythonEvaluationOutputTerm]:
    """Evaluate one zero-argument Python expression during domain computation."""
    result, errors = evaluator.evaluate_expr(expr_, solver_identifiers, {})
    return _python_result_terms(result, errors)


def _python_domain_values(output_terms: list[PythonEvaluationOutputTerm]) -> set[ReducedExpr]:
    """Extract the actual expression-domain values from one Python evaluation."""
    return set(output_terms)


def _python_value_reference(expr_: Expr, value: PythonEvaluationOutputValue, set_uid_maps: SetUidMaps) -> PythonEvaluationOutputValue:
    """Replace concrete set values by the stable UID of the owning set expression when available."""
    if isinstance(value, frozenset):
        uid_map = set_uid_maps.get(expr_)
        if uid_map is not None and value in uid_map:
            return uid_map[value]
    return value


def _evaluate_domain(
    expr_: Expr,
    expression_domains: ExpressionDomains,
    solver_identifiers,
) -> set[ReducedExpr]:
    """Evaluate one expression using already-computed child-expression domains."""
    match expr_:
        case expression.Variable(_):
            return expression_domains.get(expr_, set())
        case expression.Val(_, _) | expression.Bad.bad:
            return {expr_}
        case expression.Lambda(_, _):
            return {expr_}
        case expression.Python(code):
            return _evaluate_python_expr(code, solver_identifiers)
        case expression.Operation(op, args):
            op_domains = (
                expression_domains.get(op, set())
                if isinstance(op, (expression.Variable, expression.Operation, expression.Lambda))
                else {op}
            )
            arg_domains = [expression_domains.get(arg, set()) for arg in args]
            if not op_domains or any(not domain for domain in arg_domains):
                return set()

            results: set[ReducedExpr] = set()
            apply_total = len(op_domains)
            for arg_domain in arg_domains:
                apply_total *= len(arg_domain)
            if _has_boolean_output(op) and apply_total > 1:
                return _boolean_output_domain()
            for op_domain_value in sorted(op_domains, key=str):
                op_value = _reduced_to_runtime(op_domain_value) if op_domain_value != op else op
                for arg_values in _domain_product(arg_domains):
                    result = _apply_operation(op_value, arg_values, solver_identifiers)
                    if result is not None:
                        results.add(result)
            return results
        case tuple(args):
            child_domains = [expression_domains.get(arg, set()) for arg in args]
            return {tuple(values) for values in _domain_product(child_domains)}
        case frozenset(args):
            child_domains = [expression_domains.get(arg, set()) for arg in args]
            return {frozenset(values) for values in _domain_product(child_domains)}
        case _ if _is_scalar_expression(expr_):
            reduced, errors = evaluator.reducedExpr(expr_)
            return {expression.Bad.bad if errors else reduced}
        case _:
            return {expression.Bad.bad}


def _compute_domains() -> tuple[
    ExpressionDomains,
    SetCandidateDomains,
    SetUidMaps,
    list[PythonEvaluationAtom],
    list[PythonEvaluationInputAtom],
    list[PythonEvaluationOutputAtom],
]:
    """Compute domains and Python evaluation traces in dependency order."""
    graph, variable_sources, set_sources = _build_expression_graph()
    globals_env = evaluator.get_environment(solver_identifiers)
    expression_domains: ExpressionDomains = {}
    set_candidate_domains: SetCandidateDomains = {}
    set_uid_maps: SetUidMaps = {}
    python_evaluations: list[PythonEvaluationAtom] = []
    python_evaluation_inputs: list[PythonEvaluationInputAtom] = []
    python_evaluation_outputs: list[PythonEvaluationOutputAtom] = []
    python_extract_execution_cache: dict[tuple[str, tuple[ReducedExpr, ...]], PythonExtractExecution] = {}
    declared_set_exprs = _declared_set_expressions()

    for expr_ in _topological_order(graph):
        match expr_:
            case expression.Variable(_):
                values: set[ReducedExpr] = set()
                for source_expr in variable_sources.get(expr_.arg, set()):
                    values.update(expression_domains.get(source_expr, set()))

                concrete_set_domain = _concrete_set_domain(expr_, expression_domains, set_sources)
                if concrete_set_domain is not None:
                    values.update(concrete_set_domain)
                expression_domains[expr_] = values
            case expression.Python(_):
                python_evaluations.append((expr_, 0))
                raw_outputs = _python_expression_output_terms(expr_, solver_identifiers)
                expression_domains[expr_] = _python_domain_values(raw_outputs)

                uid_map = _set_uid_map(expression_domains[expr_])
                if uid_map:
                    set_uid_maps[expr_] = uid_map

                for output_value in raw_outputs:
                    python_evaluation_outputs.append(
                        (expr_, 0, _python_value_reference(expr_, output_value, set_uid_maps))
                    )
            case expression.Operation(op_value, args) if isinstance(op_value, (expression.Python, expression.PythonExtract)):
                arg_domains = [expression_domains.get(arg, set()) for arg in args]
                values: set[ReducedExpr] = set()
                outputs_by_assignment: dict[PythonEvaluationAssignment, PythonEvaluationOutputSignature] = {}

                if not any(not domain for domain in arg_domains):
                    for arg_values in _domain_product(arg_domains):
                        if isinstance(op_value, expression.PythonExtract):
                            raw_outputs = _python_extract_output_terms(
                                op_value.stmt,
                                op_value.expr,
                                arg_values,
                                solver_identifiers,
                                python_extract_execution_cache,
                            )
                        else:
                            raw_outputs = _python_operation_output_terms(op_value, arg_values, solver_identifiers)
                        outputs_by_assignment[arg_values] = _python_output_signature(raw_outputs)
                        values.update(_python_domain_values(raw_outputs))

                expression_domains[expr_] = values

                uid_map = _set_uid_map(values)
                if uid_map:
                    set_uid_maps[expr_] = uid_map

                for uid, (bindings, output_signature) in enumerate(
                    _compressed_python_evaluations(arg_domains, outputs_by_assignment)
                ):
                    python_evaluations.append((expr_, uid))

                    if isinstance(op_value, expression.PythonExtract):
                        for index, arg_value in bindings:
                            arg_expr = args[index]
                            if not (
                                isinstance(arg_expr, tuple)
                                and len(arg_expr) == 2
                                and isinstance(arg_expr[0], expression.Val)
                            ):
                                continue
                            if not (
                                isinstance(arg_value, tuple)
                                and len(arg_value) == 2
                                and isinstance(arg_value[0], expression.Val)
                            ):
                                continue
                            _, parameter_value = arg_value
                            _, value_expr = arg_expr
                            python_evaluation_inputs.append(
                                (
                                    expr_,
                                    uid,
                                    value_expr,
                                    _python_value_reference(value_expr, parameter_value, set_uid_maps),
                                )
                            )
                    else:
                        for index, arg_value in bindings:
                            arg_expr = args[index]
                            python_evaluation_inputs.append(
                                (
                                    expr_,
                                    uid,
                                    arg_expr,
                                    _python_value_reference(arg_expr, arg_value, set_uid_maps),
                                )
                            )

                    for output_value in output_signature:
                        python_evaluation_outputs.append(
                            (expr_, uid, _python_value_reference(expr_, output_value, set_uid_maps))
                        )
            case _:
                expression_domains[expr_] = _evaluate_domain(expr_, expression_domains, solver_identifiers)

        if expr_ not in set_uid_maps:
            uid_map = _set_uid_map(expression_domains[expr_])
            if uid_map:
                set_uid_maps[expr_] = uid_map

        candidate_domain = _set_candidate_domain(expr_, expression_domains, set_sources)
        if candidate_domain is not None:
            set_candidate_domains[expr_] = candidate_domain

    for expr_ in declared_set_exprs:
        expression_domains.setdefault(expr_, set())
        set_candidate_domains.setdefault(expr_, set())

    return (
        expression_domains,
        set_candidate_domains,
        set_uid_maps,
        python_evaluations,
        python_evaluation_inputs,
        python_evaluation_outputs,
    )


def _ensure_cached_domains() -> DomainCache:
    """Return cached domain data, computing it once per grounding input."""
    global cached_domains
    if cached_domains is None:
        (
            expression_domains,
            set_candidate_domains,
            set_uid_maps,
            python_evaluations,
            python_evaluation_inputs,
            python_evaluation_outputs,
        ) = _compute_domains()
        declared_set_expressions = _declared_set_expressions()
        set_expressions = {
            expr_
            for expr_, values in expression_domains.items()
            if any(isinstance(value, frozenset) for value in values)
        }
        set_expressions.update(set_candidate_domains)
        set_expressions.update(expr_ for expr_ in expression_domains if expr_ in declared_set_expressions)
        cached_domains = DomainCache(
            expression_domains=expression_domains,
            set_candidate_domains=set_candidate_domains,
            set_expressions=set_expressions,
            set_uid_maps=set_uid_maps,
            python_evaluations=python_evaluations,
            python_evaluation_inputs=python_evaluation_inputs,
            python_evaluation_outputs=python_evaluation_outputs,
        )
    return cached_domains


def expressionDomain() -> list[clingo.Symbol]:
    """Expose all computed expression-domain pairs back to clingo."""
    cache = _ensure_cached_domains()

    result: list[clingo.Symbol] = []
    for expr_, values in sorted(cache.expression_domains.items(), key=lambda item: str(item[0])):
        cl_expr = myClorm.pytocl(expr_)
        for value in sorted(values, key=str):
            if expr_ in cache.set_expressions and isinstance(value, frozenset):
                continue
            result.append(myClorm.pytocl((cl_expr, value)))
    return result


def expressionSetDomain() -> list[clingo.Symbol]:
    """Expose one identifier per concrete set in the computed domain of a set expression."""
    cache = _ensure_cached_domains()

    result: list[clingo.Symbol] = []
    for expr_, uid_map in sorted(cache.set_uid_maps.items(), key=lambda item: str(item[0])):
        cl_expr = myClorm.pytocl(expr_)
        for _set_value, uid in sorted(uid_map.items(), key=lambda item: item[1]):
            result.append(myClorm.pytocl((cl_expr, uid)))
    return result


def expressionSetDomainValue() -> list[clingo.Symbol]:
    """Expose explicit positive and negative membership for each concrete set domain."""
    cache = _ensure_cached_domains()

    result: list[clingo.Symbol] = []
    for expr_, uid_map in sorted(cache.set_uid_maps.items(), key=lambda item: str(item[0])):
        cl_expr = myClorm.pytocl(expr_)
        candidate_values = cache.set_candidate_domains.get(expr_, set())
        for set_value, uid in sorted(uid_map.items(), key=lambda item: item[1]):
            members = set(set_value)
            for member in sorted(candidate_values | members, key=str):
                sign = SET_DOMAIN_POS if member in members else SET_DOMAIN_NEG
                result.append(myClorm.pytocl((cl_expr, uid, sign, member)))
    return result


def expressionSetDomainSymbol(cl_expr: clingo.Symbol) -> list[clingo.Symbol]:
    """Expose concrete set values only for the requested set expression."""
    cache = _ensure_cached_domains()

    expr_ = myClorm.cltopy(cl_expr, expression.Expr)
    uid_map = cache.set_uid_maps.get(expr_, {})
    return [
        myClorm.pytocl((uid, set_value))
        for set_value, uid in sorted(uid_map.items(), key=lambda item: item[1])
    ]


def expressionSet() -> list[clingo.Symbol]:
    """Expose expressions whose computed domain contains a set value."""
    cache = _ensure_cached_domains()

    result: list[clingo.Symbol] = []
    for expr_ in sorted(cache.set_expressions, key=str):
        result.append(myClorm.pytocl(expr_))
    return result


def pythonEvaluation() -> list[clingo.Symbol]:
    """Expose one identifier per Python evaluation considered during domain computation."""
    cache = _ensure_cached_domains()

    result: list[clingo.Symbol] = []
    symbol_cache: ClingoSymbolCache = {}
    for evaluation in cache.python_evaluations:
        expr_, uid = evaluation
        result.append(
            clingo.Function(
                "",
                [_cached_pytocl(expr_, symbol_cache), _cached_pytocl(uid, symbol_cache)],
            )
        )
    return result


def pythonEvaluationInput() -> list[clingo.Symbol]:
    """Expose the concrete inputs used in each Python evaluation."""
    cache = _ensure_cached_domains()

    result: list[clingo.Symbol] = []
    symbol_cache: ClingoSymbolCache = {}
    for evaluation_input in cache.python_evaluation_inputs:
        expr_, uid, arg_expr, arg_value = evaluation_input
        result.append(
            clingo.Function(
                "",
                [
                    _cached_pytocl(expr_, symbol_cache),
                    _cached_pytocl(uid, symbol_cache),
                    _cached_pytocl(arg_expr, symbol_cache),
                    _cached_pytocl(arg_value, symbol_cache),
                ],
            )
        )
    return result


def pythonEvaluationOutput() -> list[clingo.Symbol]:
    """Expose the outputs produced by each Python evaluation."""
    cache = _ensure_cached_domains()

    result: list[clingo.Symbol] = []
    symbol_cache: ClingoSymbolCache = {}
    for evaluation_output in cache.python_evaluation_outputs:
        expr_, uid, output_value = evaluation_output
        result.append(
            clingo.Function(
                "",
                [
                    _cached_pytocl(expr_, symbol_cache),
                    _cached_pytocl(uid, symbol_cache),
                    _cached_pytocl(output_value, symbol_cache),
                ],
            )
        )
    return result
#end.
