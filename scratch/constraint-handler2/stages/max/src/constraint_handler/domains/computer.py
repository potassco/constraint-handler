"""Topological and scope-aware domain computation for internal expressions."""

from __future__ import annotations

import math
from collections.abc import Callable
from itertools import product
from typing import assert_never

from ..diagnostics import Diagnostics
from ..internal_input import (
    ConstraintStore,
    Expr,
    ExprId,
    Lambda,
    Operation,
    OperationArg,
    Python,
    ValueDef,
    ValueType,
    VariableRef,
)
from ..python_input import Operator
from ..util import EvaluationOrder
from .evaluation import EnumerationDecision, bounded_product_decision
from .operations import DomainOperationEvaluator
from .values import (
    DEFAULT_BOOLEAN_THRESHOLD,
    DEFAULT_THRESHOLD,
    EMPTY_DOMAIN,
    UNKNOWN_DOMAIN,
    Domain,
    DomainStore,
    DomainValue,
    SetValue,
    domain_from_values,
    has_value_collisions,
    is_domain_value,
    is_finite_value,
    join_domains,
)

type ScopedDomainHandler = Callable[[tuple[OperationArg, ...], dict[VariableRef, Domain], ExprId | None], Domain]


class _DomainComputer:
    """Traverse expressions in dependency order and retain binding-specific domains."""

    def __init__(
        self,
        store: ConstraintStore,
        order: EvaluationOrder,
        diagnostics: Diagnostics,
        threshold: int,
        boolean_threshold: int,
    ) -> None:
        """Initialize the domain computer with evaluation order, thresholds, and diagnostics."""
        self._store = store
        self._order = order
        self._diagnostics = diagnostics
        self._threshold = threshold
        self._result = DomainStore()
        self._operations = DomainOperationEvaluator(diagnostics, threshold, boolean_threshold)

        self._scoped_handlers: dict[Operator, ScopedDomainHandler] = {
            Operator.python_eval: self._visit_python_call,
            Operator.lambda_: self._visit_lambda_call,
            Operator.set_fold: self._visit_set_fold,
            Operator.linear_integer: self._visit_linear_integer,
        }

    def run(self) -> DomainStore:
        """Compute domains using the shared topological evaluation schedule."""
        order = self._order

        for var in self._store.variables:
            if var not in order.defining_exprs:
                self._result[var] = EMPTY_DOMAIN
        for var in self._store.set_variables:
            if var not in order.defining_exprs:
                self._result[var] = Domain(explicit_sets=frozenset({frozenset()}))

        for expr_id, ready_variables in order.evaluation_steps():
            expr = self._store.expressions[expr_id]
            self._visit_expr(expr, {}, expr_id)
            for var in ready_variables:
                self._compute_variable_domain(var)

        for expr_id in order.cyclic_exprs:
            self._result[self._store.expressions[expr_id]] = UNKNOWN_DOMAIN
        for var in set(self._store.variables) | set(self._store.set_variables):
            if var not in self._result:
                self._result[var] = UNKNOWN_DOMAIN

        return self._result

    def _compute_variable_domain(self, var: VariableRef) -> None:
        """Combine defining expression domains into the variable's Domain."""
        if var in self._store.set_variables:
            set_var = self._store.set_variables[var]
            elem_doms = [
                *(self._result[self._store.expressions[b.value]] for b in set_var.bases),
                *(self._result[self._store.expressions[a.value]] for a in set_var.assigns),
                *(self._result[self._store.expressions[d.value]] for d in set_var.defaults),
            ]
            if any(d.unknown for d in elem_doms):
                self._result[var] = UNKNOWN_DOMAIN
                return
            combined_elems = join_domains(elem_doms, self._threshold)
            if combined_elems.unknown or combined_elems.int_range is not None:
                self._result[var] = UNKNOWN_DOMAIN
                return
            scalars: list[SetValue] = []
            for val in combined_elems.iter_values():
                if isinstance(val, frozenset):
                    self._diagnostics.error(
                        f"Nested sets are not supported in set variable {var.name!r}",
                        variable=var,
                    )
                    self._result[var] = UNKNOWN_DOMAIN
                    return
                scalars.append(val)
            if has_value_collisions(scalars):
                self._diagnostics.warn(
                    "Set variable contains values that Python sets cannot distinguish; returning unknown",
                    variable=var,
                )
                self._result[var] = UNKNOWN_DOMAIN
                return
            self._result[var] = Domain(implicit_set_elements=frozenset(scalars))
            return

        variable = self._store.variables[var]
        def_doms = [
            *(self._result[self._store.expressions[c.value]] for c in variable.choices),
            *(self._result[self._store.expressions[d.value]] for d in variable.definitions),
            *(self._result[self._store.expressions[d.value]] for d in variable.defaults),
        ]
        self._result[var] = join_domains(def_doms, self._threshold)
        if self._result[var].unknown and has_value_collisions(
            value for dom in def_doms for value in (*dom.tuples, *dom.explicit_sets)
        ):
            self._diagnostics.warn(
                "Variable alternatives contain values that Python sets cannot distinguish; returning unknown",
                variable=var,
            )

    def _visit_expr(
        self,
        expr: Expr,
        env: dict[VariableRef, Domain],
        expr_id: ExprId | None,
    ) -> Domain:
        """Retain every visited subexpression's domain in its binding context."""
        result = self._compute_expr(expr, env, expr_id)
        self._result.record(expr, result, scope=frozenset(env.items()))
        return result

    def _compute_expr(
        self,
        expr: Expr,
        env: dict[VariableRef, Domain],
        expr_id: ExprId | None,
    ) -> Domain:
        """Compute the sound Domain of an internal expression."""
        match expr:
            case ValueDef(value_type, value):
                match value_type:
                    case ValueType.boolean:
                        return Domain(bools=frozenset({bool(value)}))
                    case ValueType.integer:
                        assert isinstance(value, int)
                        return Domain(ints=frozenset({value}))
                    case ValueType.real:
                        assert isinstance(value, (int, float))
                        return Domain(reals=frozenset({float(value)}))
                    case ValueType.string:
                        assert isinstance(value, str)
                        return Domain(strings=frozenset({value}))
                    case ValueType.none:
                        return Domain(has_none=True)
            case VariableRef():
                if expr in env:
                    return env[expr]
                return self._result.get(expr, UNKNOWN_DOMAIN)
            case frozenset():
                return self._visit_set_expr(tuple(expr), env, expr_id)
            case tuple():
                return self._visit_tuple_expr(expr, env, expr_id)
            case Operation(op, args):
                return self._visit_operation(op, args, env, expr_id)
        assert_never(expr)

    def _visit_set_expr(
        self,
        items: tuple[Expr, ...],
        env: dict[VariableRef, Domain],
        expr_id: ExprId | None,
    ) -> Domain:
        """Compute the domain of a set literal or set_make operation."""
        item_doms = [self._visit_expr(item, env, expr_id) for item in items]
        return self._operations.evaluate(Operator.set_make, item_doms, expr_id)

    def _visit_tuple_expr(
        self,
        items: tuple[Expr, ...],
        env: dict[VariableRef, Domain],
        expr_id: ExprId | None,
    ) -> Domain:
        """Compute the domain of a tuple expression {(v1,...,vn) | vi in D(ei)}."""
        if not items:
            return Domain(tuples=frozenset({()}))
        item_doms = [self._visit_expr(item, env, expr_id) for item in items]
        decision = bounded_product_decision(item_doms, self._threshold)
        if decision in (EnumerationDecision.UNKNOWN, EnumerationDecision.EXCESSIVE):
            return UNKNOWN_DOMAIN
        if decision == EnumerationDecision.EMPTY:
            return EMPTY_DOMAIN
        value_lists: list[list[SetValue]] = []
        for d in item_doms:
            vals: list[SetValue] = []
            for v in d.iter_values():
                if isinstance(v, frozenset):
                    self._diagnostics.error("Sets inside tuples are not supported", expr_id=expr_id)
                    return UNKNOWN_DOMAIN
                vals.append(v)
            value_lists.append(vals)
        result = domain_from_values(product(*value_lists))
        if result.unknown:
            self._diagnostics.warn(
                "Tuple alternatives contain values that Python sets cannot distinguish; returning unknown",
                expr_id=expr_id,
            )
        return result

    def _visit_arg(
        self,
        arg: OperationArg,
        env: dict[VariableRef, Domain],
        expr_id: ExprId | None,
    ) -> Domain:
        """Evaluate an OperationArg that is expected to be an expression."""
        if isinstance(arg, (Lambda, Python)):
            self._diagnostics.error(
                f"{type(arg).__name__} is not a value and has no domain",
                expr_id=expr_id,
            )
            return UNKNOWN_DOMAIN
        return self._visit_expr(arg, env, expr_id)

    def _visit_operation(
        self,
        op: Operator,
        args: tuple[OperationArg, ...],
        env: dict[VariableRef, Domain],
        expr_id: ExprId | None,
    ) -> Domain:
        """Dispatch domain computation for an Operation."""
        handler = self._scoped_handlers.get(op)
        if handler is not None:
            return handler(args, env, expr_id)

        doms = [self._visit_arg(arg, env, expr_id) for arg in args]

        return self._operations.evaluate(op, doms, expr_id)

    def _visit_linear_integer(
        self,
        args: tuple[OperationArg, ...],
        env: dict[VariableRef, Domain],
        expr_id: ExprId | None,
    ) -> Domain:
        """Compute domain for Operation(LinearInteger, [(c1, x1), ..., (cn, xn), c])."""
        if not args:
            self._diagnostics.error("linear_integer requires at least 1 argument", expr_id=expr_id)
            return UNKNOWN_DOMAIN
        coeffs: list[int] = []
        term_doms: list[Domain] = []
        offset = 0

        for idx, arg in enumerate(args):
            if isinstance(arg, tuple) and len(arg) == 2:
                coeff_expr, term_expr = arg
                if not isinstance(coeff_expr, ValueDef) or coeff_expr.value_type != ValueType.integer:
                    self._diagnostics.error(
                        "linear_integer coefficient must be a constant integer literal",
                        expr_id=expr_id,
                    )
                    return UNKNOWN_DOMAIN
                self._visit_expr(coeff_expr, env, expr_id)
                term_domain = self._visit_expr(term_expr, env, expr_id)
                scope = frozenset(env.items())
                c_dom = self._result.lookup(coeff_expr, scope=scope)
                if c_dom.unknown or c_dom.cardinality() != 1:
                    self._diagnostics.error(
                        "linear_integer coefficient must be a constant integer literal",
                        expr_id=expr_id,
                    )
                    return UNKNOWN_DOMAIN
                c_val = next(c_dom.iter_values())
                if not isinstance(c_val, int) or isinstance(c_val, bool):
                    self._diagnostics.error("linear_integer coefficient must be integer", expr_id=expr_id)
                    return UNKNOWN_DOMAIN
                coeffs.append(c_val)
                term_doms.append(term_domain)
                count = term_domain.cardinality()
                pair_domain = UNKNOWN_DOMAIN
                if (
                    count is not None
                    and count <= self._threshold
                    and not term_domain.explicit_sets
                    and term_domain.implicit_set_elements is None
                ):
                    pair_domain = domain_from_values(
                        (c_val, value) for value in term_domain.iter_values() if not isinstance(value, frozenset)
                    )
                self._result.record(arg, pair_domain, scope=scope)
            elif idx == len(args) - 1 and not isinstance(arg, (Lambda, Python, tuple)):
                if not isinstance(arg, ValueDef) or arg.value_type != ValueType.integer:
                    self._diagnostics.error(
                        "linear_integer constant offset must be a constant integer literal",
                        expr_id=expr_id,
                    )
                    return UNKNOWN_DOMAIN
                off_dom = self._visit_expr(arg, env, expr_id)
                if off_dom.unknown or off_dom.cardinality() != 1:
                    self._diagnostics.error(
                        "linear_integer constant offset must be a constant literal",
                        expr_id=expr_id,
                    )
                    return UNKNOWN_DOMAIN
                off_val = next(off_dom.iter_values())
                if not isinstance(off_val, int) or isinstance(off_val, bool):
                    self._diagnostics.error(
                        "linear_integer constant offset must be integer",
                        expr_id=expr_id,
                    )
                    return UNKNOWN_DOMAIN
                offset = off_val
            else:
                self._diagnostics.error(
                    f"Invalid linear_integer argument at position {idx}",
                    expr_id=expr_id,
                )
                return UNKNOWN_DOMAIN

        return self._operations.linear_integer(coeffs, term_doms, offset, expr_id)

    def _visit_lambda_call(
        self,
        args: tuple[OperationArg, ...],
        env: dict[VariableRef, Domain],
        expr_id: ExprId | None,
    ) -> Domain:
        """Compute domain for Operation(LambdaCall, [Lambda(vars, body), a1, ..., an])."""
        if not args or not isinstance(args[0], Lambda):
            self._diagnostics.error("lambda_ requires a Lambda as first argument", expr_id=expr_id)
            return UNKNOWN_DOMAIN
        lam = args[0]
        call_args = args[1:]
        if len(call_args) != len(lam.vars):
            self._diagnostics.error(
                f"Lambda expects {len(lam.vars)} arguments, got {len(call_args)}",
                expr_id=expr_id,
            )
            return UNKNOWN_DOMAIN
        arg_doms = [self._visit_arg(a, env, expr_id) for a in call_args]
        decision = bounded_product_decision(arg_doms, self._threshold)
        if decision in (EnumerationDecision.UNKNOWN, EnumerationDecision.EXCESSIVE):
            return UNKNOWN_DOMAIN
        if decision == EnumerationDecision.EMPTY:
            return EMPTY_DOMAIN
        branch_doms: list[Domain] = []
        for combo in product(*(d.iter_values() for d in arg_doms)):
            local_env = dict(env)
            for param, val in zip(lam.vars, combo, strict=True):
                local_env[param] = domain_from_values((val,))
            branch_doms.append(self._visit_expr(lam.expr, local_env, expr_id))
        return join_domains(branch_doms, self._threshold)

    def _visit_python_call(
        self,
        args: tuple[OperationArg, ...],
        env: dict[VariableRef, Domain],
        expr_id: ExprId | None,
    ) -> Domain:
        """Compute domain for Operation(PythonEval, [Python(fn), ...])."""
        if not args or not isinstance(args[0], Python):
            self._diagnostics.error(
                "python_eval requires a Python callable as first argument",
                expr_id=expr_id,
            )
            return UNKNOWN_DOMAIN
        arg_domains = [self._visit_arg(arg, env, expr_id) for arg in args[1:]]
        decision = bounded_product_decision(arg_domains, self._threshold)
        if decision in (EnumerationDecision.UNKNOWN, EnumerationDecision.EXCESSIVE):
            return UNKNOWN_DOMAIN
        if decision == EnumerationDecision.EMPTY:
            return EMPTY_DOMAIN
        results: list[DomainValue] = []
        try:
            if any(domain.has_nonfinite_values() for domain in arg_domains):
                raise ValueError("non-finite real input")
            callback: object = eval(args[0].fn, {"math": math})
            if not callable(callback):
                raise TypeError("Python source must evaluate to a callable")
            for values in product(*(domain.iter_values() for domain in arg_domains)):
                value = callback(*values)
                if not is_domain_value(value):
                    raise TypeError(f"unsupported Python result type: {type(value).__name__}")
                if not is_finite_value(value):
                    raise ValueError("non-finite real result")
                results.append(value)
        except Exception as error:
            if isinstance(error, (MemoryError, RecursionError)):
                raise
            self._diagnostics.warn(f"python_eval domain evaluation failed: {error}", expr_id=expr_id)
            return UNKNOWN_DOMAIN
        return join_domains((domain_from_values(results),), self._threshold)

    def _visit_set_fold(
        self,
        args: tuple[OperationArg, ...],
        env: dict[VariableRef, Domain],
        expr_id: ExprId | None,
    ) -> Domain:
        """Fold in repr order, as specified, including for heterogeneous members."""
        if len(args) != 3:
            self._diagnostics.error(
                f"set_fold expects 3 arguments, got {len(args)}",
                expr_id=expr_id,
            )
            return UNKNOWN_DOMAIN
        callback, set_arg, init_arg = args
        ds = self._visit_arg(set_arg, env, expr_id)
        dz = self._visit_arg(init_arg, env, expr_id)
        if not isinstance(callback, Lambda) or len(callback.vars) != 2:
            if isinstance(callback, Python):
                self._diagnostics.warn(
                    "set_fold domain evaluation supports only Lambda callbacks; returning unknown",
                    expr_id=expr_id,
                )
            elif isinstance(callback, Lambda):
                self._diagnostics.error("set_fold Lambda expects 2 parameters", expr_id=expr_id)
            else:
                self._diagnostics.error(
                    "set_fold first argument must be a callable",
                    expr_id=expr_id,
                )
            return UNKNOWN_DOMAIN
        if ds.unknown or dz.unknown:
            return UNKNOWN_DOMAIN
        if ds.is_empty() or dz.is_empty():
            return EMPTY_DOMAIN
        if bounded_product_decision((ds, dz), self._threshold) != EnumerationDecision.ENUMERABLE:
            return UNKNOWN_DOMAIN
        results: list[Domain] = []
        sets = [s for s in ds.iter_values() if isinstance(s, frozenset)]
        if not sets:
            self._diagnostics.error("set_fold requires a set argument", expr_id=expr_id)
            return UNKNOWN_DOMAIN
        for s_val, z_val in product(sets, dz.iter_values()):
            acc_dom = domain_from_values((z_val,))
            for elem in sorted(s_val, key=repr):
                elem_dom = domain_from_values((elem,))
                local_env = dict(env)
                local_env[callback.vars[0]] = acc_dom
                local_env[callback.vars[1]] = elem_dom
                acc_dom = self._visit_expr(callback.expr, local_env, expr_id)
                if acc_dom.unknown:
                    return UNKNOWN_DOMAIN
            results.append(acc_dom)
        return join_domains(results, self._threshold)


def compute_domains(
    store: ConstraintStore,
    order: EvaluationOrder,
    diagnostics: Diagnostics,
    *,
    threshold: int = DEFAULT_THRESHOLD,
    boolean_threshold: int = DEFAULT_BOOLEAN_THRESHOLD,
) -> DomainStore:
    """Compute a sound Domain for every variable and expression in the store."""
    return _DomainComputer(store, order, diagnostics, threshold, boolean_threshold).run()
