"""Split nested expressions when auxiliary definitions reduce grounding costs."""

from collections.abc import Hashable, Iterable
from itertools import combinations
from math import inf
from typing import cast

from .analysis import ExpressionStore
from .diagnostics import Diagnostics
from .domains import Domain, DomainStore
from .internal_input import (
    ConstraintStore,
    Expr,
    Lambda,
    Operation,
    OperationArg,
    Python,
    ValueDef,
    ValueType,
    Variable,
    VariableDefinition,
    VariableRef,
)
from .python_conversion import convert
from .python_input import Operator
from .static_types import SetOf, StaticTypeStore, UnknownType
from .util import EvaluationOrder, free_variables

DEFAULT_SUBSET_LIMIT = 12
type Cost = int | float
type Renaming = tuple[Expr, Expr, frozenset[VariableRef]]


def _product(factors: Iterable[Cost]) -> Cost:
    """Multiply cardinalities, giving empty domains precedence over infinity."""
    result: Cost = 1
    for factor in factors:
        if factor == 0:
            return 0
        result = inf if result == inf or factor == inf else result * factor
    return result


def _sum(costs: Iterable[Cost]) -> Cost:
    """Add cardinalities without converting arbitrarily large integers to reals."""
    total: Cost = 0
    for cost in costs:
        if cost == inf:
            return inf
        total += cost
    return total


def _contains_operation(expr: OperationArg) -> bool:
    """Find operations inside collections without entering callable descriptors."""
    if isinstance(expr, Operation):
        return True
    if isinstance(expr, (tuple, frozenset)):
        return any(_contains_operation(item) for item in expr)
    return False


class _MetadataTransfer[Metadata: Hashable]:
    """Transfer renamed metadata from a fixed index of original lexical scopes."""

    def __init__(self, metadata: ExpressionStore[Metadata]) -> None:
        """Index source scopes once, excluding scopes created during conversion."""
        self.metadata = metadata
        self.by_expression: dict[
            Expr, list[tuple[frozenset[tuple[VariableRef, Metadata]], Metadata]]
        ] = {}
        for (expr, scope), value in metadata.scoped_expressions.items():
            self.by_expression.setdefault(expr, []).append((scope, value))

    def transfer(
        self,
        renamings: list[Renaming],
        replacements: dict[VariableRef, VariableRef],
    ) -> None:
        """Copy available metadata only from the node's active lexical bindings."""
        metadata = self.metadata
        bindings = {target: metadata[source] for source, target in replacements.items()}
        for source, target, shadowed in renamings:
            if not shadowed and source in metadata:
                if bindings:
                    metadata.scoped_expressions.setdefault(
                        (target, frozenset(bindings.items())), metadata[source]
                    )
                else:
                    metadata.setdefault(target, metadata[source])
            for scope, value in self.by_expression.get(source, ()):
                if shadowed != frozenset(var for var, _ in scope):
                    continue
                renamed_scope = dict(bindings)
                renamed_scope.update(scope)
                metadata.scoped_expressions.setdefault(
                    (target, frozenset(renamed_scope.items())), value
                )


class GroundingCost:
    """Estimate expression grounding costs from precomputed domains and types."""

    def __init__(
        self,
        domains: DomainStore,
        static_types: StaticTypeStore,
    ) -> None:
        """Retain the metadata used by the encoding-specific estimates."""
        self.domains = domains
        self.types = static_types

    def size(self, expr: Expr) -> Cost:
        """Read cardinality without enumerating an unknown or implicit domain."""
        count = self.domains[expr].cardinality()
        return inf if count is None else count

    def members(self, expr: Expr) -> Cost:
        """Count potential members without enumerating complete set values."""
        domain = self.domains[expr]
        return inf if domain.unknown else len(domain.potential_set_members())

    def trivial_cost(self, expr: Operation) -> Cost:
        """Estimate the specialized encoding as if direct arguments were leaves."""
        op = expr.op
        args = [
            arg
            for arg in self.parameters(expr)
            if not isinstance(arg, (Lambda, Python))
        ]
        if op in {Operator.lambda_, Operator.set_fold}:
            captures = frozenset(
                var
                for arg in expr.args
                if isinstance(arg, Lambda)
                for var in free_variables(arg)
            )
            return _product(
                (
                    *(self.size(arg) for arg in args),
                    *(self.size(var) for var in captures if var not in args),
                )
            )
        if op in {Operator.conj, Operator.disj}:
            return len(args) + 1
        if op == Operator.linear_comparison:
            return 1
        if op == Operator.leqv:
            return len(args)
        if op == Operator.linear_integer:
            terms = args[:-1]
            return (
                self.size(expr)
                if len(terms) > 2
                else _product(self.size(term) for term in terms)
            )
        if op in {Operator.eq, Operator.neq}:
            if all(self.is_set(arg) for arg in args):
                return _sum(self.members(arg) for arg in args)
            return 2 * min(self.size(arg) for arg in args)
        if op == Operator.union:
            return _sum(self.members(arg) for arg in args)
        if op == Operator.inter:
            return min(self.members(arg) for arg in args)
        if op in {Operator.diff, Operator.subset}:
            return self.members(args[0])
        if op == Operator.set_make:
            return _sum(self.size(arg) for arg in args)
        if op in {Operator.set_isin, Operator.set_notin}:
            return self.size(args[0])
        if op == Operator.cardinality or (
            op == Operator.length and self.is_set(args[0])
        ):
            return self.size(expr) + self.members(args[0])
        return _product(self.size(arg) for arg in args)

    def is_set(self, expr: Expr) -> bool:
        """Recognize exclusively set-valued expressions from static types."""
        kind = self.types[expr]
        return (
            not isinstance(kind, UnknownType)
            and bool(kind)
            and all(isinstance(member, SetOf) for member in kind)
        )

    def complexity(self, expr: Expr) -> Cost:
        """Use specialized costs only when the expression has no nested operation."""
        if isinstance(expr, Operation) and not any(
            _contains_operation(arg) for arg in expr.args
        ):
            return self.trivial_cost(expr)
        return _product(self.size(var) for var in free_variables(expr))

    def parameters(self, expr: Operation) -> tuple[OperationArg, ...]:
        """Expose linear terms without detaching their literal coefficients."""
        if expr.op in {Operator.linear_integer, Operator.linear_comparison}:
            pairs = (
                expr.args[1:-1]
                if expr.op == Operator.linear_comparison
                else expr.args[:-1]
            )
            return (
                *(cast(tuple[Expr, Expr], pair)[1] for pair in pairs),
                expr.args[-1],
            )
        return expr.args


class _Splitter(GroundingCost):
    """Estimate unchanged candidates and commit only the best local replacement."""

    def __init__(
        self,
        store: ConstraintStore,
        domains: DomainStore,
        static_types: StaticTypeStore,
        subset_limit: int,
    ) -> None:
        """Retain mutable pass state and reserve all existing variable names."""
        super().__init__(domains, static_types)
        self.store = store
        self.subset_limit = subset_limit
        self.names = {var.name for var in (*store.variables, *store.set_variables)}
        pending: list[OperationArg] = list(store.expressions.values())
        while pending:
            expr = pending.pop()
            match expr:
                case VariableRef(name):
                    self.names.add(name)
                case Lambda(parameters, body):
                    self.names.update(var.name for var in parameters)
                    pending.append(body)
                case Operation(_, args):
                    pending.extend(args)
                case tuple() | frozenset():
                    pending.extend(expr)
                case ValueDef() | Python():
                    pass
        self.counter = 0

    def fresh(self) -> VariableRef:
        """Allocate a deterministic name distinct from free and bound inputs."""
        while True:
            name = f"__split_{self.counter}"
            self.counter += 1
            if name not in self.names:
                self.names.add(name)
                return VariableRef(name)

    def rename(
        self,
        expr: OperationArg,
        replacements: dict[VariableRef, VariableRef],
        renamings: list[Renaming],
        shadowed: frozenset[VariableRef] = frozenset(),
    ) -> OperationArg:
        """Rename free variables and record nodes whose metadata needs copying."""
        renamed: Expr
        match expr:
            case VariableRef():
                renamed = replacements.get(expr, expr)
            case Lambda(parameters, body):
                visible = {
                    source: target
                    for source, target in replacements.items()
                    if source not in parameters
                }
                return Lambda(
                    parameters,
                    cast(
                        Expr,
                        self.rename(
                            body, visible, renamings, shadowed | frozenset(parameters)
                        ),
                    ),
                )
            case Operation(op, args):
                renamed = Operation(
                    op,
                    tuple(
                        self.rename(arg, replacements, renamings, shadowed)
                        for arg in args
                    ),
                )
            case tuple():
                renamed = tuple(
                    cast(Expr, self.rename(item, replacements, renamings, shadowed))
                    for item in expr
                )
            case frozenset():
                renamed = frozenset(
                    cast(Expr, self.rename(item, replacements, renamings, shadowed))
                    for item in expr
                )
            case Python():
                return expr
            case ValueDef():
                renamed = expr
        renamings.append((expr, renamed, shadowed))
        return renamed

    def best_subset(self, expr: Operation) -> tuple[int, ...]:
        """Search unchanged candidates using cached parameter costs and variables."""
        parameters = self.parameters(expr)
        positions = tuple(
            index for index, arg in enumerate(parameters) if _contains_operation(arg)
        )
        if not positions:
            return ()
        sizes = {index: self.size(cast(Expr, parameters[index])) for index in positions}
        costs = {
            index: self.complexity(cast(Expr, parameters[index])) for index in positions
        }
        variables = tuple(free_variables(arg) for arg in parameters)
        variable_sizes = {var: self.size(var) for group in variables for var in group}
        trivial = self.trivial_cost(expr)
        best: tuple[int, ...] = ()
        best_cost = self.complexity(expr)
        candidates = (
            (
                selected
                for count in range(1, len(positions) + 1)
                for selected in combinations(positions, count)
            )
            if len(positions) <= self.subset_limit
            else iter((positions,))
        )
        for selected in candidates:
            remaining = frozenset(
                var
                for index, group in enumerate(variables)
                if index not in selected
                for var in group
            )
            outer = (
                trivial
                if len(selected) == len(positions)
                else _product(
                    (
                        *(variable_sizes[var] for var in remaining),
                        *(sizes[index] for index in selected),
                    )
                )
            )
            cost = _sum((outer, _sum(costs[index] for index in selected)))
            if cost < best_cost:
                best, best_cost = selected, cost
        return best

    def run(self, order: EvaluationOrder) -> None:
        """Split store expressions and auxiliaries, then convert remaining nesting."""
        worklist = list(order.expr_order)
        for expr_id in worklist:
            expr = self.store.expressions[expr_id]
            if not isinstance(expr, Operation):
                continue
            best = self.best_subset(expr)
            parameters = self.parameters(expr)
            args = list(parameters)
            for index in best:
                parameter = cast(Expr, args[index])
                auxiliary = self.fresh()
                definition_id = self.store.add_expression(parameter)
                condition = ValueDef(ValueType.boolean, True)
                condition_id = self.store.add_expression(condition)
                self.store.variables[auxiliary] = Variable(
                    definitions=[VariableDefinition(definition_id, condition_id, "")]
                )
                domain = self.domains[parameter]
                kind = self.types[parameter]
                self.domains[auxiliary] = domain
                self.domains.setdefault(condition, Domain(bools=frozenset({True})))
                self.types[auxiliary] = kind
                self.types.setdefault(condition, frozenset({ValueType.boolean}))
                args[index] = auxiliary
                worklist.append(definition_id)
            if best:
                pairs = (
                    expr.args[1:-1]
                    if expr.op == Operator.linear_comparison
                    else expr.args[:-1]
                )
                rewritten_args = (
                    (
                        *(
                            (expr.args[0],)
                            if expr.op == Operator.linear_comparison
                            else ()
                        ),
                        *(
                            (cast(tuple[Expr, Expr], pair)[0], cast(Expr, arg))
                            for pair, arg in zip(pairs, args[:-1], strict=True)
                        ),
                        args[-1],
                    )
                    if expr.op in {Operator.linear_integer, Operator.linear_comparison}
                    else tuple(args)
                )
                rewritten = Operation(expr.op, rewritten_args)
                if expr.op in {Operator.linear_integer, Operator.linear_comparison}:
                    rewritten_pairs = (
                        rewritten_args[1:-1]
                        if expr.op == Operator.linear_comparison
                        else rewritten_args[:-1]
                    )
                    for before, after in zip(pairs, rewritten_pairs, strict=True):
                        before, after = cast(Expr, before), cast(Expr, after)
                        self.domains.setdefault(after, self.domains[before])
                        self.types.setdefault(after, self.types[before])
                self.store.replace_expression(expr_id, rewritten)
                self.domains.setdefault(rewritten, self.domains[expr])
                self.types.setdefault(rewritten, self.types[expr])
        self.convert_python_calls()

    def convert_python_calls(self) -> None:
        """Retain supported flat native operations; lower others to Python."""
        domains = _MetadataTransfer(self.domains)
        types = _MetadataTransfer(self.types)
        for expr_id, expr in self.store.expressions.items():
            if (
                isinstance(expr, Operation)
                and (
                    expr.op
                    in {
                        Operator.python_eval,
                        Operator.linear_integer,
                        Operator.linear_comparison,
                        Operator.conj,
                        Operator.disj,
                        Operator.leqv,
                        Operator.union,
                        Operator.inter,
                        Operator.diff,
                        Operator.subset,
                        Operator.set_make,
                        Operator.set_isin,
                        Operator.set_notin,
                        Operator.cardinality,
                    }
                    or expr.op in {Operator.eq, Operator.neq, Operator.length}
                    and all(self.is_set(cast(Expr, arg)) for arg in expr.args)
                )
                and not any(_contains_operation(arg) for arg in expr.args)
            ):
                continue
            if not isinstance(expr, Operation) and not _contains_operation(expr):
                continue
            actual = tuple(sorted(free_variables(expr), key=lambda var: var.name))
            bound = tuple(self.fresh() for _ in actual)
            replacements = dict(zip(actual, bound, strict=True))
            renamings: list[Renaming] = []
            body = cast(Expr, self.rename(expr, replacements, renamings))
            domains.transfer(renamings, replacements)
            types.transfer(renamings, replacements)
            call = Operation(Operator.python_eval, (convert(bound, body), *actual))
            self.store.replace_expression(expr_id, call)
            self.domains.setdefault(call, self.domains[expr])
            self.types.setdefault(call, self.types[expr])


def split(
    store: ConstraintStore,
    domains: DomainStore,
    static_types: StaticTypeStore,
    order: EvaluationOrder,
    diagnostics: Diagnostics,
    *,
    subset_limit: int = DEFAULT_SUBSET_LIMIT,
) -> None:
    """Update store, domains, and types in place with splitting and Python calls.

    Require validated expressions and metadata and order for the current store.
    Linear integer operations must end with an explicit integer literal offset.
    Above subset_limit nested arguments, consider only all-or-nothing splitting.
    Use the supplied evaluation order only for traversal. Only new nodes and
    scopes receive metadata; existing entries and diagnostics are preserved.
    """
    if subset_limit < 0:
        raise ValueError("subset_limit must be nonnegative")
    if diagnostics.has_errors:
        return
    _Splitter(store, domains, static_types, subset_limit).run(order)
