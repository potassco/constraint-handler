"""Dependency analysis and topological ordering utilities."""

from collections.abc import Iterator
from contextlib import suppress
from dataclasses import dataclass
from graphlib import CycleError, TopologicalSorter
from typing import assert_never

from .diagnostics import Diagnostics
from .internal_input import (
    ConstraintStore,
    ExprId,
    Lambda,
    Operation,
    OperationArg,
    Python,
    ValueDef,
    VariableRef,
)


def free_variables(
    expr: OperationArg, bound: frozenset[VariableRef] = frozenset()
) -> frozenset[VariableRef]:
    """Return all free VariableRefs read by an expression or operation argument."""
    match expr:
        case ValueDef() | Python():
            return frozenset()
        case VariableRef():
            return frozenset() if expr in bound else frozenset({expr})
        case frozenset() | tuple():
            return frozenset(
                var for item in expr for var in free_variables(item, bound)
            )
        case Lambda(params, body):
            return free_variables(body, bound | frozenset(params))
        case Operation(_, args):
            return frozenset(var for arg in args for var in free_variables(arg, bound))
    assert_never(expr)


def defining_expr_ids_for_variable(
    store: ConstraintStore, var: VariableRef
) -> tuple[ExprId, ...]:
    """Collect all value expression IDs that define a scalar or set variable."""
    ids: list[ExprId] = []
    if var in store.variables:
        variable = store.variables[var]
        ids.extend(choice.value for choice in variable.choices)
        ids.extend(definition.value for definition in variable.definitions)
        ids.extend(default.value for default in variable.defaults)
    if var in store.set_variables:
        set_var = store.set_variables[var]
        ids.extend(base.value for base in set_var.bases)
        ids.extend(assign.value for assign in set_var.assigns)
        ids.extend(default.value for default in set_var.defaults)
    return tuple(ids)


@dataclass(frozen=True, slots=True)
class EvaluationOrder:
    """Store topological expression order, undefined variables, and blocked expressions."""

    expr_order: tuple[ExprId, ...]
    undefined_variables: frozenset[VariableRef]
    cyclic_exprs: frozenset[ExprId]
    defining_exprs: dict[VariableRef, tuple[ExprId, ...]]

    def evaluation_steps(self) -> Iterator[tuple[ExprId, tuple[VariableRef, ...]]]:
        """Yield expressions and variables ready after each expression completes."""
        remaining = {var: len(set(defs)) for var, defs in self.defining_exprs.items()}
        dependents: dict[ExprId, list[VariableRef]] = {}
        for var, definitions in self.defining_exprs.items():
            for expr_id in set(definitions):
                dependents.setdefault(expr_id, []).append(var)
        for expr_id in self.expr_order:
            ready: list[VariableRef] = []
            for var in dependents.get(expr_id, ()):
                remaining[var] -= 1
                if remaining[var] == 0:
                    ready.append(var)
            yield expr_id, tuple(ready)


def compute_evaluation_order(
    store: ConstraintStore, diagnostics: Diagnostics
) -> EvaluationOrder:
    """Order expressions with graphlib.TopologicalSorter and report undefined or cyclic dependencies."""
    defined_vars = {
        var: defs
        for var in set(store.variables) | set(store.set_variables)
        if (defs := defining_expr_ids_for_variable(store, var))
    }

    undefined: set[VariableRef] = set()
    sorter: TopologicalSorter[ExprId] = TopologicalSorter()

    for expr_id, expr in store.expressions.items():
        deps: set[ExprId] = set()
        for var in free_variables(expr):
            if var in defined_vars:
                deps.update(defined_vars[var])
            else:
                if var not in undefined:
                    diagnostics.error(
                        f"Variable {var.name!r} has no defining expressions",
                        variable=var,
                        expr_id=expr_id,
                    )
                undefined.add(var)
        sorter.add(expr_id, *deps)

    with suppress(CycleError):
        sorter.prepare()
    ordered: list[ExprId] = []
    while ready := sorted(sorter.get_ready()):
        ordered.extend(ready)
        sorter.done(*ready)

    cyclic = frozenset(store.expressions.keys() - set(ordered))
    for expr_id in sorted(cyclic):
        diagnostics.error(
            f"Expression {expr_id} is part of or depends on a dependency cycle",
            expr_id=expr_id,
        )

    return EvaluationOrder(
        expr_order=tuple(ordered),
        undefined_variables=frozenset(undefined),
        cyclic_exprs=cyclic,
        defining_exprs=defined_vars,
    )
