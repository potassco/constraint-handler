"""Static type computation and representation for variables and expressions."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from itertools import product
from typing import assert_never

from .diagnostics import Diagnostics
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


@dataclass(frozen=True, slots=True)
class UnknownType:
    """Represent an absorbing unknown static type."""


type TypeMember = ValueType | SetOf | TupleType
type Type = frozenset[TypeMember] | UnknownType

_NUMERIC_TYPES: frozenset[ValueType] = frozenset({ValueType.integer, ValueType.real})
_ORDERED_TYPES: frozenset[ValueType] = frozenset(
    {ValueType.boolean, ValueType.integer, ValueType.real}
)
_BOOL_OR_NONE_TYPES: frozenset[ValueType] = frozenset(
    {ValueType.boolean, ValueType.none}
)


class StaticTypeStore(dict[Expr, Type]):
    """Map expressions, including variables, to their precomputed static types."""

    def __init__(
        self, expressions: Mapping[Expr, Type] | Iterable[tuple[Expr, Type]] = ()
    ) -> None:
        """Initialize expression metadata and a separate lambda-context mapping."""
        super().__init__(expressions)
        self.scoped_expressions: dict[
            tuple[Expr, frozenset[tuple[VariableRef, Type]]], Type
        ] = {}

    def lookup(
        self,
        expr: Expr,
        *,
        scope: frozenset[tuple[VariableRef, Type]] = frozenset(),
    ) -> Type:
        """Look up an expression in its explicit lambda binding environment."""
        return self.scoped_expressions[expr, scope] if scope else self[expr]


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


def _extract_set_info(t: Type) -> tuple[frozenset[ValueType], bool]:
    """Extract combined element types and can_be_empty flag from SetOf members."""
    if isinstance(t, UnknownType):
        return frozenset(), True
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
        if var in self._store.set_variables:
            set_var = self._store.set_variables[var]
            elem_types = union_types(
                [
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
            )
            if isinstance(elem_types, UnknownType):
                self._result[var] = UnknownType()
                return
            scalars: set[ValueType] = set()
            for m in elem_types:
                if isinstance(m, ValueType):
                    scalars.add(m)
                else:
                    self._diagnostics.error(
                        f"Set variable {var.name!r} requires scalar elements, got {m}",
                        variable=var,
                    )
            can_be_empty = len(set_var.assigns) == 0
            self._result[var] = frozenset({SetOf(frozenset(scalars), can_be_empty)})
            return

        variable = self._store.variables[var]
        choices_type: Type = (
            union_types(
                self._result[self._store.expressions[c.value]] for c in variable.choices
            )
            if variable.choices
            else frozenset[TypeMember]()
        )
        definition_type = union_types(
            self._result[self._store.expressions[d.value]] for d in variable.definitions
        )
        defaults_type = union_types(
            self._result[self._store.expressions[d.value]] for d in variable.defaults
        )
        self._result[var] = union_types((choices_type, definition_type, defaults_type))

    def _eval_expr(
        self,
        expr: Expr,
        env: dict[VariableRef, Type],
        expr_id: ExprId | None,
    ) -> Type:
        """Retain every visited subexpression's type in its binding context."""
        result = self._compute_expr(expr, env, expr_id)
        if env:
            self._result.scoped_expressions[expr, frozenset(env.items())] = result
        else:
            self._result[expr] = result
        return result

    def _compute_expr(
        self,
        expr: Expr,
        env: dict[VariableRef, Type],
        expr_id: ExprId | None,
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
                item_types = union_types(
                    self._eval_expr(item, env, expr_id) for item in expr
                )
                if isinstance(item_types, UnknownType):
                    return UnknownType()
                if not _is_all_scalars(item_types):
                    self._diagnostics.error(
                        "Set literal elements must be scalar values",
                        expr_id=expr_id,
                    )
                    return UnknownType()
                scalars = frozenset(m for m in item_types if isinstance(m, ValueType))
                return frozenset({SetOf(scalars, False)})
            case tuple():
                elem_types = tuple(self._eval_expr(item, env, expr_id) for item in expr)
                if any(isinstance(t, UnknownType) for t in elem_types):
                    return UnknownType()
                if any(
                    len(t) == 0 for t in elem_types if not isinstance(t, UnknownType)
                ):
                    return frozenset()
                return frozenset({TupleType(elem_types)})
            case Operation(op, args):
                return self._eval_operation(op, args, env, expr_id)
        assert_never(expr)

    def _eval_expr_arg(
        self,
        arg: OperationArg,
        env: dict[VariableRef, Type],
        expr_id: ExprId | None,
    ) -> Type:
        """Evaluate an operation argument that must be an expression."""
        if isinstance(arg, (Lambda, Python)):
            self._diagnostics.error(
                f"Expected value expression argument, got {type(arg).__name__}",
                expr_id=expr_id,
            )
            return UnknownType()
        return self._eval_expr(arg, env, expr_id)

    def _check_contract(
        self,
        condition: bool,
        message: str,
        expr_id: ExprId | None,
    ) -> bool:
        """Record an error diagnostic when a type contract is violated."""
        if not condition:
            self._diagnostics.error(message, expr_id=expr_id)
        return condition

    def _eval_operation(
        self,
        op: Operator,
        args: tuple[OperationArg, ...],
        env: dict[VariableRef, Type],
        expr_id: ExprId | None,
    ) -> Type:
        """Compute the result type of an Operation according to the type table."""
        match op:
            case Operator.python_eval:
                if not args or not isinstance(args[0], Python):
                    self._diagnostics.error(
                        "python_eval requires a Python callable as first argument",
                        expr_id=expr_id,
                    )
                for arg in args[1:]:
                    self._eval_expr_arg(arg, env, expr_id)
                return UnknownType()

            case Operator.set_fold:
                if len(args) != 3:
                    self._diagnostics.error(
                        f"set_fold expects 3 arguments, got {len(args)}",
                        expr_id=expr_id,
                    )
                    return UnknownType()
                callback, set_arg, init_arg = args
                if not isinstance(callback, (Lambda, Python)):
                    self._diagnostics.error(
                        "set_fold first argument must be a callable",
                        expr_id=expr_id,
                    )
                set_type = self._eval_expr_arg(set_arg, env, expr_id)
                self._eval_expr_arg(init_arg, env, expr_id)
                self._check_contract(
                    _is_all_sets(set_type),
                    f"set_fold requires a set argument, got {set_type}",
                    expr_id,
                )
                return UnknownType()

            case Operator.lambda_:
                if not args or not isinstance(args[0], Lambda):
                    self._diagnostics.error(
                        "lambda_ requires a Lambda as first argument",
                        expr_id=expr_id,
                    )
                    return UnknownType()
                lam = args[0]
                call_args = args[1:]
                if len(call_args) != len(lam.vars):
                    self._diagnostics.error(
                        f"Lambda expects {len(lam.vars)} arguments, got {len(call_args)}",
                        expr_id=expr_id,
                    )
                    return UnknownType()
                arg_types = [self._eval_expr_arg(a, env, expr_id) for a in call_args]
                if any(isinstance(t, UnknownType) for t in arg_types):
                    return UnknownType()
                known_arg_types: list[frozenset[TypeMember]] = [
                    t for t in arg_types if not isinstance(t, UnknownType)
                ]
                if any(len(t) == 0 for t in known_arg_types):
                    return frozenset()
                results: list[Type] = []
                for combo in product(*known_arg_types):
                    local_env = dict(env)
                    for param, member_type in zip(lam.vars, combo, strict=True):
                        local_env[param] = frozenset({member_type})
                    results.append(self._eval_expr(lam.expr, local_env, expr_id))
                return union_types(results)

            case Operator.linear_integer:
                return self._eval_linear_integer(args, env, expr_id)

            case _:
                pass

        arg_types = [self._eval_expr_arg(arg, env, expr_id) for arg in args]
        if any(isinstance(t, UnknownType) for t in arg_types):
            return UnknownType()
        known_types: list[frozenset[TypeMember]] = [
            t for t in arg_types if not isinstance(t, UnknownType)
        ]
        if any(len(t) == 0 for t in known_types):
            return frozenset()

        match op:
            case Operator.eq | Operator.neq:
                if not self._check_contract(
                    len(known_types) == 2,
                    f"{op} expects 2 arguments, got {len(known_types)}",
                    expr_id,
                ):
                    return UnknownType()
                return frozenset({ValueType.boolean})

            case Operator.concat:
                if not self._check_contract(
                    len(known_types) == 2
                    and all(
                        _is_subset_of_scalars(t, frozenset({ValueType.string}))
                        for t in known_types
                    ),
                    "concat requires 2 string arguments",
                    expr_id,
                ):
                    return UnknownType()
                return frozenset({ValueType.string})

            case Operator.length:
                if not self._check_contract(
                    len(known_types) == 1
                    and _is_subset_of_scalars(
                        known_types[0], frozenset({ValueType.string})
                    ),
                    "length requires 1 string argument",
                    expr_id,
                ):
                    return UnknownType()
                return frozenset({ValueType.integer})

            case Operator.max | Operator.min:
                if not self._check_contract(
                    len(known_types) >= 1
                    and all(
                        _is_subset_of_scalars(t, _ORDERED_TYPES) for t in known_types
                    ),
                    f"{op} requires at least 1 boolean/integer/real argument",
                    expr_id,
                ):
                    return UnknownType()
                return union_types(known_types)

            case Operator.get_or_else:
                if not self._check_contract(
                    len(known_types) == 2,
                    f"get_or_else expects 2 arguments, got {len(known_types)}",
                    expr_id,
                ):
                    return UnknownType()
                without_none = frozenset(
                    m for m in known_types[0] if m != ValueType.none
                )
                return union_types((without_none, known_types[1]))

            case Operator.if_:
                if not self._check_contract(
                    len(known_types) == 2
                    and _is_subset_of_scalars(
                        known_types[0], frozenset({ValueType.boolean})
                    ),
                    "if_ requires (boolean, any) arguments",
                    expr_id,
                ):
                    return UnknownType()
                return union_types((known_types[1], frozenset({ValueType.none})))

            case Operator.has_value:
                if not self._check_contract(
                    len(known_types) == 1,
                    f"has_value expects 1 argument, got {len(known_types)}",
                    expr_id,
                ):
                    return UnknownType()
                return frozenset({ValueType.boolean})

            case Operator.abs | Operator.minus:
                if not self._check_contract(
                    len(known_types) == 1
                    and _is_subset_of_scalars(known_types[0], _NUMERIC_TYPES),
                    f"{op} requires 1 numeric argument",
                    expr_id,
                ):
                    return UnknownType()
                return known_types[0]

            case (
                Operator.sqrt
                | Operator.cos
                | Operator.sin
                | Operator.tan
                | Operator.acos
                | Operator.asin
                | Operator.atan
            ):
                if not self._check_contract(
                    len(known_types) == 1
                    and _is_subset_of_scalars(known_types[0], _NUMERIC_TYPES),
                    f"{op} requires 1 numeric argument",
                    expr_id,
                ):
                    return UnknownType()
                return frozenset({ValueType.real})

            case Operator.floor | Operator.ceil:
                if not self._check_contract(
                    len(known_types) == 1
                    and _is_subset_of_scalars(known_types[0], _NUMERIC_TYPES),
                    f"{op} requires 1 numeric argument",
                    expr_id,
                ):
                    return UnknownType()
                return frozenset({ValueType.integer})

            case Operator.add | Operator.mult:
                if not self._check_contract(
                    len(known_types) >= 1
                    and all(
                        _is_subset_of_scalars(t, _NUMERIC_TYPES) for t in known_types
                    ),
                    f"{op} requires at least 1 numeric argument",
                    expr_id,
                ):
                    return UnknownType()
                return _combine_arithmetic_types(known_types)

            case Operator.sub | Operator.mod:
                if not self._check_contract(
                    len(known_types) == 2
                    and all(
                        _is_subset_of_scalars(t, _NUMERIC_TYPES) for t in known_types
                    ),
                    f"{op} requires 2 numeric arguments",
                    expr_id,
                ):
                    return UnknownType()
                return _combine_arithmetic_types(known_types)

            case Operator.int_div:
                if not self._check_contract(
                    len(known_types) == 2
                    and all(
                        _is_subset_of_scalars(t, _NUMERIC_TYPES) for t in known_types
                    ),
                    "int_div requires 2 numeric arguments",
                    expr_id,
                ):
                    return UnknownType()
                return frozenset({ValueType.integer})

            case Operator.real_div:
                if not self._check_contract(
                    len(known_types) == 2
                    and all(
                        _is_subset_of_scalars(t, _NUMERIC_TYPES) for t in known_types
                    ),
                    "real_div requires 2 numeric arguments",
                    expr_id,
                ):
                    return UnknownType()
                return frozenset({ValueType.real})

            case Operator.pow:
                if not self._check_contract(
                    len(known_types) == 2
                    and all(
                        _is_subset_of_scalars(t, _NUMERIC_TYPES) for t in known_types
                    ),
                    "pow requires 2 numeric arguments",
                    expr_id,
                ):
                    return UnknownType()
                results_pow: set[TypeMember] = set()
                for b_t, e_t in product(known_types[0], known_types[1]):
                    if b_t == ValueType.integer and e_t == ValueType.integer:
                        results_pow.add(ValueType.integer)
                        results_pow.add(ValueType.real)
                    else:
                        results_pow.add(ValueType.real)
                return frozenset(results_pow)

            case Operator.leq | Operator.lt | Operator.geq | Operator.gt:
                if not self._check_contract(
                    len(known_types) == 2
                    and all(
                        _is_subset_of_scalars(t, _ORDERED_TYPES) for t in known_types
                    ),
                    f"{op} requires 2 ordered arguments",
                    expr_id,
                ):
                    return UnknownType()
                return frozenset({ValueType.boolean})

            case Operator.real_from_int:
                if not self._check_contract(
                    len(known_types) == 1
                    and _is_subset_of_scalars(
                        known_types[0], frozenset({ValueType.integer})
                    ),
                    "real_from_int requires 1 integer argument",
                    expr_id,
                ):
                    return UnknownType()
                return frozenset({ValueType.real})

            case Operator.int_from_real:
                if not self._check_contract(
                    len(known_types) == 1
                    and _is_subset_of_scalars(
                        known_types[0], frozenset({ValueType.real})
                    ),
                    "int_from_real requires 1 real argument",
                    expr_id,
                ):
                    return UnknownType()
                return frozenset({ValueType.integer})

            case Operator.conj | Operator.disj | Operator.lxor | Operator.leqv:
                if not self._check_contract(
                    len(known_types) >= 1
                    and all(
                        _is_subset_of_scalars(t, frozenset({ValueType.boolean}))
                        for t in known_types
                    ),
                    f"{op} requires boolean arguments",
                    expr_id,
                ):
                    return UnknownType()
                return frozenset({ValueType.boolean})

            case Operator.limp:
                if not self._check_contract(
                    len(known_types) == 2
                    and all(
                        _is_subset_of_scalars(t, frozenset({ValueType.boolean}))
                        for t in known_types
                    ),
                    "limp requires 2 boolean arguments",
                    expr_id,
                ):
                    return UnknownType()
                return frozenset({ValueType.boolean})

            case Operator.ite:
                if not self._check_contract(
                    len(known_types) == 3
                    and _is_subset_of_scalars(
                        known_types[0], frozenset({ValueType.boolean})
                    ),
                    "ite requires (boolean, any, any) arguments",
                    expr_id,
                ):
                    return UnknownType()
                return union_types((known_types[1], known_types[2]))

            case Operator.lnot:
                if not self._check_contract(
                    len(known_types) == 1
                    and _is_subset_of_scalars(
                        known_types[0], frozenset({ValueType.boolean})
                    ),
                    "lnot requires 1 boolean argument",
                    expr_id,
                ):
                    return UnknownType()
                return frozenset({ValueType.boolean})

            case Operator.snot | Operator.wnot:
                if not self._check_contract(
                    len(known_types) == 1
                    and _is_subset_of_scalars(known_types[0], _BOOL_OR_NONE_TYPES),
                    f"{op} requires 1 boolean or none argument",
                    expr_id,
                ):
                    return UnknownType()
                return frozenset({ValueType.boolean})

            case Operator.cardinality:
                if not self._check_contract(
                    len(known_types) == 1 and _is_all_sets(known_types[0]),
                    "cardinality requires 1 set argument",
                    expr_id,
                ):
                    return UnknownType()
                return frozenset({ValueType.integer})

            case Operator.set_make:
                if not known_types:
                    return frozenset({SetOf(frozenset(), True)})
                if not self._check_contract(
                    all(_is_all_scalars(t) for t in known_types),
                    "set_make requires scalar arguments",
                    expr_id,
                ):
                    return UnknownType()
                combined = union_types(known_types)
                if isinstance(combined, UnknownType):  # pragma: no cover
                    return UnknownType()
                scalars = frozenset(m for m in combined if isinstance(m, ValueType))
                return frozenset({SetOf(scalars, False)})

            case Operator.set_isin | Operator.set_notin:
                if not self._check_contract(
                    len(known_types) == 2
                    and _is_all_scalars(known_types[0])
                    and _is_all_sets(known_types[1]),
                    f"{op} requires (scalar, set) arguments",
                    expr_id,
                ):
                    return UnknownType()
                return frozenset({ValueType.boolean})

            case Operator.union:
                if not self._check_contract(
                    len(known_types) == 2
                    and _is_all_sets(known_types[0])
                    and _is_all_sets(known_types[1]),
                    "union requires 2 set arguments",
                    expr_id,
                ):
                    return UnknownType()
                elems_a, empty_a = _extract_set_info(known_types[0])
                elems_b, empty_b = _extract_set_info(known_types[1])
                return frozenset({SetOf(elems_a | elems_b, empty_a and empty_b)})

            case Operator.inter:
                if not self._check_contract(
                    len(known_types) == 2
                    and _is_all_sets(known_types[0])
                    and _is_all_sets(known_types[1]),
                    "inter requires 2 set arguments",
                    expr_id,
                ):
                    return UnknownType()
                elems_a, _ = _extract_set_info(known_types[0])
                elems_b, _ = _extract_set_info(known_types[1])
                return frozenset({SetOf(elems_a | elems_b, True)})

            case Operator.diff:
                if not self._check_contract(
                    len(known_types) == 2
                    and _is_all_sets(known_types[0])
                    and _is_all_sets(known_types[1]),
                    "diff requires 2 set arguments",
                    expr_id,
                ):
                    return UnknownType()
                elems_a, _ = _extract_set_info(known_types[0])
                return frozenset({SetOf(elems_a, True)})

            case Operator.subset:
                if not self._check_contract(
                    len(known_types) == 2
                    and _is_all_sets(known_types[0])
                    and _is_all_sets(known_types[1]),
                    "subset requires 2 set arguments",
                    expr_id,
                ):
                    return UnknownType()
                return frozenset({ValueType.boolean})

            case Operator.tuple_get:
                if len(known_types) != 2 or len(args) != 2:
                    self._diagnostics.error(
                        f"tuple_get expects 2 arguments, got {len(args)}",
                        expr_id=expr_id,
                    )
                    return UnknownType()
                tuple_t, idx_t = known_types
                if not _is_subset_of_scalars(idx_t, frozenset({ValueType.integer})):
                    self._diagnostics.error(
                        "tuple_get index must be an integer",
                        expr_id=expr_id,
                    )
                    return UnknownType()
                idx_arg = args[1]
                if not all(isinstance(m, TupleType) for m in tuple_t):
                    self._diagnostics.error(
                        "tuple_get first argument must be a tuple",
                        expr_id=expr_id,
                    )
                    return UnknownType()
                if (
                    isinstance(idx_arg, ValueDef)
                    and idx_arg.value_type == ValueType.integer
                    and isinstance(idx_arg.value, int)
                ):
                    idx_val = idx_arg.value
                    projected: list[Type] = []
                    for m in tuple_t:
                        if isinstance(m, TupleType):
                            if 0 <= idx_val < len(m.elements):
                                projected.append(m.elements[idx_val])
                            else:
                                self._diagnostics.error(
                                    f"tuple_get index {idx_val} out of range",
                                    expr_id=expr_id,
                                )
                                return UnknownType()
                    return union_types(projected)
                all_pos: list[Type] = []
                for m in tuple_t:
                    if isinstance(m, TupleType):
                        all_pos.extend(m.elements)
                return union_types(all_pos)

        assert_never(op)

    def _eval_linear_integer(
        self,
        args: tuple[OperationArg, ...],
        env: dict[VariableRef, Type],
        expr_id: ExprId | None,
    ) -> Type:
        """Compute the static type of Operation(Operator.linear_integer, ...)."""
        if not args:
            self._diagnostics.error(
                "linear_integer requires at least one argument", expr_id=expr_id
            )
            return UnknownType()
        component_types: list[Type] = []
        for idx, arg in enumerate(args):
            if isinstance(arg, tuple) and len(arg) == 2:
                coeff, term = arg
                if (
                    not isinstance(coeff, ValueDef)
                    or coeff.value_type != ValueType.integer
                ):
                    self._diagnostics.error(
                        "linear_integer coefficient must be a constant integer literal",
                        expr_id=expr_id,
                    )
                    return UnknownType()
                self._eval_expr(arg, env, expr_id)
                scope = frozenset(env.items())
                c_type = self._result.lookup(coeff, scope=scope)
                x_type = self._result.lookup(term, scope=scope)
                component_types.append(c_type)
                component_types.append(x_type)
            elif idx == len(args) - 1 and not isinstance(arg, (Lambda, Python, tuple)):
                if not isinstance(arg, ValueDef) or arg.value_type != ValueType.integer:
                    self._diagnostics.error(
                        "linear_integer constant offset must be a constant integer literal",
                        expr_id=expr_id,
                    )
                    return UnknownType()
                component_types.append(self._eval_expr(arg, env, expr_id))
            else:
                self._diagnostics.error(
                    f"Invalid linear_integer argument at position {idx}: {arg}",
                    expr_id=expr_id,
                )
                return UnknownType()

        if any(isinstance(t, UnknownType) for t in component_types):
            return UnknownType()
        known = [t for t in component_types if not isinstance(t, UnknownType)]
        if any(len(t) == 0 for t in known):
            return frozenset()
        if not self._check_contract(
            all(
                _is_subset_of_scalars(t, frozenset({ValueType.integer})) for t in known
            ),
            "linear_integer requires integer coefficients, terms, and constant offset",
            expr_id,
        ):
            return UnknownType()
        return frozenset({ValueType.integer})


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
