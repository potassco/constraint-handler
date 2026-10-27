"""Static type computation and representation for variables and expressions."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from itertools import product
from math import inf
from typing import Final, Literal, assert_never, final

from .analysis import (
    ExpressionStore,
    lambda_call,
    linear_comparison_arguments,
    linear_integer_arguments,
)
from .diagnostics import Diagnostics, ExpressionLocation
from .internal_input import (
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
from .python_input import Operator
from .util import EvaluationOrder


@dataclass(frozen=True, slots=True)
class SetOf:
    """Represent a non-nested set type with scalar member types and emptiness flag."""

    elements: frozenset[ValueType]
    can_be_empty: bool


@dataclass(frozen=True, slots=True)
class TupleType:
    """Represent a fixed-length tuple type with per-position static types."""

    elements: tuple[Type, ...]


@final
@dataclass(frozen=True, slots=True)
class UnknownType:
    """Represent an absorbing unknown static type."""

    def __new__(cls) -> UnknownType:
        """Return the shared immutable unknown marker."""
        return UNKNOWN


UNKNOWN: Final = object.__new__(UnknownType)


type TypeMember = ValueType | SetOf | TupleType
type Type = frozenset[TypeMember] | UnknownType
type TypeScope = frozenset[tuple[VariableRef, Type]]

_NUMERIC_TYPES: frozenset[ValueType] = frozenset({ValueType.integer, ValueType.real})
_ORDERED_TYPES: frozenset[ValueType] = frozenset(
    {ValueType.boolean, ValueType.integer, ValueType.real}
)
_BOOL_OR_NONE_TYPES: frozenset[ValueType] = frozenset(
    {ValueType.boolean, ValueType.none}
)


@dataclass(frozen=True, slots=True)
class _ScalarRule:
    """Describe scalar arity, accepted members, and result construction."""

    minimum: int
    maximum: int | float
    allowed: frozenset[ValueType]
    result: ValueType | Literal["identity", "union", "arithmetic", "power"]
    contract: str


_SCALAR_RULES: dict[Operator, _ScalarRule] = {
    Operator.concat: _ScalarRule(
        2, 2, frozenset({ValueType.string}), ValueType.string, "2 string arguments"
    ),
    **{
        op: _ScalarRule(
            1, inf, _ORDERED_TYPES, "union", "at least 1 boolean/integer/real argument"
        )
        for op in (Operator.min, Operator.max)
    },
    **{
        op: _ScalarRule(1, 1, _NUMERIC_TYPES, "identity", "1 numeric argument")
        for op in (Operator.abs, Operator.minus)
    },
    **{
        op: _ScalarRule(1, 1, _NUMERIC_TYPES, ValueType.real, "1 numeric argument")
        for op in (
            Operator.sqrt,
            Operator.cos,
            Operator.sin,
            Operator.tan,
            Operator.acos,
            Operator.asin,
            Operator.atan,
        )
    },
    **{
        op: _ScalarRule(1, 1, _NUMERIC_TYPES, ValueType.integer, "1 numeric argument")
        for op in (Operator.floor, Operator.ceil)
    },
    **{
        op: _ScalarRule(
            1, inf, _NUMERIC_TYPES, "arithmetic", "at least 1 numeric argument"
        )
        for op in (Operator.add, Operator.mult)
    },
    **{
        op: _ScalarRule(2, 2, _NUMERIC_TYPES, "arithmetic", "2 numeric arguments")
        for op in (Operator.sub, Operator.mod)
    },
    Operator.int_div: _ScalarRule(
        2, 2, _NUMERIC_TYPES, ValueType.integer, "2 numeric arguments"
    ),
    Operator.real_div: _ScalarRule(
        2, 2, _NUMERIC_TYPES, ValueType.real, "2 numeric arguments"
    ),
    Operator.pow: _ScalarRule(2, 2, _NUMERIC_TYPES, "power", "2 numeric arguments"),
    **{
        op: _ScalarRule(2, 2, _ORDERED_TYPES, ValueType.boolean, "2 ordered arguments")
        for op in (Operator.leq, Operator.lt, Operator.geq, Operator.gt)
    },
    Operator.real_from_int: _ScalarRule(
        1, 1, frozenset({ValueType.integer}), ValueType.real, "1 integer argument"
    ),
    Operator.int_from_real: _ScalarRule(
        1, 1, frozenset({ValueType.real}), ValueType.integer, "1 real argument"
    ),
    **{
        op: _ScalarRule(
            0,
            inf,
            frozenset({ValueType.boolean}),
            ValueType.boolean,
            "boolean arguments",
        )
        for op in (Operator.conj, Operator.disj, Operator.lxor, Operator.leqv)
    },
    Operator.limp: _ScalarRule(
        2, 2, frozenset({ValueType.boolean}), ValueType.boolean, "2 boolean arguments"
    ),
    Operator.lnot: _ScalarRule(
        1, 1, frozenset({ValueType.boolean}), ValueType.boolean, "1 boolean argument"
    ),
    **{
        op: _ScalarRule(
            1, 1, _BOOL_OR_NONE_TYPES, ValueType.boolean, "1 boolean or none argument"
        )
        for op in (Operator.snot, Operator.wnot)
    },
}


class StaticTypeStore(ExpressionStore[Type]):
    """Own global and lambda-scoped types through an expression mapping interface."""


def union_types(types: Iterable[Type]) -> Type:
    """Combine static types, absorbing into UnknownType if any input is unknown."""
    members: set[TypeMember] = set()
    set_elements: set[ValueType] = set()
    has_set = False
    set_can_be_empty = False
    for item in types:
        if isinstance(item, UnknownType):
            return UnknownType()
        for member in item:
            if isinstance(member, SetOf):
                has_set = True
                set_elements.update(member.elements)
                set_can_be_empty = set_can_be_empty or member.can_be_empty
            else:
                members.add(member)
    if has_set:
        members.add(SetOf(frozenset(set_elements), set_can_be_empty))
    return frozenset(members)


def _is_subset_of_scalars(t: Type, allowed: frozenset[ValueType]) -> bool:
    """Check whether all members of a known type are within the allowed scalar set."""
    if isinstance(t, UnknownType):
        return True
    return all(isinstance(m, ValueType) and m in allowed for m in t)


def _is_all_sets(t: Type) -> bool:
    """Check whether all members of a known type are SetOf instances."""
    if isinstance(t, UnknownType):
        return True
    return all(isinstance(m, SetOf) for m in t)


def _is_all_scalars(t: Type) -> bool:
    """Check whether all members of a known type are scalar ValueTypes."""
    if isinstance(t, UnknownType):
        return True
    return all(isinstance(m, ValueType) for m in t)


def _extract_set_info(t: frozenset[TypeMember]) -> tuple[frozenset[ValueType], bool]:
    """Extract combined element types and can_be_empty flag from SetOf members."""
    elems: set[ValueType] = set()
    can_be_empty = False
    for m in t:
        if isinstance(m, SetOf):
            elems.update(m.elements)
            can_be_empty = can_be_empty or m.can_be_empty
    return frozenset(elems), can_be_empty


class _StaticTypeComputer:
    """Internal visitor computing static types for expressions and variables."""

    def __init__(
        self,
        store: ConstraintStore,
        order: EvaluationOrder,
        diagnostics: Diagnostics,
    ) -> None:
        """Initialize the type computer with a store, evaluation order, and diagnostics sink."""
        self._store = store
        self._order = order
        self._diagnostics = diagnostics
        self._result = StaticTypeStore()

    def run(self) -> StaticTypeStore:
        """Execute topological static type computation over the store."""
        order = self._order

        for var in self._store.variables:
            if var not in order.defining_exprs:
                self._result[var] = frozenset()
        for var in self._store.set_variables:
            if var not in order.defining_exprs:
                self._result[var] = frozenset({SetOf(frozenset(), True)})

        for expr_id, ready_variables in order.evaluation_steps():
            expr = self._store.expressions[expr_id]
            self._eval_expr(expr, {}, expr_id)
            for var in ready_variables:
                self._compute_variable_type(var)

        for expr_id in order.cyclic_exprs:
            self._result[self._store.expressions[expr_id]] = UnknownType()
        for var in set(self._store.variables) | set(self._store.set_variables):
            if var not in self._result:
                self._result[var] = UnknownType()

        return self._result

    def _compute_variable_type(self, var: VariableRef) -> None:
        """Combine choices, definitions, and defaults for a variable."""
        types: list[Type] = []
        if var in self._store.set_variables:
            set_var = self._store.set_variables[var]
            sources = [
                *(
                    self._result[self._store.expressions[b.value]]
                    for b in set_var.bases
                ),
                *(
                    self._result[self._store.expressions[a.value]]
                    for a in set_var.assigns
                ),
                *(
                    self._result[self._store.expressions[d.value]]
                    for d in set_var.defaults
                ),
            ]
            elem_types = frozenset(
                member
                for kind in sources
                if not isinstance(kind, UnknownType)
                for member in kind
            )
            scalars: set[ValueType] = set()
            invalid = False
            for m in elem_types:
                if isinstance(m, ValueType):
                    scalars.add(m)
                else:
                    invalid = True
                    self._diagnostics.error(
                        f"Set variable {var.name!r} requires scalar elements, got {m}",
                        variable=var,
                    )
            if invalid or any(isinstance(kind, UnknownType) for kind in sources):
                types.append(UNKNOWN)
            else:
                can_be_empty = not any(
                    self._store.expressions[assignment.condition]
                    == ValueDef(ValueType.boolean, True)
                    for assignment in set_var.assigns
                )
                types.append(frozenset({SetOf(frozenset(scalars), can_be_empty)}))

        if var in self._store.variables:
            variable = self._store.variables[var]
            types.extend(
                self._result[self._store.expressions[source.value]]
                for source in (
                    *variable.choices,
                    *variable.definitions,
                    *variable.defaults,
                )
            )
        self._result[var] = union_types(types)

    def _eval_expr(
        self,
        expr: Expr,
        env: dict[VariableRef, Type],
        root_id: ExprId,
    ) -> Type:
        """Retain every visited subexpression's type in its binding context."""
        result = self._compute_expr(expr, env, ExpressionLocation(root_id, expr))
        self._result.record(expr, result, scope=frozenset(env.items()))
        return result

    def _compute_expr(
        self,
        expr: Expr,
        env: dict[VariableRef, Type],
        location: ExpressionLocation,
    ) -> Type:
        """Compute the static type of an internal expression."""
        match expr:
            case ValueDef(value_type, _):
                return frozenset({value_type})
            case VariableRef():
                if expr in env:
                    return env[expr]
                return self._result.get(expr, UnknownType())
            case frozenset():
                if not expr:
                    return frozenset({SetOf(frozenset(), True)})
                element_types = [
                    self._eval_expr(item, env, location.root_id) for item in expr
                ]
                if not all(_is_all_scalars(kind) for kind in element_types):
                    self._diagnostics.error(
                        "Set literal elements must be scalar values",
                        location=location,
                    )
                    return UnknownType()
                item_types = union_types(element_types)
                if isinstance(item_types, UnknownType):
                    return UnknownType()
                if any(not kind for kind in element_types):
                    return frozenset()
                scalars = frozenset(m for m in item_types if isinstance(m, ValueType))
                return frozenset({SetOf(scalars, False)})
            case tuple():
                elem_types = tuple(
                    self._eval_expr(item, env, location.root_id) for item in expr
                )
                if any(
                    isinstance(member, SetOf)
                    for kind in elem_types
                    if not isinstance(kind, UnknownType)
                    for member in kind
                ):
                    self._diagnostics.error(
                        "Sets inside tuples are not supported", location=location
                    )
                    return UNKNOWN
                if any(isinstance(t, UnknownType) for t in elem_types):
                    return UnknownType()
                if any(
                    len(t) == 0 for t in elem_types if not isinstance(t, UnknownType)
                ):
                    return frozenset()
                return frozenset({TupleType(elem_types)})
            case Operation(op, args):
                return self._eval_operation(op, args, env, location)
        assert_never(expr)

    def _eval_expr_arg(
        self,
        arg: OperationArg,
        env: dict[VariableRef, Type],
        location: ExpressionLocation,
    ) -> Type:
        """Evaluate an operation argument that must be an expression."""
        if isinstance(arg, (Lambda, Python)):
            self._diagnostics.error(
                f"Expected value expression argument, got {type(arg).__name__}",
                location=location,
            )
            return UnknownType()
        return self._eval_expr(arg, env, location.root_id)

    def _eval_operation(
        self,
        op: Operator,
        args: tuple[OperationArg, ...],
        env: dict[VariableRef, Type],
        location: ExpressionLocation,
    ) -> Type:
        """Compute the result type of an Operation according to the type table."""
        match op:
            case Operator.python_eval:
                if not args or not isinstance(args[0], Python):
                    self._diagnostics.error(
                        "python_eval requires a Python callable as first argument",
                        location=location,
                    )
                for arg in args[1:]:
                    self._eval_expr_arg(arg, env, location)
                return UnknownType()

            case Operator.set_fold:
                return self._eval_set_fold(args, env, location)

            case Operator.lambda_:
                lam = lambda_call(args, self._diagnostics, location)
                if lam is None:
                    return UNKNOWN
                arg_types = [
                    self._eval_expr_arg(arg, env, location) for arg in args[1:]
                ]
                return self._apply_lambda(lam, arg_types, env, location)

            case Operator.linear_integer:
                return self._eval_linear_integer(args, env, location)

            case Operator.linear_comparison:
                if (
                    linear_comparison_arguments(args, self._diagnostics, location)
                    is None
                ):
                    return UNKNOWN
                self._eval_expr_arg(args[0], env, location)
                kind = self._eval_linear_integer(args[1:], env, location)
                return (
                    kind
                    if isinstance(kind, UnknownType) or not kind
                    else frozenset({ValueType.boolean})
                )

            case _:
                pass

        arg_types = [self._eval_expr_arg(arg, env, location) for arg in args]
        if op in _SCALAR_RULES:
            return self._eval_scalar_operation(op, arg_types, location)
        return self._eval_value_operation(op, args, arg_types, location)

    def _apply_lambda(
        self,
        callback: Lambda,
        arg_types: list[Type],
        env: dict[VariableRef, Type],
        location: ExpressionLocation,
    ) -> Type:
        """Check a lambda under each binding combination, including unknown arguments."""
        if not self._check_contract(
            len(set(callback.vars)) == len(callback.vars),
            "Lambda parameter names must be distinct",
            location,
        ):
            return UNKNOWN
        alternatives: list[Iterable[TypeMember | UnknownType]] = [
            (kind,) if isinstance(kind, UnknownType) else kind for kind in arg_types
        ]
        results: list[Type] = []
        for combination in product(*alternatives):
            local_env = dict(env)
            for parameter, member in zip(callback.vars, combination, strict=True):
                local_env[parameter] = (
                    member if isinstance(member, UnknownType) else frozenset({member})
                )
            results.append(self._eval_expr(callback.expr, local_env, location.root_id))
        if any(isinstance(kind, UnknownType) for kind in arg_types):
            return UNKNOWN
        return union_types(results)

    def _eval_set_fold(
        self,
        args: tuple[OperationArg, ...],
        env: dict[VariableRef, Type],
        location: ExpressionLocation,
    ) -> Type:
        """Check fold callbacks to a scalar fixed point, widening structural growth."""
        if not self._check_contract(
            len(args) == 3, f"set_fold expects 3 arguments, got {len(args)}", location
        ):
            return UNKNOWN
        callback, set_arg, init_arg = args
        set_type = self._eval_expr_arg(set_arg, env, location)
        accumulator = self._eval_expr_arg(init_arg, env, location)
        valid_set = self._check_contract(
            _is_all_sets(set_type),
            f"set_fold requires a set argument, got {set_type}",
            location,
        )
        if not self._check_contract(
            isinstance(callback, (Lambda, Python)),
            "set_fold first argument must be a callable",
            location,
        ):
            return UNKNOWN
        if not isinstance(callback, Lambda):
            return UNKNOWN
        if not self._check_contract(
            len(callback.vars) == 2, "set_fold lambda requires 2 parameters", location
        ):
            return UNKNOWN
        if not valid_set:
            return UNKNOWN
        elements: Type = (
            UNKNOWN
            if isinstance(set_type, UnknownType)
            else _extract_set_info(set_type)[0]
        )
        while True:
            result = self._apply_lambda(
                callback, [accumulator, elements], env, location
            )
            combined = union_types((accumulator, result))
            if (
                isinstance(combined, UnknownType)
                or isinstance(accumulator, UnknownType)
                or combined == accumulator
            ):
                return UNKNOWN
            if any(
                not isinstance(member, ValueType) and member not in accumulator
                for member in combined
            ):
                self._apply_lambda(callback, [UNKNOWN, elements], env, location)
                return UNKNOWN
            accumulator = combined

    def _eval_linear_integer(
        self,
        args: tuple[OperationArg, ...],
        env: dict[VariableRef, Type],
        location: ExpressionLocation,
    ) -> Type:
        """Compute the static type of Operation(Operator.linear_integer, ...)."""
        validated = linear_integer_arguments(args, self._diagnostics, location)
        if validated is None:
            return UNKNOWN
        component_types: list[Type] = []
        for arg in validated:
            if isinstance(arg, tuple):
                coeff, term = arg
                self._eval_expr(arg, env, location.root_id)
                scope = frozenset(env.items())
                c_type = self._result.lookup(coeff, scope=scope)
                x_type = self._result.lookup(term, scope=scope)
                component_types.append(c_type)
                component_types.append(x_type)
            else:
                component_types.append(self._eval_expr(arg, env, location.root_id))

        if not self._check_contract(
            all(
                _is_subset_of_scalars(kind, frozenset({ValueType.integer}))
                for kind in component_types
            ),
            "linear_integer requires integer coefficients, terms, and constant offset",
            location,
        ):
            return UNKNOWN
        if any(isinstance(kind, UnknownType) for kind in component_types):
            return UNKNOWN
        if any(not kind for kind in component_types):
            return frozenset()
        return frozenset({ValueType.integer})

    def _check_contract(
        self, condition: bool, message: str, location: ExpressionLocation
    ) -> bool:
        """Record an error diagnostic when a type contract is violated."""
        if not condition:
            self._diagnostics.error(message, location=location)
        return condition

    def _eval_value_operation(
        self,
        op: Operator,
        args: tuple[OperationArg, ...],
        arg_types: list[Type],
        location: ExpressionLocation,
    ) -> Type:
        """Keep each value operator's contract and inference together before propagation."""
        known: list[frozenset[TypeMember]] = [
            frozenset() if isinstance(kind, UnknownType) else kind for kind in arg_types
        ]
        result: Type = UNKNOWN
        match op:
            case Operator.eq | Operator.neq:
                valid = len(arg_types) == 2
                message = f"{op} expects 2 arguments, got {len(arg_types)}"
                result = frozenset({ValueType.boolean})
            case Operator.get_or_else:
                valid = len(arg_types) == 2
                message = f"{op} expects 2 arguments, got {len(arg_types)}"
                if valid:
                    result = union_types((known[0] - {ValueType.none}, known[1]))
            case Operator.has_value:
                valid = len(arg_types) == 1
                message = f"has_value expects 1 argument, got {len(arg_types)}"
                result = frozenset({ValueType.boolean})
            case Operator.length:
                valid = len(arg_types) == 1 and (
                    isinstance(arg_types[0], UnknownType)
                    or all(
                        member == ValueType.string
                        or isinstance(member, (TupleType, SetOf))
                        for member in arg_types[0]
                    )
                )
                message = "length requires 1 string, tuple, or set argument"
                result = frozenset({ValueType.integer})
            case Operator.if_ | Operator.ite:
                arity = 2 if op == Operator.if_ else 3
                valid = len(arg_types) == arity and _is_subset_of_scalars(
                    arg_types[0], frozenset({ValueType.boolean})
                )
                message = (
                    "if_ requires (boolean, any) arguments"
                    if op == Operator.if_
                    else "ite requires (boolean, any, any) arguments"
                )
                if valid:
                    result = union_types(
                        (
                            known[1],
                            frozenset({ValueType.none})
                            if op == Operator.if_
                            else known[2],
                        )
                    )
            case Operator.cardinality:
                valid = len(arg_types) == 1 and _is_all_sets(arg_types[0])
                message = "cardinality requires 1 set argument"
                result = frozenset({ValueType.integer})
            case Operator.set_make:
                valid = all(_is_all_scalars(kind) for kind in arg_types)
                message = "set_make requires scalar arguments"
                scalars = frozenset(
                    member
                    for kind in known
                    for member in kind
                    if isinstance(member, ValueType)
                )
                result = frozenset({SetOf(scalars, not arg_types)})
            case Operator.set_isin | Operator.set_notin:
                valid = (
                    len(arg_types) == 2
                    and _is_all_scalars(arg_types[0])
                    and _is_all_sets(arg_types[1])
                )
                message = f"{op} requires (scalar, set) arguments"
                result = frozenset({ValueType.boolean})
            case Operator.union | Operator.inter | Operator.diff | Operator.subset:
                valid = len(arg_types) == 2 and all(
                    _is_all_sets(kind) for kind in arg_types
                )
                message = f"{op} requires 2 set arguments"
                if valid:
                    elems_a, empty_a = _extract_set_info(known[0])
                    elems_b, empty_b = _extract_set_info(known[1])
                    match op:
                        case Operator.union:
                            result = frozenset(
                                {SetOf(elems_a | elems_b, empty_a and empty_b)}
                            )
                        case Operator.inter:
                            result = frozenset({SetOf(elems_a | elems_b, True)})
                        case Operator.diff:
                            result = frozenset({SetOf(elems_a, True)})
                        case Operator.subset:
                            result = frozenset({ValueType.boolean})
            case Operator.tuple_get:
                if not self._check_contract(
                    len(arg_types) == 2,
                    f"tuple_get expects 2 arguments, got {len(arg_types)}",
                    location,
                ):
                    return UNKNOWN
                tuple_type, index_type = arg_types
                valid_index = self._check_contract(
                    _is_subset_of_scalars(index_type, frozenset({ValueType.integer})),
                    "tuple_get index must be an integer",
                    location,
                )
                valid_tuple = self._check_contract(
                    isinstance(tuple_type, UnknownType)
                    or all(isinstance(member, TupleType) for member in tuple_type),
                    "tuple_get first argument must be a tuple",
                    location,
                )
                if not valid_index or not valid_tuple:
                    return UNKNOWN
                tuples = [
                    member for member in known[0] if isinstance(member, TupleType)
                ]
                index = args[1]
                if (
                    isinstance(index, ValueDef)
                    and index.value_type == ValueType.integer
                    and isinstance(index.value, int)
                ):
                    if not self._check_contract(
                        all(
                            0 <= index.value < len(member.elements) for member in tuples
                        ),
                        f"tuple_get index {index.value} out of range",
                        location,
                    ):
                        return UNKNOWN
                    result = union_types(
                        member.elements[index.value] for member in tuples
                    )
                else:
                    result = union_types(
                        position for member in tuples for position in member.elements
                    )
                valid, message = True, ""
            case _:
                raise AssertionError(f"Missing static type rule for {op}")
        if not self._check_contract(valid, message, location):
            return UNKNOWN
        if any(isinstance(kind, UnknownType) for kind in arg_types):
            return UNKNOWN
        if any(not kind for kind in known):
            return frozenset()
        return result

    def _eval_scalar_operation(
        self, op: Operator, arg_types: list[Type], location: ExpressionLocation
    ) -> Type:
        """Validate scalar contracts before unknown propagation and combine union members."""
        rule = _SCALAR_RULES[op]
        if not self._check_contract(
            rule.minimum <= len(arg_types) <= rule.maximum
            and all(_is_subset_of_scalars(kind, rule.allowed) for kind in arg_types),
            f"{op} requires {rule.contract}",
            location,
        ):
            return UNKNOWN
        if any(isinstance(kind, UnknownType) for kind in arg_types):
            return UNKNOWN
        known = [kind for kind in arg_types if not isinstance(kind, UnknownType)]
        if any(not kind for kind in known):
            return frozenset()
        match rule.result:
            case ValueType() as scalar:
                return frozenset({scalar})
            case "identity":
                return known[0]
            case "union":
                return union_types(known)
            case "arithmetic":
                return _combine_arithmetic_types(known)
            case "power":
                return (
                    frozenset({ValueType.integer, ValueType.real})
                    if all(ValueType.integer in kind for kind in known)
                    else frozenset({ValueType.real})
                )
        assert_never(rule.result)


def _combine_arithmetic_types(
    known_types: list[frozenset[TypeMember]],
) -> frozenset[TypeMember]:
    """Combine numeric argument types: integer if all integer, else real."""
    has_all_int = all(ValueType.integer in t for t in known_types)
    has_any_real = any(ValueType.real in t for t in known_types)
    result: set[TypeMember] = set()
    if has_all_int:
        result.add(ValueType.integer)
    if has_any_real:
        result.add(ValueType.real)
    return frozenset(result)


def compute_static_types(
    store: ConstraintStore,
    order: EvaluationOrder,
    diagnostics: Diagnostics,
) -> StaticTypeStore:
    """Compute a static type for every variable and expression in the store."""
    return _StaticTypeComputer(store, order, diagnostics).run()
