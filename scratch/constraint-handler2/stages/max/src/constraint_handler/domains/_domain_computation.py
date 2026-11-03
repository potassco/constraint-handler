"""Compute domains when requested and reuse table rows instead of evaluating twice."""

from __future__ import annotations

import math
from collections.abc import Callable, Mapping
from itertools import product
from typing import TYPE_CHECKING, cast

from ..diagnostics import Diagnostics, ExpressionLocation
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
    convert_expression,
)
from ..python_conversion import compile_python, convert
from ..python_input import FailIntegrityExn, Operator
from ..type_checking._type_inference import operand_contract, operation_arity
from ..util import free_variables
from ._domain import (
    EMPTY_DOMAIN,
    UNKNOWN_DOMAIN,
    Domain,
    DomainValue,
    PythonTable,
    domain_from_values,
    is_domain_value,
    is_finite_value,
    join_domains,
)
from ._evaluation import EnumerationDecision, bounded_product_decision
from ._integer import linear_integer
from ._symbolic import symbolic_operation
from .domain_cache import DomainTable

if TYPE_CHECKING:
    from .domain_cache import DomainCache, DomainScope

__all__ = ["_DomainComputation"]


class _DomainComputation:
    """Compute approximate domains through the cache and keep evaluated table rows."""

    def __init__(
        self,
        cache: DomainCache,
        store: ConstraintStore,
        threshold: int,
        boolean_threshold: int,
        python_context: Mapping[str, object],
        diagnostics: Diagnostics | None = None,
    ) -> None:
        """Keep evaluation settings and original variable sources for this session."""
        self.cache = cache
        self.store = store
        self.threshold = threshold
        self.python_context = python_context
        self.diagnostics = diagnostics if diagnostics is not None else Diagnostics()
        self.boolean_threshold = boolean_threshold
        self.relations: dict[
            tuple[str, str, tuple[Domain, ...]], tuple[PythonTable, Domain] | None
        ] = {}
        self.tables: dict[tuple[Expr, DomainScope], DomainTable | None] = {}
        self.programs: dict[
            tuple[ExprId, DomainScope], tuple[Expr, str, tuple[Expr, ...]]
        ] = {}
        self.callbacks: dict[str, Callable[..., object]] = {}
        self.sources = {
            variable: tuple(
                store.expressions[source.value]
                for source in (
                    *entries.choices,
                    *entries.definitions,
                    *entries.defaults,
                )
            )
            for variable, entries in store.variables.items()
        }
        self.set_sources = {
            variable: tuple(
                store.expressions[source.value]
                for source in (*entries.bases, *entries.assigns, *entries.defaults)
            )
            for variable, entries in store.set_variables.items()
        }

    def compute(self, expr: Expr, bindings: dict[VariableRef, Domain]) -> Domain:
        """Compute one domain, requesting operand and variable domains through the cache."""
        match expr:
            case ValueDef(_, value):
                if not is_domain_value(value):
                    return UNKNOWN_DOMAIN
                return domain_from_values((value,))
            case VariableRef():
                if expr in bindings:
                    return bindings[expr]
                if bindings:
                    return self.cache.get_domain(expr)
                if expr in self.set_sources:
                    base = join_domains(
                        self.cache.get_domain(source)
                        for source in self.set_sources[expr]
                    )
                    return Domain(set_base=self.filter(base, frozenset(ValueType)))
                if expr not in self.sources:
                    return UNKNOWN_DOMAIN
                return join_domains(
                    self.cache.get_domain(source) for source in self.sources[expr]
                )
            case tuple():
                return self.operation(Operator.make_tuple, expr, bindings, expr)
            case frozenset():
                return self.operation(Operator.set_make, tuple(expr), bindings, expr)
            case Operation(op, args):
                return self.operation(op, args, bindings, expr)
        raise TypeError("A callable descriptor is not a domain value expression")

    def argument(
        self, arg: OperationArg, bindings: dict[VariableRef, Domain]
    ) -> Domain:
        """Request an argument's domain; a bare Lambda or Python callable is not a value."""
        if isinstance(arg, (Lambda, Python)):
            return UNKNOWN_DOMAIN
        return self.cache.get_domain(arg, bindings)

    def operation(
        self,
        op: Operator,
        args: tuple[OperationArg, ...],
        bindings: dict[VariableRef, Domain],
        expr: Expr,
    ) -> Domain:
        """Compute an operator's domain directly or by table evaluation, as needed."""
        if not operation_arity(op, len(args)):
            return UNKNOWN_DOMAIN
        if op in {Operator.python_eval, Operator.set_fold}:
            table = self.table(expr, bindings)
            return UNKNOWN_DOMAIN if table is None else table.output_domain
        if op == Operator.lambda_:
            if not isinstance(args[0], Lambda):
                return UNKNOWN_DOMAIN
            callback = args[0]
            if len(callback.vars) != len(args) - 1:
                return UNKNOWN_DOMAIN
            domains = [self.argument(arg, bindings) for arg in args[1:]]
            decision = bounded_product_decision(domains, self.threshold)
            if decision == EnumerationDecision.EMPTY:
                return EMPTY_DOMAIN
            if decision != EnumerationDecision.ENUMERABLE:
                local = {**bindings, **dict(zip(callback.vars, domains, strict=True))}
                return self.cache.get_domain(callback.expr, local)
            results: list[Domain] = []
            for values in product(*(domain.iter_values() for domain in domains)):
                local = dict(bindings)
                local.update(
                    (parameter, domain_from_values((value,)))
                    for parameter, value in zip(callback.vars, values, strict=True)
                )
                results.append(self.cache.get_domain(callback.expr, local))
            return join_domains(results)
        if op in {Operator.ite, Operator.if_}:
            condition = self.argument(args[0], bindings)
            possibilities = {True, False} if condition.unknown else condition.bools
            branches: list[Domain] = []
            if True in possibilities:
                branches.append(self.argument(args[1], bindings))
            if False in possibilities:
                branches.append(
                    Domain(has_none=True)
                    if op == Operator.if_
                    else self.argument(args[2], bindings)
                )
            return join_domains(branches)
        if op in {Operator.conj, Operator.disj}:
            decisive = op == Operator.disj
            domains: list[Domain] = []
            for index, arg in enumerate(args):
                raw = self.argument(arg, bindings)
                self.check_operand(op, index, raw, expr)
                domain = self.filter(raw, operand_contract(op, index))
                if not domain.unknown and domain.bools == frozenset({decisive}):
                    return Domain(bools=frozenset({decisive}))
                domains.append(domain)
        else:
            raw = [self.argument(arg, bindings) for arg in args]
            for index, domain in enumerate(raw):
                self.check_operand(op, index, domain, expr)
            domains = [
                self.filter(domain, operand_contract(op, index))
                for index, domain in enumerate(raw)
            ]
        if op in {Operator.linear_integer, Operator.linear_comparison}:
            start = 1 if op == Operator.linear_comparison else 0
            terms = args[start:]
            if not terms:
                return domain_from_values((0,)) if not start else UNKNOWN_DOMAIN
            offset = terms[-1]
            if not isinstance(offset, ValueDef) or type(offset.value) is not int:
                return UNKNOWN_DOMAIN
            coefficients: list[int] = []
            term_domains: list[Domain] = []
            for term in terms[:-1]:
                if not isinstance(term, tuple) or len(term) != 2:
                    return UNKNOWN_DOMAIN
                coefficient = term[0]
                if (
                    not isinstance(coefficient, ValueDef)
                    or type(coefficient.value) is not int
                ):
                    return UNKNOWN_DOMAIN
                if coefficient.value == 0:
                    continue
                coefficients.append(coefficient.value)
                term_domains.append(
                    self.filter(
                        self.cache.get_domain(term[1], bindings),
                        frozenset({ValueType.integer}),
                    )
                )
            total = linear_integer(coefficients, term_domains, offset.value)
            if not start:
                return total
            relation = args[0]
            if not isinstance(relation, ValueDef) or relation.value not in {
                "eq",
                "neq",
                "lt",
                "leq",
                "gt",
                "geq",
            }:
                return UNKNOWN_DOMAIN
            op = Operator(str(relation.value))
            domains = [total, domain_from_values((0,))]
        if not any(domain.reals for domain in domains) or op in {
            Operator.set_make,
            Operator.make_tuple,
            Operator.length,
            Operator.tuple_get,
        }:
            result = symbolic_operation(op, domains, self.threshold)
            if result is not None:
                return result
        if (
            op in {Operator.eq, Operator.neq}
            and bounded_product_decision(domains, self.boolean_threshold)
            != EnumerationDecision.ENUMERABLE
        ):
            return Domain(bools=(True, False))
        table = self.table(expr, bindings)
        return UNKNOWN_DOMAIN if table is None else table.output_domain

    def filter(self, domain: Domain, allowed: frozenset[ValueType | str]) -> Domain:
        """Keep allowed value types without changing the operand's cached domain."""
        if domain.unknown:
            return domain
        return Domain(
            bools=domain.bools if ValueType.boolean in allowed else (),
            integers=domain.integers
            if ValueType.integer in allowed
            else type(domain.integers)(),
            reals=domain.reals if ValueType.real in allowed else (),
            has_none=domain.has_none and ValueType.none in allowed,
            strings=domain.strings if ValueType.string in allowed else (),
            tuple_domains=domain.tuple_domains if "tuple" in allowed else (),
            set_base=domain.set_base if "set" in allowed else None,
        )

    def check_operand(self, op: Operator, index: int, domain: Domain, expr: Expr) -> None:
        """Report operand kinds outside the operator's contract, grouped by kind."""
        if domain.unknown:
            return
        allowed = operand_contract(op, index)
        kinds = [
            name
            for kind, name, present in (
                (ValueType.boolean, "boolean", domain.bools),
                (ValueType.integer, "integer", domain.integers.intervals),
                (ValueType.real, "real", domain.reals),
                (ValueType.none, "none", domain.has_none),
                (ValueType.string, "string", domain.strings),
                ("tuple", "tuple", domain.tuple_domains),
                ("set", "set", domain.set_base is not None),
            )
            if present and kind not in allowed
        ]
        if not kinds:
            return
        location = self.location(expr)
        found = ", ".join(kinds)
        expected = "/".join(sorted(allowed))
        message = f"{op} operand {index + 1} has {found} values, expected {expected}"
        if any(
            item.message == message and item.location == location
            for item in self.diagnostics.items
        ):
            return
        self.diagnostics.error(message, location=location)

    def location(self, expr: Expr) -> ExpressionLocation:
        """Find a stored expression ID for an evaluation diagnostic when possible."""
        root = next(
            (root for root, value in self.store.expressions.items() if value == expr),
            -1,
        )
        return ExpressionLocation(root, expr)

    def table(
        self, expr: Expr, bindings: dict[VariableRef, Domain]
    ) -> DomainTable | None:
        """Find table inputs and reuse earlier rows, or an earlier unavailable result."""
        key = expr, frozenset(bindings.items())
        if key in self.tables:
            return self.tables[key]
        if isinstance(expr, Operation) and expr.op == Operator.python_eval:
            if not expr.args or not isinstance(expr.args[0], Python):
                self.tables[key] = None
                return None
            inputs = tuple(
                arg for arg in expr.args[1:] if not isinstance(arg, (Lambda, Python))
            )
            if len(inputs) != len(expr.args) - 1:
                self.tables[key] = None
                return None
            source = expr.args[0].fn
            for root, current in self.store.expressions.items():
                original = self.programs.get((root, key[1]))
                if (
                    current == expr
                    and original is not None
                    and (source, inputs) == original[1:]
                ):
                    result = self.table(original[0], bindings)
                    self.tables[key] = result
                    return result
        else:
            inputs = tuple(sorted(free_variables(expr), key=lambda var: var.name))
            source = convert(inputs, expr).fn
            for root, current in self.store.expressions.items():
                if current == expr:
                    self.programs[root, key[1]] = expr, source, inputs
        domains = tuple(self.cache.get_domain(arg, bindings) for arg in inputs)
        if (
            any(domain.is_empty() for domain in domains)
            and isinstance(expr, Operation)
            and expr.op
            in {
                Operator.ite,
                Operator.if_,
                Operator.conj,
                Operator.disj,
                Operator.limp,
                Operator.mult,
                Operator.linear_integer,
                Operator.linear_comparison,
            }
        ):
            self.tables[key] = None
            return None
        if isinstance(expr, Operation):
            for index, argument in enumerate(expr.args):
                if isinstance(argument, (Lambda, Python)) or argument not in inputs:
                    continue
                position = inputs.index(argument)
                domains = (
                    *domains[:position],
                    self.filter(domains[position], operand_contract(expr.op, index)),
                    *domains[position + 1 :],
                )
        relation = self.relation(source, domains, expr, inputs)
        result = (
            None
            if relation is None
            else DomainTable(inputs, domains, key[1], relation[0], relation[1])
        )
        self.tables[key] = result
        return result

    def relation(
        self,
        source: str,
        domains: tuple[Domain, ...],
        expr: Expr,
        inputs: tuple[Expr, ...],
    ) -> tuple[PythonTable, Domain] | None:
        """Check the input limit, then evaluate and cache rows and their output domain.

        Reuse this result for both domain queries and table queries. Return None
        when inputs are unknown, excessive, or cannot be evaluated completely.
        """
        key = (
            (
                "python"
                if isinstance(expr, Operation) and expr.op == Operator.python_eval
                else "expression"
            ),
            source,
            domains,
        )
        if key in self.relations:
            return self.relations[key]
        decision = bounded_product_decision(domains, self.threshold)
        if decision == EnumerationDecision.EMPTY:
            result: tuple[PythonTable, Domain] | None = (), EMPTY_DOMAIN
        elif decision != EnumerationDecision.ENUMERABLE:
            result = None
        else:
            rows: list[tuple[tuple[DomainValue, ...], DomainValue]] = []
            try:
                if any(domain.has_nonfinite_values() for domain in domains):
                    raise ValueError("Finite evaluation requires finite inputs")
                python_callback = (
                    self.callback(source)
                    if isinstance(expr, Operation) and expr.op == Operator.python_eval
                    else None
                )
                for values in product(*(domain.iter_values() for domain in domains)):
                    try:
                        if python_callback is not None:
                            value = python_callback(*values)
                        else:
                            value = self.evaluate(
                                expr, dict(zip(inputs, values, strict=True))
                            )
                    except FailIntegrityExn:
                        continue
                    except (
                        ArithmeticError,
                        LookupError,
                        TypeError,
                        ValueError,
                    ) as error:
                        self.diagnostics.error(
                            f"Domain evaluation failed for {values!r}: {error}",
                            location=self.location(expr),
                        )
                        continue
                    if isinstance(value, set):
                        value = frozenset(cast(set[object], value))
                    if not is_domain_value(value) or not is_finite_value(value):
                        raise ValueError("Unsupported or non-finite evaluation result")
                    rows.append((values, value))
                result = tuple(rows), domain_from_values(value for _, value in rows)
            except MemoryError, RecursionError:
                raise
            except (
                ArithmeticError,
                LookupError,
                TypeError,
                ValueError,
                NameError,
                SyntaxError,
                RuntimeError,
            ) as error:
                self.diagnostics.error(
                    f"Domain evaluation unavailable: {error}",
                    location=self.location(expr),
                )
                result = None
        self.relations[key] = result
        return result

    def callback(self, source: str) -> Callable[..., object]:
        """Compile a Python callable once using this session's context."""
        if source not in self.callbacks:
            callback: object = eval(
                compile_python(source), {"math": math, **self.python_context}
            )
            if not callable(callback):
                raise TypeError("Python source must evaluate to a callable")
            self.callbacks[source] = callback
        return self.callbacks[source]

    def evaluate(self, expr: Expr, values: dict[Expr, DomainValue]) -> DomainValue:
        """Evaluate one input combination, respecting lambda bindings and allowed types."""
        if expr in values:
            return values[expr]
        if isinstance(expr, ValueDef):
            if not is_domain_value(expr.value):
                raise ValueError("Unsupported literal value")
            return expr.value
        if isinstance(expr, VariableRef):
            raise FailIntegrityExn
        if isinstance(expr, (tuple, frozenset)):
            op = Operator.make_tuple if isinstance(expr, tuple) else Operator.set_make
            args: tuple[OperationArg, ...] = tuple(expr)
        else:
            op, args = expr.op, expr.args
        if not operation_arity(op, len(args)):
            raise FailIntegrityExn
        if op in {Operator.lambda_, Operator.set_fold}:
            if not isinstance(args[0], Lambda):
                raise FailIntegrityExn
            callback = args[0]
            if op == Operator.lambda_:
                if len(callback.vars) != len(args) - 1:
                    raise ValueError("Lambda parameter-count mismatch")
                supplied = [self.evaluate(cast(Expr, arg), values) for arg in args[1:]]
                local = dict(values)
                local.update(zip(callback.vars, supplied, strict=True))
                return self.evaluate(callback.expr, local)
            if len(callback.vars) != 2:
                raise ValueError("set_fold requires a Lambda with 2 parameters")
            members = self.evaluate(cast(Expr, args[1]), values)
            if not isinstance(members, frozenset):
                raise FailIntegrityExn
            accumulator = self.evaluate(cast(Expr, args[2]), values)
            for member in sorted(members, key=repr):
                local = dict(values)
                local.update(zip(callback.vars, (member, accumulator), strict=True))
                accumulator = self.evaluate(callback.expr, local)
            return accumulator
        if op in {Operator.ite, Operator.if_}:
            condition = self.evaluate(cast(Expr, args[0]), values)
            if type(condition) is not bool:
                raise FailIntegrityExn
            if condition:
                return self.evaluate(cast(Expr, args[1]), values)
            return (
                None
                if op == Operator.if_
                else self.evaluate(cast(Expr, args[2]), values)
            )
        evaluated: list[DomainValue] = []
        for index, arg in enumerate(args):
            if isinstance(arg, (Lambda, Python)):
                if op == Operator.python_eval and index == 0:
                    continue
                raise FailIntegrityExn
            value = self.evaluate(arg, values)
            domain = self.filter(
                domain_from_values((value,)), operand_contract(op, index)
            )
            if domain.is_empty():
                raise FailIntegrityExn
            evaluated.append(value)
            if op == Operator.conj and value is False:
                return False
            if op == Operator.disj and value is True:
                return True
            if op == Operator.mult and type(value) in {int, float} and value == 0:
                return 0
        if op == Operator.python_eval:
            if not isinstance(args[0], Python):
                raise FailIntegrityExn
            result = self.callback(args[0].fn)(*evaluated)
        else:
            parameters = tuple(
                VariableRef(f"__argument_{index}") for index in range(len(evaluated))
            )
            body = Operation(op, parameters)
            if op in {Operator.linear_integer, Operator.linear_comparison}:
                body = Operation(
                    op, tuple(convert_expression(value) for value in evaluated)
                )
                parameters = ()
            result = self.callback(convert(parameters, body).fn)(
                *(evaluated if parameters else ())
            )
        if isinstance(result, set):
            result = frozenset(cast(set[object], result))
        if not is_domain_value(result):
            raise ValueError("Unsupported evaluation result")
        return result
