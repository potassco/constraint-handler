"""Independent, binding-aware validation of stored expressions and statements."""

from collections.abc import Mapping

from ..diagnostics import Diagnostic, DiagnosticSeverity, ExpressionLocation
from ..internal_input import (
    ConstraintStore,
    Expr,
    ExprId,
    Lambda,
    Operation,
    Python,
    ValueType,
    VariableRef,
)
from ..python_input import Operator
from ._type_inference import (
    lambda_bindings,
    operation_errors,
    operation_warnings,
    scalar_subset,
)
from .type_cache import (
    UNKNOWN,
    SetOf,
    Type,
    TypeCache,
    TypeScope,
    UnknownType,
    union_types,
)


class TypeChecker:
    """Check every root independently of cached or trusted result types."""

    def __init__(self, types: TypeCache) -> None:
        """Retain the session cache without retaining diagnostics between checks."""
        self._types = types

    def check(self, store: ConstraintStore) -> frozenset[Diagnostic]:
        """Return a fresh deduplicated diagnostic set for this cache's store."""
        diagnostics: set[Diagnostic] = set()
        visited: set[tuple[ExprId, Expr, TypeScope]] = set()
        for root, expression in store.expressions.items():
            self._visit(expression, {}, root, diagnostics, visited)
        for variable, definition in store.variables.items():
            for source in (
                *definition.choices,
                *definition.definitions,
                *definition.defaults,
            ):
                self._require(
                    store,
                    source.condition,
                    ValueType.boolean,
                    "Statement condition",
                    diagnostics,
                    variable,
                )
        for variable, definition in store.set_variables.items():
            for source in (
                *definition.bases,
                *definition.assigns,
                *definition.defaults,
            ):
                self._require(
                    store,
                    source.condition,
                    ValueType.boolean,
                    "Statement condition",
                    diagnostics,
                    variable,
                )
                expression = store.expressions[source.value]
                kind = self._types.get_type(expression)
                if not scalar_subset(kind, frozenset(ValueType)):
                    diagnostics.add(
                        Diagnostic(
                            DiagnosticSeverity.error,
                            "Set variable requires scalar elements",
                            variable,
                            ExpressionLocation(expression),
                        )
                    )
        for constraint in store.constraints:
            self._require(
                store,
                constraint.expr,
                ValueType.boolean,
                "Constraint expression",
                diagnostics,
            )
        for item in store.optimizations:
            self._require(
                store,
                item.expr,
                ValueType.integer,
                "Optimization expression",
                diagnostics,
            )
            self._require(
                store,
                item.condition,
                ValueType.boolean,
                "Optimization condition",
                diagnostics,
            )
        return frozenset(diagnostics)

    def _require(
        self,
        store: ConstraintStore,
        root: ExprId,
        required: ValueType,
        role: str,
        diagnostics: set[Diagnostic],
        variable: VariableRef | None = None,
    ) -> None:
        """Validate a statement's scalar contract without rejecting unknown types."""
        expression = store.expressions[root]
        if not scalar_subset(self._types.get_type(expression), frozenset({required})):
            diagnostics.add(
                Diagnostic(
                    DiagnosticSeverity.error,
                    f"{role} must be {required}",
                    variable,
                    ExpressionLocation(expression),
                )
            )

    def _visit(
        self,
        expression: Expr,
        bindings: Mapping[VariableRef, Type],
        root: ExprId,
        diagnostics: set[Diagnostic],
        visited: set[tuple[ExprId, Expr, TypeScope]],
    ) -> None:
        """Visit nested values and callable bodies under their lexical bindings."""
        key = (root, expression, frozenset(bindings.items()))
        if key in visited:
            return
        visited.add(key)
        location = ExpressionLocation(expression)
        if isinstance(expression, (tuple, frozenset)):
            for item in expression:
                self._visit(item, bindings, root, diagnostics, visited)
            op = (
                Operator.make_tuple
                if isinstance(expression, tuple)
                else Operator.set_make
            )
            operation = Operation(op, tuple(expression))
        elif isinstance(expression, Operation):
            operation = expression
        else:
            return
        kinds: list[Type] = []
        for index, arg in enumerate(operation.args):
            if isinstance(arg, (Lambda, Python)):
                kinds.append(UNKNOWN)
                allowed = index == 0 and operation.op in {
                    Operator.lambda_,
                    Operator.set_fold,
                    Operator.python_eval,
                }
                if not allowed:
                    diagnostics.add(
                        Diagnostic(
                            DiagnosticSeverity.error,
                            f"Expected value expression argument, got {type(arg).__name__}",
                            location=location,
                        )
                    )
                if isinstance(arg, Lambda):
                    self._visit_callable(
                        arg, operation, bindings, root, diagnostics, visited
                    )
            else:
                self._visit(arg, bindings, root, diagnostics, visited)
                kinds.append(self._types.get_type(arg, bindings))
        for message in operation_errors(operation, kinds):
            if (
                isinstance(expression, frozenset)
                and message == "set_make requires scalar arguments"
            ):
                message = "Set literal elements must be scalar values"
            diagnostics.add(
                Diagnostic(DiagnosticSeverity.error, message, location=location)
            )
        for message in operation_warnings(operation, kinds):
            diagnostics.add(
                Diagnostic(DiagnosticSeverity.warning, message, location=location)
            )

    def _visit_callable(
        self,
        callback: Lambda,
        operation: Operation,
        outer: Mapping[VariableRef, Type],
        root: ExprId,
        diagnostics: set[Diagnostic],
        visited: set[tuple[ExprId, Expr, TypeScope]],
    ) -> None:
        """Check callbacks even with unknown, empty, missing, or invalid arguments."""
        if operation.op == Operator.lambda_:
            argument_types: list[Type] = []
            for arg in operation.args[1:]:
                kind = (
                    UNKNOWN
                    if isinstance(arg, (Lambda, Python))
                    else self._types.get_type(arg, outer)
                )
                argument_types.append(
                    kind if isinstance(kind, UnknownType) or kind else UNKNOWN
                )
            argument_types = (argument_types + [UNKNOWN] * len(callback.vars))[
                : len(callback.vars)
            ]
            for local in lambda_bindings(callback, argument_types, outer):
                self._visit(callback.expr, local, root, diagnostics, visited)
            return
        if operation.op == Operator.set_fold and len(operation.args) == 3:
            set_arg, initial = operation.args[1:]
            collection = (
                UNKNOWN
                if isinstance(set_arg, (Lambda, Python))
                else self._types.get_type(set_arg, outer)
            )
            accumulator = (
                UNKNOWN
                if isinstance(initial, (Lambda, Python))
                else self._types.get_type(initial, outer)
            )
            elements: Type = UNKNOWN
            if not isinstance(collection, UnknownType) and all(
                isinstance(member, SetOf) for member in collection
            ):
                elements = (
                    frozenset(
                        element
                        for member in collection
                        if isinstance(member, SetOf)
                        for element in member.elements
                    )
                    or UNKNOWN
                )
            seen: set[Type] = set()
            while True:
                argument_types = (
                    [elements, accumulator] + [UNKNOWN] * len(callback.vars)
                )[: len(callback.vars)]
                body_types: list[Type] = []
                for local in lambda_bindings(
                    callback,
                    [
                        kind if isinstance(kind, UnknownType) or kind else UNKNOWN
                        for kind in argument_types
                    ],
                    outer,
                ):
                    self._visit(callback.expr, local, root, diagnostics, visited)
                    body_types.append(self._types.get_type(callback.expr, local))
                combined = union_types((accumulator, *body_types))
                if isinstance(accumulator, UnknownType) or combined == accumulator:
                    return
                if (
                    isinstance(combined, UnknownType)
                    or combined in seen
                    or any(
                        not isinstance(member, ValueType) and member not in accumulator
                        for member in combined
                    )
                ):
                    accumulator = UNKNOWN
                else:
                    seen.add(accumulator)
                    accumulator = combined
        local = dict(outer)
        local.update(dict.fromkeys(callback.vars, UNKNOWN))
        self._visit(callback.expr, local, root, diagnostics, visited)
